import sys
import pickle
import random
import sympy
import subprocess
import os
import os.path
import time

weights = {}
weight_sum = {}
lpmlncompiler = 'code/lpmlncompiler'
clingo3to4 = 'code/clingo3to4'
SMSample_script = 'code/xorro/xorro.py '
#SMSample_script = 'code/clingoXOR-Count.py '
#SMSample_script = 'code/XOR-countncheck.py '
#SMSample_script = 'code/XOR-countncheck-faster.py '
tmp_sat_const_file = 'sat_const.lp'
tmp_weights_file = 'tmp_weight.obj'
tmp_lpmln2cl_file = 'out.txt'
negConvProgram = 'code/negconv'
tmp_aspprog = 'asp_out.txt'
tmp_posprog = 'tmp_posprog.lpmln'
lr = 0.1
numExecutionXorCount = 10
max_iteration = 50
max_mcsat_iteration = 50
stopping_diff = 0.001
init_weight = -1
numUnsat = {}
mis = {}
total_mis = {}
log_file_name = 'log.txt'

class gringoFun:
	def __init__(self, atom_name, atom_args):
		self.name = atom_name
		self.args = atom_args

	def __str__(self):
		return self.name + '(' + ','.join([str(x) for x in self.args]) + ')'

	def __repr__(self):
		return self.name + '(' + ','.join([str(x) for x in self.args]) + ')'

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			if self.name != other.name:
				return False
			for i in range(len(self.args)):
				if i > len(other.args) - 1 or self.args[i] != other.args[i]:
					return False
			return True
		return False

	def __hash__(self):
		return hash(str(self))

def updateWithWeightPlaceHolders(program, out, rule_idx):
	global weights
	clingo_ipt = open(program, 'r')
	buffer = []
	for line in clingo_ipt:
		if line.startswith('@getWeight('):
			idx = line.split(' ')[0].split('(')[1].split(')')[0]
			buffer.append(str(weights[int(idx)]) + ' ' + ''.join(line.split(' ')[1:]))
		else:
			buffer.append(line)

	clingo_ipt.close()
	clingo_opt = open(out, 'w')
	for line in buffer:
		clingo_opt.write(line)
	clingo_opt.close()

def getSampleFromText(txt):
	#print txt
	whole_model = []
	if 'UNSATISFIABLE' in txt or "UNKNOWN" in txt:
		return None
	answers = txt.split('Answer: 1')[1]
	answers = answers.split('Optimization:')[0]
	answers = answers.split('SATISFIABLE')[0]
	answers = answers.lstrip(' ').lstrip('\n').lstrip('\r')
	atoms = answers.split(' ')
	for atom in atoms:
		atom_name = atom.split('(')[0]
		if len(atom.split('(')) > 1:
			args = atom.split('(')[1].replace('\r', '').replace('\n', '').rstrip(')')
		else:
			args = ''
		whole_model.append(gringoFun(atom_name, [eval(arg) for arg in args.split(',')]))
	#print whole_model
	return whole_model

def findUnsatRules(atoms):
	M = []
	for atom in atoms:
		#print 'atom', atom
		if atom.name.startswith('unsat'):
			weight = float(atom.args[1])
			r = random.random()
			#print 'r', r
			#print 'weight', weight
			#print '1 - sympy.exp(weight)', 1.0 - sympy.exp(weight)
			if r < 1.0 - sympy.exp(weight):
				M.append(atom)
	#print M
	return M

def countUnsatAtom(atoms, rule_idx):
	lmis = {}
	for rule_id in rule_idx:
		lmis[rule_id] = 0
	for atom in atoms:
		if atom.name.startswith('unsat'):
			idx = atom.args[0]
			if idx in weights:
				lmis[idx] += 1
	return lmis

def create_constraint_file(M, filename):
	sat_const = open(filename, 'w')
	for m in M:
		argsStr = ''
		for arg in m.args:
			if type(arg) == str:
				argsStr += ('"' + arg + '"' + ',')
			else:
				argsStr += (str(arg) + ',')
		argsStr = argsStr.rstrip(',')
		sat_const.write(':- not ' + m.name + '(' + argsStr + ').\n')
	sat_const.close()

def executeCmd(cmd):
	try:
		out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
	except Exception, e:
		out = str(e.output)
	return out

def findTotalMisWithMCSAT(total_mis, program):
	global max_mcsat_iteration
	## Generate first sample
	out = executeCmd('clingo ' + program + ' 1')
	print out
	#print out
	sample = getSampleFromText(out)
	mis = countUnsatAtom(sample, rule_idx)
	M = findUnsatRules(sample)

	sample_count = 0
	for _ in range(max_mcsat_iteration):
		sample_count += 1
		print 'Sample ', sample_count, sample
		print 'M', M
		for idx in weights:
			total_mis[idx] += mis[idx]

		create_constraint_file(M, tmp_sat_const_file)

		# Generate next sample
		cmd = 'python ' + SMSample_script +  ' ' + program + ' ' + tmp_sat_const_file + ' 1'
		out = ''
		print 'command:', cmd
		for _ in range(numExecutionXorCount):
			out = executeCmd(cmd)
			if 'Answer: 1' in out:
				break
		# Extract sample from output
		#print out
		tmp_sample = getSampleFromText(out)
		if tmp_sample != None:
			sample = tmp_sample
		else:
			print 'Could not find stable models. Using current sample as next sample.'

		# Find rules that are not satisfied
		M = findUnsatRules(sample)
		mis = countUnsatAtom(sample, rule_idx)
	return total_mis, sample_count
	
program = sys.argv[1]
evidence = sys.argv[2]

print 'program template:', program
print 'evidence:', evidence
print '\n'

raw_rule_idx = raw_input('Rule indices? (Separate with Comma) ')
rule_idx = []
if '..' in raw_rule_idx:
	start_idx = int(raw_rule_idx.split('..')[0])
	end_idx = int(raw_rule_idx.split('..')[1])
	for i in range(start_idx, end_idx + 1):
		rule_idx.append(i)
else:
	rule_idx = [int(x) for x in raw_rule_idx.split(',')]

for idx in rule_idx:
	weights[idx] = init_weight
	weight_sum[idx] = 0

random.seed()
for fn in [tmp_weights_file, tmp_sat_const_file, tmp_posprog, tmp_aspprog, tmp_lpmln2cl_file, tmp_lpmln2cl_file + '.cl', log_file_name]:
	if os.path.isfile(fn):
		os.remove(fn)

log_file = open(log_file_name, 'w')
pickle.dump(weights, open(tmp_weights_file, 'w'))
# Prepare input program
updateWithWeightPlaceHolders(program, program + '.weights', rule_idx)
executeCmd(lpmlncompiler + ' ' + program + '.weights > ' + tmp_lpmln2cl_file)
executeCmd(clingo3to4 + ' ' + tmp_lpmln2cl_file)
# End: Modify input program with weight placeholders
out = executeCmd('clingo ' + tmp_lpmln2cl_file + '.cl ' + evidence)
if 'UNSATISFIABLE' in out:
	print 'Evidence and program not satisfiable. Exit.'
	sys.exit()
#for idx in rule_idx:
#	numUnsat[idx] = numUnsat[idx] / sample_count
#print 'Number of false instances in Evidence:', numUnsat

# Begin: Learning Iterations
actualNumIteration = 0
start_time = time.time()
for iter_count in range(max_iteration):
	actualNumIteration += 1
	print '============ Iteration ' + str(iter_count) + ' ============'
	prev_weights = pickle.load(open(tmp_weights_file, 'r'))
	# Begin: Single learning iteration
	updateWithWeightPlaceHolders(program, program + '.weights', rule_idx)

	# Eliminate positive weights from program
	executeCmd(negConvProgram + ' ' + program + '.weights' + ' > ' + tmp_posprog)

	# Executing MC-SAT on the program with positive weight eliminated
	executeCmd(lpmlncompiler + ' ' + tmp_posprog + ' > ' + tmp_aspprog)
	executeCmd(clingo3to4 + ' ' + tmp_aspprog)
	print 'tmp_aspprog:'
	for line in open(tmp_aspprog + '.cl', 'r'):
		print line
	print 'tmp_aspprog_end'
	
	for idx in weights:
		numUnsat[idx] = 0.0
		total_mis[idx] = 0

	numUnsat, sample_count1 = findTotalMisWithMCSAT(numUnsat, tmp_aspprog + '.cl ' + evidence)
	total_mis, sample_count2 = findTotalMisWithMCSAT(total_mis, tmp_aspprog + '.cl')
	
	# End: Single learning iteration
	# Compute new weights
	total_gradient = 0
	for idx in weights:
		print 'Rule', idx
		print '# False ground instances from Evidence', float(numUnsat[idx])/float(sample_count1)
		print 'Expected # false ground instances', float(total_mis[idx])/float(sample_count2)
		prob_gradient = -numUnsat[idx]/sample_count1 + float(total_mis[idx])/float(sample_count2)
		print 'Gradient', prob_gradient
		total_gradient += abs(prob_gradient)
		weights[idx] += lr * prob_gradient
		print 'New weight ', idx, ':', weights[idx]

	pickle.dump(weights, open(tmp_weights_file, 'w'))
# End: Learning Iterations
	print "New weights:"
	max_diff = abs(weights[weights.keys()[0]] - prev_weights[weights.keys()[0]])
	for rule_id in rule_idx:
		print "Rule " + str(rule_id) + ": ", weights[rule_id]
		weight_sum[rule_id] += weights[rule_id]
		if abs(weights[rule_id] - prev_weights[rule_id]) > max_diff:
			max_diff = abs(weights[rule_id] - prev_weights[rule_id])

	print "max_diff", max_diff
	if actualNumIteration % 10 == 0:
		log_file.write(str(actualNumIteration) + ',' + str(max_diff) + ',' + str(total_gradient) + ',' + str(time.time() - start_time) + '\n')
	if max_diff <= stopping_diff:
		break

# Begin: Store and save new weights
outfile = open('weights.out.txt', 'w')
print 'Averaged Weights:'
for rule_id in rule_idx:
	print "Rule " + str(rule_id) + ": ", weight_sum[rule_id]/actualNumIteration
	outfile.write(str(rule_id) + ':' + str(weight_sum[rule_id]/actualNumIteration))
os.remove(tmp_weights_file)
# End: Store and save new weights
log_file.close()

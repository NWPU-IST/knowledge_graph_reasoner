import math
import copy
import pickle
import copy
import random
import sympy
import sys
import subprocess
import ast


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


numExecutionXorCount = 10
max_num_iteration = 100
tmp_sat_const_file = 'sat_const.lp'
SMSample_script = 'lpmln-learn/code/XOR-countncheck.py'
# SMSample_script = 'code/clingoXOR-Count.py'

#program_filename = 'out.txt'

curr_sample = None
sample_attempt = None
whole_model = []
queries = []
query_count = {}
domain = []
atoms2count = []
M = []


def getSampleFromText(txt):
	global whole_model
	if 'UNSATISFIABLE' in txt:
		return False

	whole_model = []
	answers = txt.split('Answer: 1')[1]
	answers = answers.split('Optimization:')[0]
	answers = answers.lstrip(' ').lstrip('\n').lstrip('\r')
	atoms = answers.split(' ')
	for atom in atoms:
		print str(atom), "---"
		atom_name = atom.split('(')[0]
		print atom_name
		args = atom.split('(')[1].replace('\r', '').replace('\n', '').rstrip(')')
		print args
		whole_model.append(gringoFun(atom_name, [eval(arg) for arg in args.split(',')]))
	#print whole_model
	return True


def findUnsatRules(atoms):
	global M
	M = []
	for atom in atoms:
		if atom.name.startswith('unsat'):
			weight = float(atom.args[1])
			# print 'weight', weight
			r = random.random()
			if r < 1 - sympy.exp(weight):
				M.append(atom)


def processSample(atoms):
	global domain
	global w
	global atoms2count
	global sample_attempt
	global atoms2count
	atoms2count = []
	sample_attempt = []
	# Find rules that are not satisfied
	findUnsatRules(atoms)

	# Do specific things with the sample: counting atom occurence
	for r in domain:
		if r in atoms:
			sample_attempt.append((r, True))
			if r in query_count:
				atoms2count.append(r)
				# print r, ' is satisfied'
		else:
			sample_attempt.append((r, False))


def read_input():
	with open('lpmln-learning/code/query_domain.txt') as f:
		content = f.readlines()
	queries = content[0].split(',')
	queries = [query.rstrip() for query in queries]
	print queries
	domain_filename = content[2]
	resource = ast.literal_eval(content[1])
	resource = ['"'+res+'"' for res in resource]
	return queries, domain_filename, resource


# Main
program_filename = sys.argv[1]

# program_filename = '../../out.txt'
#
# queries = sys.argv[2].split(',')
# domain_filename = sys.argv[3]

queries, domain_filename, resource = read_input()

print queries, domain_filename, resource, program_filename
domain_file = open(domain_filename, 'r')

for line in domain_file:
	if len(line) <= 2:
		continue
	parts = line.split('~')
	instances = parts[1].split('&')
	for inst in instances:
		domain.append(gringoFun(parts[0], [eval(arg) for arg in inst.split(';')]))
	if parts[0] in queries:
		for inst in instances:
			query_count[gringoFun(parts[0], [eval(arg) for arg in inst.split(';')])] = 0

print 'domain', domain
print 'query atoms', query_count.keys()

iter_count = 0
random.seed()

sample_count = 0

# Generate First Sampling
whole_model = None
#prg.conf.solve.models = 1
#prg.ground([('base', [])])
#prg.solve([], getSample)
cmd = 'clingo ' + program_filename + ' 1'
try:
	out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
except Exception, e:
	out = str(e.output)

if getSampleFromText(out):
	processSample(whole_model)
else:
	print 'Input program is unsatisfiable. Exit.'
	sys.exit()

for _ in range(max_num_iteration):
	sample_count += 1
	curr_sample = sample_attempt
	# print 'Sample ', sample_count, curr_sample
	# print 'M', M
	for atom in atoms2count:
		query_count[atom] += 1
	# Create file with satisfaction constraints
	sat_const = open(tmp_sat_const_file, 'w')
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

	# Generate next sample
	cmd = 'clingo5 ' + SMSample_script +  ' -c s=0 ' + program_filename + ' ' + tmp_sat_const_file + ' 1'
	out = ''
	for _ in range(numExecutionXorCount):
		try:
			out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
		except Exception, e:
			out = str(e.output)
		#print out
		if 'Answer: 1' in out:
			break
	# Extract sample from output
	# print out
	if getSampleFromText(out):
		processSample(whole_model)
	else:
		processSample(whole_model)
		print 'Could not find stable models. Using current sample as next sample.'


def get_label(compare_prob):
    if None not in compare_prob:
        if compare_prob[0] > compare_prob[1]:
            label = -1
        elif compare_prob[0] < compare_prob[1]:
            label = 1
        elif compare_prob[0] == compare_prob[1] and compare_prob[0] == 0.0:
            label = 0
        else:
            label = 'equal'
    else:
        label = 'None'
    return label


# Compute new marginal probabilities
for atom in query_count:
	# print atom, ": ", float(query_count[atom])/float(sample_count)
	try:
		atom_str = str(atom).encode('utf-8')
		entities = re.findall(r'\".*?\"', atom_str)
		if resource[0] == entities[0] and resource[1] == entities[1]:
			prob = float(query_count[atom]) / float(sample_count)
			print atom, ": ", prob
			if 'neg' in atom_str:
				compare_prob[0] = prob
			else:
				compare_prob[1] = prob
			output.append(str(atom) + ": " + str(round(prob, 2)))
	except:
		pass

label = get_label(compare_prob)
with open('lpmln-learning/code/lpmln_prob_mc.txt', 'w') as the_file:
	the_file.write(str(output).encode('utf-8'))
	the_file.write(';' + str(label))



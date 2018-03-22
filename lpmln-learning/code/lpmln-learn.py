import subprocess
import pickle
import sys
import os
import math

max_learning_iteration = 100
max_mcsat_iteration = 100
stopping_diff = 0.005
init_weight = 1
weight_sum = {}
weights = {}
tmp_weights_file = 'tmp_weight.obj'
tmp_evidence_file = 'tmp_evidence.obj'
tmp_lr_file = 'tmp_lr.obj'
learning_alg = 'code/learn-pseudolikelihood.py'
#learning_alg = 'code/learn-mhsampling.py'
#learning_alg = 'code/learn-gibbssampling.py'
tmp_lpmln2cl_file = 'out.txt'
lr = 1
lr_decay_rate = 0.5
lr_decay_steps = 100

def updateWithWeightPlaceHolders(program, rule_idx):
	clingo_ipt = open(program, 'r')
	buffer = []
	for line in clingo_ipt:
		parts = line.split(' ')
		for part in parts:
			if part.startswith('unsat('):
				idx = part.split('unsat(')[1].split(',')[0]
				weight = part.split('unsat(')[1].split('"')[1]
				if int(idx) in rule_idx:
					buffer.append('unsat('+str(idx)+',@getWeight(' + idx + ')' + part.split('"' + weight + '"')[1])
				else:
					buffer.append(part)
			elif part.startswith(':~unsat('):
				idx = part.split(':~unsat(')[1].split(',')[0]
				weight = part.split(':~unsat(')[1].split('"')[1]
				if int(idx) in rule_idx:
					buffer.append(':~unsat('+str(idx)+',@getWeight(' + idx + ')' + part.split('"' + weight + '"')[1])
				else:
					buffer.append(part)
			else:
				buffer.append(part)

			buffer.append(' ')
		buffer.append('\n')
	clingo_ipt.close()
	os.remove(program)
	clingo_opt = open(program, 'w')
	for line in buffer:
		clingo_opt.write(line)
	clingo_opt.close()

# Get arguments
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
pickle.dump(weights, open(tmp_weights_file, 'w'))
pickle.dump(lr, open(tmp_lr_file, 'w'))

# Modify input program with weight placeholders
cmd = 'lpmln2cl ' + program
try:
	out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
except Exception, e:
	out = str(e.output)
print out

updateWithWeightPlaceHolders(tmp_lpmln2cl_file, rule_idx)

# Build Evidence Object
evid_file = open(evidence, 'r')
evidence_obj = []
for line in evid_file:
	if len(line) <= 2:
		continue
	parts = line.split(' ')
	evidence_obj.append((parts[0], [eval(arg) for arg in parts[1].split(';')], bool(int(parts[2]))))
pickle.dump(evidence_obj, open(tmp_evidence_file, 'w'))

actualNumIteration = 0
# Learning Iterations
for iter_count in range(max_learning_iteration):
	actualNumIteration += 1
	print '============ Iteration ' + str(iter_count) + ' ============'
	prev_weights = pickle.load(open(tmp_weights_file, 'r'))

	# Execute one iteration of learning algorithm
	cmd = 'clingo ' + tmp_lpmln2cl_file + ' ' + learning_alg + ' --quiet=2'
	try:
		out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
	except Exception, e:
		out = str(e.output)
	print out

	# Print out new weights
	weights = pickle.load(open(tmp_weights_file, 'r'))
	print "New weights:"
	max_diff = abs(weights[weights.keys()[0]] - prev_weights[weights.keys()[0]])
	for rule_id in rule_idx:
		print "Rule " + str(rule_id) + ": ", weights[rule_id]
		weight_sum[rule_id] += weights[rule_id]
		if abs(weights[rule_id] - prev_weights[rule_id]) > max_diff:
			max_diff = abs(weights[rule_id] - prev_weights[rule_id])

	print "max_diff", max_diff

	if max_diff <= stopping_diff:
		break

	lr = lr * math.pow(lr_decay_rate, float(actualNumIteration/lr_decay_steps))
	pickle.dump(lr, open(tmp_lr_file, 'w'))

outfile = open('weights.out.txt', 'w')
print 'Averaged Weights:'
for rule_id in rule_idx:
	print "Rule " + str(rule_id) + ": ", weight_sum[rule_id]/actualNumIteration
	outfile.write(str(rule_id) + ':' + str(weight_sum[rule_id]/actualNumIteration))
os.remove(tmp_weights_file)
os.remove(tmp_evidence_file)

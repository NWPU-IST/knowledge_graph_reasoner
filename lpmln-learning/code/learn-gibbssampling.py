#script (python)
import gringo
import math
import copy
from gringo import Model
import pickle
import copy
import random
import sympy

mis = {}
numUnsat = {}
w = 0
lr = 1
init_weight = 1
tmp_weights_file = 'tmp_weight.obj'
tmp_evidence_file = 'tmp_evidence.obj'
tmp_lr_file = 'tmp_lr.obj'
curr_sample = None
sample_attempt = None
max_num_iteration = 1000
isStableModelVar = False
evidenceIsStableModel = False

weights = pickle.load(open(tmp_weights_file, 'r'))
evid_obj = pickle.load(open(tmp_evidence_file, 'r'))
lr = pickle.load(open(tmp_lr_file, 'r'))

#weights = {}
#weights[1] = 1
#evidence = [(gringo.Fun('q', [1]), True), (gringo.Fun('p', [1]), False)]
evidence = []
for r in evid_obj:
	evidence.append((gringo.Fun(r[0], r[1]), r[2]))

def getWeight(rule_id):
	global weights
	print str(weights[rule_id])
	return str(weights[rule_id])

def main(prg):
	global mis
	global w
	global weights
	global curr_sample
	global max_num_iteration
	global numUnsat
	global isStableModelVar
	global sample_attempt
	global lr

	iter_count = 0
	random.seed()

	for idx in weights:
		mis[idx] = 0

	print "Solving for M_i....."
	prg.ground([('base', [])])
	prg.solve(evidence, solveWithEvidence)
	if not evidenceIsStableModel:
		print "No stable model satisfies evidence. Exit..."
		sys.exit()
	print "---------------------"

	sample_count = 1
	total_mis = {}
	for idx in weights:
		total_mis[idx] = 0

	# Generate First Sample by MAP inference
	prg.solve([], getSample)
	curr_sample = sample_attempt

	# Main Loop
	for _ in range(max_num_iteration):
		curr_weight = w
		for idx in weights:
			total_mis[idx] += numUnsat[idx]
		print 'Sample ',sample_count,': ',curr_sample
		print 'Weight: ' + str(w)
		print "Number of False Instances: "
		for idx in numUnsat:
			print 'Rule ' + str(idx) + ': ' + str(numUnsat[idx])

		# Generate next sample by sampling each atom
		for i in range(len(evidence)):
			atom, val = evidence[i]
			evidence[i] = (atom, True)
			w = 0
			prg.solve(evidence, getSample)
			wt = w
			evidence[i] = (atom, False)
			w = 0
			prg.solve(evidence, getSample)
			wf = w
			r = random.random()
			if float(wt+wf) == 0 or r < float(wt)/float(wt+wf):
				evidence[i] = (atom, True)
			else:
				evidence[i] = (atom, False)

		sample_count += 1
		prg.solve(evidence, getSample)

	# Compute new weights
	for idx in weights:
		print weights
		print lr
		print mis[idx]
		print total_mis[idx]
		print sample_count
		prob_gradient = -mis[idx] + float(total_mis[idx])/float(sample_count)
		weights[idx] += lr * prob_gradient
		print 'New weight ', idx, ':', weights[idx]

	pickle.dump(weights, open(tmp_weights_file, 'w'))

def getSample(model):
	global sample_attempt
	global w
	global numUnsat
	global isStableModelVar
	isStableModelVar = True
	sample_attempt = []
	for r in evidence:
		if model.contains(r[0]):
			sample_attempt.append((r[0], True))
		else:
			sample_attempt.append((r[0], False))
	w = computeWeight(model)
	numUnsat = computeMis(model)


def computeWeight(model):
	penalty = 0
	for atom in model.atoms(Model.ATOMS):
		if atom.name().startswith('unsat'):
			weight = float(atom.args()[1])
			penalty += weight
	return sympy.exp(-penalty)

def computeMis(model):
	global mis
	lmis = {}
	for idx in mis:
		lmis[idx] = 0
	for atom in model.atoms(Model.ATOMS):
		if atom.name().startswith('unsat'):
			idx = atom.args()[0]
			if idx in lmis:
				lmis[idx] += 1
	return lmis

def solveWithToggledEvidence(model):
	global p_mis
	global w
	p_mis = computeMis(model)
	for idx in p_mis:
		print 'False ground instance of rule ' + str(idx) + ': ' + str(p_mis[idx])
	w = computeWeight(model)
	print 'Weight: ', w

def solveWithEvidence(model):
	global mis
	global evidenceIsStableModel
	evidenceIsStableModel = True
	mis = computeMis(model)
	for idx in mis:
		print 'False ground instance of rule ' + str(idx) + ': ' + str(mis[idx])
	print 'Weight: ', computeWeight(model)

#end.

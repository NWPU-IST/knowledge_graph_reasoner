#script (python)
import gringo
import math
import copy
from gringo import Model
import pickle
import copy
import random
import sympy

w = 0
curr_sample = None
sample_attempt = None
max_num_iteration = 5
isStableModelVar = False
queries = []
query_count = {}
domain = []
atoms2count = []

def main(prg):
	global w
	global curr_sample
	global max_num_iteration
	global isStableModelVar
	global sample_attempt
	global query_count
	global queries
	global domain
	global atoms2count

	queries = raw_input('Queries?(Separated with Comma; No space) ').split(',')
	domain_filename = raw_input('Domain File? ')
	domain_file = open(domain_filename, 'r')
	for line in domain_file:
		if len(line) <= 2:
			continue
		parts = line.split('~')
		instances = parts[1].split('&')
		for inst in instances:
			domain.append(gringo.Fun(parts[0], [eval(arg) for arg in inst.split(';')]))
		if parts[0] in queries:
			for inst in instances:
				query_count[gringo.Fun(parts[0], [eval(arg) for arg in inst.split(';')])] = 0

	print 'domain', domain
	print 'query atoms', query_count.keys()

	iter_count = 0
	random.seed()

	sample_count = 1

	# Generate First Sampling by MAP inference
	prg.ground([('base', [])])
	prg.solve([], getSample)
	curr_sample = sample_attempt

	# Main Loop
	for _ in range(max_num_iteration):
		curr_weight = w
		print 'Sample ',sample_count,': ',curr_sample
	 	print 'Weight: ' + str(w)
	 	print "Query Count: ", query_count
		for atom in atoms2count:
			query_count[atom] += 1

		# Generate next sample by randomly flipping atoms
		while True:
			sample_attempt = []
			for r in curr_sample:
				sample_attempt.append(r)
			ridx = random.randint(0, len(sample_attempt)-1)
			sample_attempt[ridx] = (sample_attempt[ridx][0], not sample_attempt[ridx][1])
			isStableModelVar = False
			prg.solve(sample_attempt, getSample)
			if isStableModelVar:
				new_weight = w
				r = random.random()
				if r < new_weight / curr_weight:
					curr_sample = sample_attempt
				else:
					sample_attempt = curr_sample
					prg.solve(sample_attempt, getSample)
				sample_count += 1
				break

	# Compute new marginal probabilities
	for atom in query_count:
		print atom, ": ", float(query_count[atom])/float(sample_count)

def getSample(model):
	global sample_attempt
	global w
	global isStableModelVar
	global atoms2count
	global domain
	atoms2count = []
	isStableModelVar = True
	sample_attempt = []
	for r in domain:
		if model.contains(r):
			sample_attempt.append((r, True))
			if r in query_count:
				atoms2count.append(r)
				print r, ' is satisfied'
		else:
			sample_attempt.append((r, False))
	w = computeWeight(model)

def computeWeight(model):
	penalty = 0
	for atom in model.atoms(Model.ATOMS):
		if atom.name().startswith('unsat'):
			weight = float(atom.args()[1])
			penalty += weight
	return sympy.exp(-penalty)
#
# def computeMis(model):
# 	global mis
# 	lmis = {}
# 	for idx in mis:
# 		lmis[idx] = 0
# 	for atom in model.atoms(Model.ATOMS):
# 		if atom.name().startswith('unsat'):
# 			idx = atom.args()[0]
# 			if idx in lmis:
# 				lmis[idx] += 1
# 	return lmis
#
# def solveWithToggledEvidence(model):
# 	global p_mis
# 	global w
# 	p_mis = computeMis(model)
# 	for idx in p_mis:
# 		print 'False ground instance of rule ' + str(idx) + ': ' + str(p_mis[idx])
# 	w = computeWeight(model)
# 	print 'Weight: ', w


#end.

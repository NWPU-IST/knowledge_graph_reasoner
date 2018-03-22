#script (python)
import gringo
import math
import copy
from gringo import Model
import pickle
import sys
import sympy

mis = {}
p_mis = {}
w = 0
pseudo_likelihood = {}
lr = 0.5
init_weight = 1
tmp_weights_file = 'tmp_weight.obj'
tmp_evidence_file = 'tmp_evidence.obj'

evidenceIsStableModel = False

weights = pickle.load(open(tmp_weights_file, 'r'))
evid_obj = pickle.load(open(tmp_evidence_file, 'r'))
evidence = []
for r in evid_obj:
	evidence.append((gringo.Fun(r[0], r[1]), r[2]))

def getWeight(rule_id):
	global weights
	print str(weights[rule_id])
	return str(weights[rule_id])

def main(prg):
	global mis
	global p_mis
	global w
	global pseudo_likelihood
	global weights
	global stopping_diff

	for idx in weights:
		mis[idx] = 0

	print "Solving for M_i....."
	prg.ground([('base', [])])
	prg.solve(evidence, solveWithEvidence)
	if not evidenceIsStableModel:
		print "No stable model satisfies evidence. Exit..."
		sys.exit()
	print "---------------------"
	for idx in weights:
		pseudo_likelihood[idx] = 0
	for i in range(len(evidence)):
		atom, truth = evidence[i]
		print "Solving for M_i[" + atom.name() + "(" + str(atom.args()) + ")=True]..."
		evidence[i] = (atom, True)
		w = 0
		prg.solve(evidence, solveWithToggledEvidence)
		p_mis_t = p_mis
		w_t = w
		print "Solving for M_i[" + atom.name() + "(" + str(atom.args()) + ")=False]..."
		evidence[i] = (atom, False)
		w = 0
		prg.solve(evidence, solveWithToggledEvidence)
		evidence[i] = (atom, truth)
		p_mis_f = p_mis
		w_f = w
		print 'w_t', w_t
		print 'w_f', w_f
		print '----------------------'
		for idx in weights:
			if w_t + w_f == 0:
				rwt = 0
				rwf = 0
			else:
				rwt = w_t/(w_t + w_f)
				rwf = w_f/(w_t + w_f)
			print 'mis[idx]', mis[idx]
			print 'w_t /(w_t + w_f)', rwt
			print 'w_f/ (w_t + w_f)', rwf
			if idx in p_mis_t:
				print 'p_mis_t[idx]', p_mis_t[idx]
			else:
				print 'p_mis_t[idx]', 'None'
				p_mis_t[idx] = 0
			if idx in p_mis_f:
				print 'p_mis_f[idx]', p_mis_f[idx]
			else:
				print 'p_mis_f[idx]', 'None'
				p_mis_f[idx] = 0
			pseudo_likelihood[idx] += (-mis[idx] + rwt * p_mis_t[idx] + rwf * p_mis_f[idx])

	for idx in weights:
		print 'Deravative of Pseudo-likelihood w.r.t. rule ', idx, ':', pseudo_likelihood[idx]

	updateWeights()

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
	global evidenceIsStableModel
	global mis
	evidenceIsStableModel = True
	mis = computeMis(model)
	for idx in mis:
		print 'False ground instance of rule ' + str(idx) + ': ' + str(mis[idx])
	print 'Weight: ', computeWeight(model)

def updateWeights():
	global weights
	global lr
	global pseudo_likelihood
	for idx in weights:
		weights[idx] += lr * pseudo_likelihood[idx]
	pickle.dump(weights, open(tmp_weights_file, 'w'))

#end.

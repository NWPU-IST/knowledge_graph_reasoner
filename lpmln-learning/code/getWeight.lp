#script (python)
import pickle

tmp_weights_file = 'tmp_weight.obj'
weights = pickle.load(open(tmp_weights_file, 'r'))

def getWeight(rule_id):
	global weights
	return str(weights[rule_id])
#end.

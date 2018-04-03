import argparse
import csv
import itertools
import random


def data_reader(predicate, folder_path):
	data_1 = []
	data_2 = []
	true_data = []
	with open(folder_path+"input.csv", 'rb') as resultFile:
		inputs = csv.reader(resultFile)
		for inp in inputs:
			data_1.append(inp[0])
			data_2.append(inp[1])
			true_data.append((inp[0],inp[1])) 
	return data_1, data_2, true_data


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--test_predicate", default='sample_case')
	args = parser.parse_args()
	folder_path = 'dataset/'+args.test_predicate+'/input/'
	data_1, data_2, true_data = data_reader(args.test_predicate, folder_path)
	catesian_data = []
	false_data = []
	true_sample = []
	for element in itertools.product(data_1,data_2):
		catesian_data.append(element)
	sample = random.sample(catesian_data,40)
	for sam in sample:
		if sam not in true_data:
			false_data.append(sam)
		else:
			true_sample.append(sam)
	print "True", len(true_sample), true_sample
	print "False", len(false_data), false_data




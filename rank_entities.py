# -*- coding: utf-8 -*-

import argparse
import csv
import sys
import sparql
from config import sparql_dbpedia

prefix = 'select count(*) where { <http://dbpedia.org/resource/'
suffix = ' ?p ?o.}'
sparql_endpoint = sparql_dbpedia


def get_rank(id,entity_1,entity_2,label):
    query_1 = prefix+ entity_1+'>'+suffix
    query_2 = prefix+entity_2+'>'+suffix
    # print query_1, query_2
    # try:
    result_1 = sparql.query(sparql_endpoint, query_1)
    result_2 = sparql.query(sparql_endpoint, query_2)
    value_1 = [sparql.unpack_row(row_result) for row_result in result_1][0][0]
    value_2 = [sparql.unpack_row(row_result) for row_result in result_2][0][0]
    score = (value_1+value_2)/2.0
    return [id,entity_1.encode('utf-8'),entity_2.encode('utf-8'),label,score]


def write_test(triples,file_name,folder_path):
    print file_name+"_0k.csv"
    with open(folder_path+file_name+"_0k.csv", 'wb') as resultFile:
        wr = csv.writer(resultFile,quotechar='"')
        wr.writerows(triples)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    args = parser.parse_args()
    folder_path = 'dataset/' + args.test_predicate + '/input/'
    with open('dataset/' + args.test_predicate + '/input/test_0k.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        positive_triples = []
        negative_triples = []
        for row in reader:
            entity_1 = row.get('sub').decode('utf-8')
            entity_2 = row.get('obj').decode('utf-8')
            label = row.get('class')
            id = row.get('sid')
            if label == '1':
                positive_triples.append(get_rank(id,entity_1,entity_2,label))
            else:
                negative_triples.append(get_rank(id,entity_1,entity_2,label))
        # print positive_triples
        # print negative_triples
        print "sorting data"
        positive_triples.sort(key=lambda x: x[4])
        negative_triples.sort(key=lambda x: x[4])
        # print positive_triples, negative_triples
        write_test(positive_triples[:100],'pos_bot100',folder_path)
        write_test(positive_triples[100:],'pos_top100',folder_path)
        write_test(negative_triples[:100],'neg_bot100',folder_path)
        write_test(negative_triples[100:],'neg_top100',folder_path)


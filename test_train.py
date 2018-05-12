# -*- coding: utf-8 -*-

import sparql
from config import sparql_dbpedia
import argparse
import csv
import sys

sparql_endpoint = sparql_dbpedia
training_size = 5000
data_size = '5k'
suffix = "} ORDER BY RAND() LIMIT "+str(training_size)


def get_query(subject, object, relation):
    print "Executing negative candidate query selection"
    prefix = "PREFIX dbp: <http://dbpedia.org/property/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> " \
             "PREFIX dbo: <http://dbpedia.org/ontology/> SELECT DISTINCT ?subject ?object  FROM <http://dbpedia.org> " \
             "WHERE { ?object <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/"+object+">. " \
             "?subject <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/"+subject+">. "

    negative_query = prefix + " {{?subject ?targetRelation ?realObject.} UNION  {?realSubject ?targetRelation ?object.}} " \
                              "?subject ?otherRelation ?object. " \
                              "FILTER (?targetRelation = <http://dbpedia.org/ontology/"+relation+">) " \
                              "FILTER (?otherRelation != <http://dbpedia.org/ontology/"+relation+">) " \
                              "FILTER NOT EXISTS {?subject <http://dbpedia.org/ontology/"+relation+"> ?object.} " + suffix
    print "Executing positive candidate query selection"

    positive_query = prefix + " ?subject ?targetRelation ?object.   " \
                              "FILTER (?targetRelation = <http://dbpedia.org/ontology/"+relation+">) " + suffix
    print positive_query
    print negative_query
    return positive_query, negative_query


def get_examples(query):
    try:
        result = sparql.query(sparql_endpoint, query)
        examples = [sparql.unpack_row(row_result) for row_result in result]
        examples = [map(lambda x:x.split('/')[-1].encode('utf-8'), vals) for vals in examples]
    except:
        examples = []
    if examples:
        size = len(examples)
        # train_size = size / 5
        return examples[:200], examples[200:]
        # return [], examples
    return [], []


def write_examples(folder_path, file_name, examples):
    with open(folder_path+file_name+"_"+data_size+".csv", 'wb') as resultFile:
        wr = csv.writer(resultFile,quotechar='"')
        wr.writerows(examples)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test_predicate", default='spouse')
    parser.add_argument("-s", "--subject", default='Person')
    parser.add_argument("-o", "--object", default='Person')
    args = parser.parse_args()
    folder_path = 'dataset/'+args.test_predicate+'/input/'

    positive_query, negative_query = get_query(args.subject, args.object,args.test_predicate)

    positive_test, positive_train = get_examples(positive_query)
    positive_test = [[i+1]+pos_test +[1] for i,pos_test in enumerate(positive_test)]

    negative_test, negative_train = get_examples(negative_query)

    negative_test = [[i+201]+neg_test + [0] for i,neg_test in enumerate(negative_test)]

    file_names = {'positive_examples':positive_train, 'negative_examples': negative_train, 'test':positive_test+negative_test}
    for file_name,examples in file_names.iteritems():
        print "writing", file_name
        write_examples(folder_path, file_name, examples)


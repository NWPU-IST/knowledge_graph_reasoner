# -*- coding: utf-8 -*-

import sparql
from config import sparql_dbpedia

sparql_endpoint = sparql_dbpedia
suffix = "} ORDER BY RAND() LIMIT 1000"


subject = 'Work'
object = 'Person'
relation = 'director'


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
    return positive_query, negative_query


def get_examples(query):
    try:
        result = sparql.query(sparql_endpoint, query)
        examples = [sparql.unpack_row(row_result) for row_result in result]
    except:
        examples = []
    if examples:
        size = len(examples)
        train_size = 0.8 * size
        return examples[:train_size], examples[train_size:]
    return [], []


def write_examples(folder_path, file_name, examples):
    pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test_predicate", default='spouse')
    parser.add_argument("-s", "--subject", default='Person')
    parser.add_argument("-o", "--object", default='Person')
    args = parser.parse_args()
    folder_path = 'dataset/'+args.test_predicate+'/input/'

    positive_train, positive_test = get_examples(positive_query)

    negative_train, negative_test = get_examples(negative_query)

    file_name = 'dataset/'+args.test_predicate+'/input/'+args.rule_type+'/'+args.filename+'.csv'

    write_examples(folder_path, file_name, examples)


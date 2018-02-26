from config import rule_mining, rule_type, top_k
import sys
import re
from ordered_set import OrderedSet
from more_itertools import unique_everseen
import os


def get_rule_predicates(data_source):
    text = open('dataset/' + data_source + '/rules/'+ rule_mining + '/'+ rule_type + '/' + "top" + str(top_k), 'r')
    f = text.read()
    text.close()
    probs = re.findall("(\w+\()", f)
    probs = list(set(probs))
    predicates = [p.replace('(', '') for p in probs]
    return predicates


def evidence_writer(evidences, sentence_id, data_source, resource_v, rule_predicates):
    item_set = OrderedSet()
    for evidence in evidences:
        if evidence[1] in rule_predicates:
            if evidence[0] == resource_v[0] and evidence[2] == resource_v[1] and evidence[1] == data_source:
                pass
            else:
                try:
                    item_set.add(evidence[1] + '("' + evidence[0] + '","' + evidence[2] + '").')
                except:
                    pass
    with open('dataset/' + data_source + '/evidence/'+ rule_mining + '/' + str(sentence_id)+'_.txt', 'wb') as csvfile:
        for i in item_set:
            if '*' not in i:
                try:
                    print i
                    csvfile.write(i+'\n')
                except:
                    pass

    with open('dataset/' + data_source + '/evidence/'+ rule_mining + '/' + str(sentence_id)+'_.txt', 'r') as f, \
            open('dataset/' + data_source + '/evidence/'+ rule_mining + '/' + str(sentence_id) + '_unique.txt', 'wb') as out_file:
        out_file.writelines(unique_everseen(f))
    remove_file = 'dataset/' + data_source + '/evidence/'+ rule_mining + '/' + str(sentence_id)+'_.txt'
    os.remove(remove_file)
    return item_set


def clingo_map(sentence_id, data_source, resource_v, top_k, predicate, set_up):
    print "Clingo Inference"
    evidence_source = 'LPmln/' + data_source + '/' + set_up + '/evidence_'+top_k+'/' + sentence_id + predicate
    cmd = "clingo {0}{4}/rudik_rules_{1}/{3}_all {2}_unique.txt > {0}clingo_result.txt ".format('LPmln/' + data_source +\
                                                                                            '/', top_k, evidence_source,\
                                                                                            predicate, set_up)
    print cmd
    subprocess.call(cmd, shell=True)
    text = open('LPmln/' +data_source + '/' + 'clingo_result.txt', 'r')
    f = text.read()
    text.close()
    probs = re.findall("(\w+\([\s\S]+\"\))",f)
    if probs:
        probs = probs[0].split(' ')
        probs = [p for p in probs if resource_v[1] in p or resource_v[0] in p]
        probs_test = [p for p in probs if resource_v[1] in p and resource_v[0] in p and predicate in p]
    else:
        probs = []
        probs_test = []
    return probs, probs_test
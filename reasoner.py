from config import rule_mining, rule_type, top_k, dbpedia
import sys
import re
from ordered_set import OrderedSet
from more_itertools import unique_everseen
import os
import subprocess


def get_rule_predicates(data_source):
    global evidence_path
    evidence_path = 'dataset/' + data_source + '/evidence/' + dbpedia + '/' + rule_mining + '/' + "top" + str(
        top_k) + '/'
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
            elif evidence[0] == resource_v[1] and evidence[2] == resource_v[0] and evidence[1] in ["keyPerson"]:
                pass
            else:
                try:
                    if '"' not in evidence[0] and '"' not in evidence[2]:
                        if ':' not in evidence[0] and ':' not in evidence[2]:
                            if '#' not in evidence[0] and '#' not in evidence[2]:
                                item_set.add(evidence[1] + '("' + evidence[0] + '","' + evidence[2] + '").')
                except:
                    pass
    with open(evidence_path + str(sentence_id) + '_.txt', 'wb') as csvfile:
        for i in item_set:
            if '*' not in i:
                try:
                    print i
                    csvfile.write(i+'\n')
                except:
                    pass
    with open(evidence_path + str(sentence_id) + '_.txt', 'r') as f, \
            open(evidence_path + str(sentence_id) + '_unique.txt', 'wb') as out_file:
        out_file.writelines(unique_everseen(f))
    remove_file = evidence_path + str(sentence_id) + '_.txt'
    os.remove(remove_file)
    return item_set


def clingo_map(sentence_id, data_source, resource_v):
    print "Clingo Inference"
    cmd = "clingo {0}rules/{2}/hard/top{1} {5}{4}_unique.txt > {0}clingo_result.txt ".format('dataset/' +\
                                                                                                         data_source +\
                                                                                                         '/', top_k,\
                                                                                                         rule_mining, \
                                                                                                          data_source, sentence_id, evidence_path)
    print cmd
    subprocess.call(cmd, shell=True)
    text = open('dataset/' +data_source + '/' + 'clingo_result.txt', 'r')
    f = text.read()
    text.close()
    probs = re.findall("(\w+\([\s\S]+\"\))",f)
    if probs:
        probs = probs[0].split(' ')
        probs = [p for p in probs if resource_v[1] in p or resource_v[0] in p]
        probs_test = [p for p in probs if resource_v[1] in p and resource_v[0] in p and data_source in p]
    else:
        if "UNKNOWN" in f:
            probs = "err"
            probs_test = "err"
        else:
            probs = []
            probs_test = []
    return probs, probs_test


def inference_map(sentence_id, data_source, resource_v):
    print "LPMLN MAP Inference"
    cmd = "lpmln2asp -i {0}rules/{2}/hard/top{1} -q {3} -e {5}{4}_unique.txt -r {0}map_result.txt".format('dataset/' +\
                                                                                                         data_source +\
                                                                                                         '/', top_k,\
                                                                                                         rule_mining, \
                                                                                                        data_source, sentence_id, evidence_path)
    print cmd
    subprocess.call(cmd, shell=True)
    text = open('dataset/' + data_source + '/' + 'map_result.txt', 'r')
    f = text.read()
    text.close()
    probs = re.findall("(\w+\(\'[\s\S].+)", f)
    probs = [p for p in probs if resource_v[1] in p or resource_v[0] in p]
    probs_test = [p for p in probs if resource_v[1] in p and resource_v[0] in p and data_source in p]
    return probs, probs_test


def inference_prob(sentence_id, data_source, resource_v):
    print "LPMLN Probability Inference"
    cmd = "lpmln2asp -i {0}rules/{2}/soft/top{1} -q {3} -e {5}{4}_unique.txt -r {0}prob_result.txt".format(
        'dataset/' + data_source + '/', top_k, rule_mining, data_source, sentence_id, evidence_path)
    print cmd
    subprocess.call(cmd, shell=True)
    text = open('dataset/' + data_source + '/' + 'prob_result.txt', 'r')
    f = text.read()
    text.close()
    probs = re.findall("(\w+\(\'[\s\S].+)", f)
    probs = [p for p in probs if resource_v[1] in p or resource_v[0] in p]
    probs_test = [p for p in probs if resource_v[1] in p and resource_v[0] in p and predicate in p]
    return probs, probs_test

from config import rule_mining, rule_type, top_k, dbpedia
import sys
import re
from ordered_set import OrderedSet
from more_itertools import unique_everseen
import os
import subprocess
from itertools import product


def get_rule_predicates(data_source, data_size, const):
    global evidence_path
    evidence_path = 'dataset/' + data_source + '/evidence/' + dbpedia + '/' + rule_mining + '/' + "topset_conf_"+ const + data_size + '/'
    text = open('dataset/' + data_source + '/rules/' + rule_mining + '/' + rule_type + '/' + "topset_conf_" + data_size, 'r')
    f = text.read()
    text.close()
    probs = re.findall("(\w+\()", f)
    probs = list(set(probs))
    predicates = [p.replace('(', '') for p in probs]
    return predicates, f


def evidence_writer(evidences, sentence_id, data_source, resource_v, rule_predicates):
    item_set = OrderedSet()
    entity_set = []
    # print rule_predicates
    for evidence in evidences:
        # print evidence[1]
        if evidence[1] in rule_predicates or top_k == 0:
            if evidence[0] == resource_v[0] and evidence[2] == resource_v[1] and evidence[1] == data_source:
                pass
            elif evidence[0] == resource_v[1] and evidence[2] == resource_v[0] and evidence[1] in ["keyPerson","capital"]:
                pass
            else:
                try:
                    if '"' not in evidence[0] and '"' not in evidence[2]:
                        if ':' not in evidence[0] and ':' not in evidence[2]:
                            if '#' not in evidence[0] and '#' not in evidence[2]:
                                if '&' not in evidence[0] and '&' not in evidence[2]:
                                    if '=' not in evidence[0] and '=' not in evidence[2]:
                                        if ' ' not in evidence[0] and ' ' not in evidence[2]:
                                            entity_1 = '"'+evidence[0]+'"'
                                            entity_2 = '"'+evidence[2]+'"'
                                            item_set.add(evidence[1] + '(' + entity_1 + ',' + entity_2 + ').')
                except:
                    pass
        else:
            pass
            # print "here"
    # print item_set
    with open(evidence_path + str(sentence_id) + '_.txt', 'wb') as csvfile:
        for i in item_set:
            if '*' not in i:
                try:
                    # print i
                    csvfile.write(i.encode('utf-8') + '\n')
                    # csvfile.write(i+'\n')
                except:
                    pass
    with open(evidence_path + str(sentence_id) + '_.txt', 'r') as f, \
            open(evidence_path + str(sentence_id) + '_unique.txt', 'wb') as out_file:
        out_file.writelines(unique_everseen(f))
    remove_file = evidence_path + str(sentence_id) + '_.txt'
    os.remove(remove_file)
    return item_set, entity_set


def rule_evidence_writer(evidences, sentence_id, data_source, resource_v, rule_predicates, rules):
    item_set = OrderedSet()
    entity_set = []
    for evidence in evidences:
        if evidence[1] in rule_predicates or top_k==0:
            if evidence[0] == resource_v[0] and evidence[2] == resource_v[1] and evidence[1] == data_source:
                pass
            elif evidence[0] == resource_v[1] and evidence[2] == resource_v[0] and evidence[1] in ["keyPerson","capital"]:
                pass
            else:
                try:
                    if '"' not in evidence[0] and '"' not in evidence[2]:
                        if ':' not in evidence[0] and ':' not in evidence[2]:
                            if '#' not in evidence[0] and '#' not in evidence[2]:
                                if '&' not in evidence[0] and '&' not in evidence[2]:
                                    if ' ' not in evidence[0] and ' ' not in evidence[2]:
                                        item_set.add(evidence[1] + '("' + evidence[0] + '","' + evidence[2] + '").')
                                        if evidence[0] not in entity_set and " " not in evidence[0]:
                                            entity_set.append(evidence[0])
                                        if evidence[2] not in entity_set and " " not in evidence[2]:
                                            entity_set.append(evidence[2])
                except:
                    pass

    with open(evidence_path + str(sentence_id) + '_er.txt', 'wb') as csvfile:
        csvfile.writelines(rules)
        csvfile.write('\n')
        for i in item_set:
            if '*' not in i:
                try:
                    csvfile.write(i.encode('utf-8')+'\n')
                except:
                    pass
    with open(evidence_path + str(sentence_id) + '_er.txt', 'r') as f, \
            open(evidence_path + str(sentence_id) + 'er_unique.txt', 'wb') as out_file:
        out_file.writelines(unique_everseen(f))
    remove_file = evidence_path + str(sentence_id) + '_er.txt'
    os.remove(remove_file)
    return item_set, entity_set


def clingo_map(sentence_id, data_source, resource_v):
    resource_v = ['"' + res + '"' for res in resource_v]
    print "Clingo Inference"
    cmd = "clingo {0}rules/{2}/hard/top{1} {5}{4}_unique.txt > {0}clingo_result.txt ".format('dataset/' +\
                                    data_source + '/', top_k, rule_mining, data_source, sentence_id, evidence_path)
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


def get_label(f, data_source, resource_v):
    probs, map_output = [], []
    if 'UNSATISFIABLE' in f:
        label = "UNSAT"
    else:
        probs = re.findall("\d+?\n(\w+\(.*\))", f)
        if probs:
            answer_set = probs[-1]
            answer_set = answer_set.split(' ')
            # probs = [p for p in probs if resource_v[1] in p or resource_v[0] in p]
            # probs_test = [p for p in probs if resource_v[1] in p and resource_v[0] in p and pos_neg+data_source in p]
            query = ['neg'+data_source+'('+','.join(resource_v)+')', data_source+'('+','.join(resource_v)+')']
            map_output = [p for p in answer_set if p.decode('utf-8') in query]
        else:
            map_output = []

        if map_output:
            if len(map_output) == 1:
                if 'neg' not in map_output[0]:
                    label = "1"
                else:
                    label = "-1"
            else:
                label = "0"
        else:
            label = "None"
    print label
    return map_output, label




def inference_map(sentence_id, data_source, resource_v):
    print resource_v
    resource_v = ['"' + res + '"' for res in resource_v]
    cmd = "lpmln2asp -i {0}rules/{2}/hard/top{1} -e {5}{4}_unique.txt -r {0}map_result.txt".format('dataset/' +\
                                        data_source + '/', top_k, rule_mining, data_source, sentence_id, evidence_path)
    print cmd
    FNULL = open(os.devnull, 'w')
    subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    text = open('dataset/' + data_source + '/' + 'map_result.txt', 'r')
    f = text.read()
    text.close()
    map_output, label = get_label(f, data_source, resource_v)
    return map_output, label


def inference_map_weight(sentence_id, data_source, resource_v):
    resource_v = ['"' + res + '"' for res in resource_v]
    cmd = "lpmln2asp -i {0}rules/{2}/soft/top{1} -e {5}{4}_unique.txt -r {0}map_result.txt".format('dataset/' +\
                                        data_source + '/', top_k, rule_mining, data_source, sentence_id, evidence_path)
    print cmd
    FNULL = open(os.devnull, 'w')
    subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    text = open('dataset/' + data_source + '/' + 'map_result.txt', 'r')
    f = text.read()
    text.close()
    map_output, label = get_label(f, data_source, resource_v)
    return map_output, label


def write_query_domain(data_source, sentence_id,resource_v):
    with open('lpmln-learning/code/query_domain.txt', 'w') as the_file:
        the_file.write('neg'+data_source+','+data_source+'\n')
        the_file.write(str(resource_v)+'\n')
        the_file.write("{1}{0}_domain.txt".format(sentence_id, evidence_path))


def inference_prob(sentence_id, data_source, resource_v):
    write_query_domain(data_source, sentence_id, resource_v)
    print "LPMLN Probability Inference"
    cmd = "lpmln2asp -i {1}{0}er_unique.txt".format(sentence_id, evidence_path)
    print cmd
    subprocess.call(cmd, shell=True)
    try:
        cmd1 = "clingo -q lpmln-learning/code/marginal-mhsampling.py out.txt"
        print cmd1
        subprocess.call(cmd1, shell=True)
    except:
        pass
    text = open('lpmln-learning/code/lpmln_prob.txt', 'r')
    probs = text.read()
    text.close()
    # with open('lpmln-learning/code/lpmln_prob.txt', 'w') as the_file:
    #     the_file.write('utf-8')
    return probs.split(";")


def inference_prob_mcsat(sentence_id, data_source, resource_v):
    write_query_domain(data_source, sentence_id, resource_v)
    print "LPMLN Probability MC-SAT Inference"
    cmd = "lpmln2asp -i {1}{0}er_unique.txt".format(sentence_id, evidence_path)
    print cmd
    FNULL = open(os.devnull, 'w')
    subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

    try:
        cmd1 = "python lpmln-learning/code/marginal-mcsat.py out.txt"
        print cmd1
        # subprocess.call(cmd1, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(cmd1, shell=True)
    except:
        print "here you go"
        pass
    text = open('lpmln-learning/code/lpmln_prob_mc.txt', 'r')
    probs = text.read()
    text.close()
    # with open('lpmln-learning/code/lpmln_prob.txt', 'w') as the_file:
    #     the_file.write('utf-8')
    return probs.split(";")


def domain_generator(entity_set, sentence_id, data_source):
    domain_text_pos = data_source+'~'
    domain_text_neg = 'neg'+data_source+'~'
    domain_text = "&".join('"%s";"%s"' % pair for pair in product(entity_set, repeat=2))
    if domain_text:
        with open(evidence_path + str(sentence_id) + "_domain.txt", "w") as text_file:
            text_file.write(domain_text_pos+domain_text.encode('utf-8')+'\n')
            text_file.write(domain_text_neg + domain_text.encode('utf-8'))
# -*- coding: utf-8 -*-

import argparse
import sys
import re
import csv
import sparql
from config import sparql_dbpedia

prefix = "select count(*) where {"
suffix = "}"
ontology = " <http://dbpedia.org/ontology/"
sparql_endpoint = sparql_dbpedia
query_dict = {'?subject': 0,'?object': 1}
comp = ["<",">","=","!="]
rep = {"subject": "A", "object": "B", "v0": "C", "v1": "D"}


def get_confidence_rudik(numerator_query, denominator_query, pos_neg, examples):
    rule_true = 0
    body_true = 0
    i = 0
    for example in examples:
        # print i, example
        # i += 1
        # numerator_query_new = numerator_query.replace('?subject','<http://dbpedia.org/resource/'+example[0]+'>')
        denominator_query_new = denominator_query.replace('?subject','<http://dbpedia.org/resource/'+example[0]+'>')
        denominator_query_new = denominator_query_new.replace('?object','<http://dbpedia.org/resource/'+example[1]+'>')
        # numerator_query_new = numerator_query_new.replace('?object','<http://dbpedia.org/resource/'+example[1]+'>')
        # try:
        #     result = sparql.query(sparql_endpoint, numerator_query_new)
        #     numerator_value = [sparql.unpack_row(row_result) for row_result in result][0][0]
        # except:
        #     numerator_value = 0
        try:
            result = sparql.query(sparql_endpoint, denominator_query_new)
            denominator_value = [sparql.unpack_row(row_result) for row_result in result][0][0]
        except:
            denominator_value = 0
        # print numerator_value, denominator_value
        # if numerator_value > 0:
        #     rule_true += 1
        if denominator_value > 0:
            body_true += 1
    # print numerator_query_new
    print denominator_query_new
    print "-----------------"
    print float(body_true),float(len(examples))
    confidence = float(body_true)/float(len(examples))
    return confidence


def get_confidence_amie(denominator_query, examples):
    body_true = 0
    for i,example in enumerate(examples):
        denominator_query_new = denominator_query.replace('?a','<http://dbpedia.org/resource/'+example[0].decode('utf-8')+'>')
        denominator_query_new = denominator_query_new.replace('?b','<http://dbpedia.org/resource/'+example[1].decode('utf-8')+'>')
        try:
            result = sparql.query(sparql_endpoint, denominator_query_new)
            denominator_value = [sparql.unpack_row(row_result) for row_result in result][0][0]
        except:
            print denominator_query_new,i
            denominator_value = 0
        if denominator_value > 0:
            body_true += 1
    # print denominator_query_new
    print "-----------------"
    print float(body_true),float(len(examples))
    confidence = float(body_true)/float(len(examples))
    return confidence


def get_rudik_query(relations, predicate):
    head_query = "?subject " + ontology + predicate + "> ?object . \n"
    query = ''
    for relation in relations:
        predicate = re.findall(r"(.*?)\(", relation)
        var = re.findall(r"\((.*)\)", relation)
        vars = var[0].split(",")
        if predicate[0] in comp:
            query += 'FILTER ( ?'+vars[0] + ' '+ predicate[0] + ' ?'+vars[1] + ').'
        else:
            query += " ?"+vars[0] + ontology + predicate[0] + "> ?"+vars[1] + ". \n"
    numerator_query = prefix + head_query + query + suffix
    denominator_query = prefix + query + suffix
    return numerator_query, denominator_query


def get_amie_query(relations, vars):
    query = ''
    for i, rel in enumerate(relations):
        query += " ?" + vars[2*i] + ontology + rel + "> ?" + vars[2*i+1] + ". \n"
    denominator_query = prefix + query + suffix
    return denominator_query


def rule_parser_rudik(fname, predicate, pos_neg, examples):
    soft_rule_list = []
    hard_rule_list = []
    with open(fname) as f:
        content = f.readlines()
    for it, con in enumerate(content):
        print it, con
        # sys.exit()
        relation = re.findall(r"\/([a-zA-Z]+\(.*?\))", con)
        compare = re.findall(r"([!>=<!]+?\(.*?\))", con)
        print relation+compare
        numerator_quer, denominator_query = get_rudik_query(relation+compare, predicate)
        score = get_confidence_rudik(numerator_quer, denominator_query, pos_neg,examples)
        print score
        for i, com in enumerate(compare):
            for c in comp:
                if c in com:
                    com = com.replace(c+'(', "")
                    com = com.replace(')', "")
                    com = com.replace(',', c)
            compare[i] = com
        relation += compare
        for i, rel in enumerate(relation):
            for r in rep.keys():
                if r in rel:
                    rel = rel.replace(r, rep[r])
            relation[i] = rel
        # score = re.findall(r"\-?\d+.\d+$", con)
        # score = round(0.7 - float(score[0]), 2)
        i = 0
        # if score:
            # rule = str(score)+' '+pos_neg+predicate+"("+ str(it+1)+",A,B) :- "
        # rule = str(score)+' '+pos_neg+predicate+"(A,B) :- "
        if pos_neg == 'pos':
            rule = predicate+"(A,B) :- "
        else:
            rule = pos_neg+predicate+"(A,B) :- "
        # else:
        #     rule = pos_neg + predicate + "(A,B) :- "
        for rel in relation:
            rule += rel
            if i == len(relation)-1:
                rule += '.'
            else:
                rule += ', '
            i += 1
        if "C<C" not in rule and "C>C" not in rule:
            soft_rule_list.append(str(score)+' '+rule)
            hard_rule_list.append(rule)
    # print soft_rule_list, hard_rule_list
    return soft_rule_list, hard_rule_list


def rule_parser_amie(fname, examples, predicate):
    soft_rule_list = []
    hard_rule_list = []
    with open(fname) as f:
        content = f.readlines()
    for it, con in enumerate(content):
        print it, con
        vars = re.findall(r"\?(.)", con)
        # score = re.findall(r"\d.\d+", con)
        # score = score[0]
        relation = re.findall(r":(.*?)\>", con)
        denominator_query = get_amie_query(relation, vars)
        score = get_confidence_amie(denominator_query, examples)
        print score
        vars = [var.upper() for var in vars]
        if relation.index(predicate) != 0:
            new_index = relation.index(predicate)
            temp = relation[0]
            relation[0] = predicate
            relation[new_index] = temp
            vars[new_index*2],vars[0] = vars[0], vars[new_index*2]
            vars[new_index*2+1], vars[1] = vars[1], vars[new_index*2+1]
        i = 0
        # rule = str(score[0]+' ')
        rule = ''
        for rel in relation:
            rule += rel + '('+vars[i] + ',' + vars[i+1]+')'
            # print i, rule
            if i == 0:
                rule += ' :- '
            elif i == len(vars)-2:
                rule += '.'
            else:
                rule += ' , '
            i += 2
        # print rule
        if score>0:
            hard_rule_list.append(rule)
            soft_rule_list.append(str(score)+' '+rule)
    return hard_rule_list, soft_rule_list


def soft_rule_writer(rule_list, predicate, rule_type, folder_path, pos_neg, k):
    with open(folder_path+"soft/topset_conf_"+k, 'ab') as resultFile:
        wr = csv.writer(resultFile, quoting=csv.QUOTE_NONE, escapechar=' ')
        for rule in rule_list:
            wr.writerow([rule,])


def soft_rule_writer_constraint(rule_list, predicate, rule_type, folder_path, pos_neg, k, constraint_rule):
    with open(folder_path+"soft/topset_conf_const_"+k, 'ab') as resultFile:
        wr = csv.writer(resultFile, quoting=csv.QUOTE_NONE, escapechar=' ')
        for rule in rule_list:
            wr.writerow([rule,])
        if pos_neg=='pos':
            wr.writerow([constraint_rule, ])


def hard_rule_writer(rule_list, predicate, rule_type, folder_path, pos_neg, k):
    with open(folder_path+"hard/topset_conf_"+k, 'ab') as resultFile:
        wr = csv.writer(resultFile, quoting=csv.QUOTE_NONE, escapechar=' ')
        for rule in rule_list:
            wr.writerow([rule,])


def hard_rule_writer_constraint(rule_list, predicate, rule_type, folder_path, pos_neg, k, constraint_rule):
    with open(folder_path+"hard/topset_conf_const_"+k, 'ab') as resultFile:
        wr = csv.writer(resultFile, quoting=csv.QUOTE_NONE, escapechar=' ')
        for rule in rule_list:
            wr.writerow([rule,])
        if pos_neg =='pos':
            wr.writerow([constraint_rule, ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("-t", "--test_predicate", default='sample_case')
    # parser.add_argument("-i", "--filename", default='')
    parser.add_argument("-r", "--rule_type", default='amie')
    # parser.add_argument("-p", "--pos_neg", default='')
    args = parser.parse_args()
    # data_size = {'1k': 1000, '5k': 5000,'0k': 5000}
    data_size = {'10k':10000}
    # rule_set = ['pos', 'neg']
    rule_set = ['pos']
    # positive_query, negative_query = get_query(args.subject, args.object,args.test_predicate)
    rule_type = args.rule_type
    with open('dataset/dataset_lpmln.csv','rb') as datainput:
        reader = csv.DictReader(datainput)
        for row in reader:
            subject = row.get('subject')
            test_predicate = row.get('predicate')
            object = row.get('object')
            print "----------------------"
            print subject, test_predicate, object
            print "----------------------"
            folder_path = 'dataset/' + test_predicate + '/rules/' + rule_type + '/'
            for k, v in data_size.iteritems():
                print "query for",k,v
                for pos_neg in rule_set:
                    filename = test_predicate + '_' + pos_neg + '_' + k
                    path = 'dataset/'+test_predicate+'/rules/'+rule_type+'/'+filename+'.csv'
                    if pos_neg=='pos':
                        train_examples = 'positive_'
                    else:
                        train_examples = 'negative_'
                    print 'dataset/'+test_predicate+'/input/'+train_examples+'examples_'+k+'.csv'
                    with open('dataset/'+test_predicate+'/input/'+train_examples+'examples_'+k+'.csv', 'rb') as csvfile:
                        example_reader = csv.reader(csvfile)
                        examples = list(example_reader)
                    if rule_type == 'amie':
                        hard_rule_list, soft_rule_list = rule_parser_amie(path, examples, test_predicate)
                        hard_rule_writer(hard_rule_list, test_predicate, rule_type, folder_path, pos_neg, k)
                        soft_rule_writer(soft_rule_list, test_predicate, rule_type, folder_path, pos_neg, k)
                    else:
                        soft_rule_list, hard_rule_list = rule_parser_rudik(path, test_predicate, pos_neg,examples)
                        constraint_rule = ':- '+test_predicate+'(A,B), neg'+test_predicate+'(A,B).'
                        soft_rule_writer(soft_rule_list, test_predicate, rule_type, folder_path, pos_neg, k)
                        soft_rule_writer_constraint(soft_rule_list, test_predicate, rule_type, folder_path, pos_neg, k, constraint_rule)
                        hard_rule_writer(hard_rule_list, test_predicate,rule_type, folder_path, pos_neg, k)
                        hard_rule_writer_constraint(hard_rule_list, test_predicate,rule_type, folder_path, pos_neg, k, constraint_rule)
import argparse
import sys
import re
import csv


def rule_parser_amie(fname, predicate):
    with open(fname) as f:
        content = f.readlines()
    rule_list = []
    for it,con in enumerate(content):
        relation = re.findall(r":(.*?)\>", con)
        if relation.index(predicate) != 0:
            new_index = relation.index(predicate)
            temp = relation[0]
            relation[0] = predicate
            relation[new_index] = temp
        vars = re.findall(r"\?(.)", con)
        score = re.findall(r"\d.\d+", con)
        vars = [var.upper() for var in vars]
        i = 0
        rule = str(score[0]+' ')
        for rel in relation:
            rule += rel +'('+vars[i]+','+ vars[i+1]+')'
            if i == 0:
                rule += ' :- '
            elif i == len(relation)-1:
                rule += '.'
            else:
                rule += ' , '
            i += 1
        rule_list.append(rule)
    return rule_list


def rule_writer(rule_list, predicate, rule_type, folder_path):
    with open(folder_path+predicate+"_"+rule_type+".csv", 'wb') as resultFile:
        wr = csv.writer(resultFile,quoting = csv.QUOTE_NONE,escapechar=' ')
        for rule in rule_list:
            wr.writerow([rule,])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    parser.add_argument("-r", "--rule_type", default='amie')
    args = parser.parse_args()
    folder_path = 'dataset/'+args.test_predicate+'/rules/'+args.rule_type+'/'
    path = 'dataset/'+args.test_predicate+'/rules/'+args.rule_type+'/'+args.test_predicate+'.csv'
    if args.rule_type=='amie':
        rule_list = rule_parser_amie(path, args.test_predicate)
    rule_writer(rule_list, args.test_predicate,args.rule_type, folder_path)
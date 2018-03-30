import argparse
import sys
import re
import csv


def rule_parser_rudik(fname, predicate, pos_neg):
    with open(fname) as f:
        content = f.readlines()
    rule_list = []
    rep = {"subject":"A", "object":"B", "v0":"C", "v1":"D"}
    comp = ["<",">","="]
    for it, con in enumerate(content):
        relation = re.findall(r"\/([a-zA-Z]+\(.*?\))", con)
        compare = re.findall(r"([>=<]\(.*?\))", con)
        for i,com in enumerate(compare):
            for c in comp:
                if c in com:
                    com = com.replace(c+'(', "")
                    com = com.replace(')', "")
                    com = com.replace(',', c)
            compare[i] = com
        relation += compare
        for i,rel in enumerate(relation):
            for r in rep.keys():
                if r in rel:
                    rel = rel.replace(r, rep[r])
            relation[i] = rel
        score = re.findall(r"\d.\d+", con)
        print score
        i = 0
        if score:
            rule = str(score[0])+' '+pos_neg+predicate+"(A,B) :- "
        else:
            rule = pos_neg + predicate + "(A,B) :- "
        for rel in relation:
            rule += rel
            if i == len(relation)-1:
                rule += '.'
            else:
                rule += ' , '
            i += 1
        rule_list.append(rule)
    return rule_list


def rule_parser_amie(fname, predicate):
    with open(fname) as f:
        content = f.readlines()
    rule_list = []
    for it, con in enumerate(content):
        vars = re.findall(r"\?(.)", con)
        score = re.findall(r"\d.\d+", con)
        vars = [var.upper() for var in vars]
        relation = re.findall(r":(.*?)\>", con)
        if relation.index(predicate) != 0:
            new_index = relation.index(predicate)
            temp = relation[0]
            relation[0] = predicate
            relation[new_index] = temp
            vars[new_index*2],vars[0] = vars[0], vars[new_index*2]
            vars[new_index*2+1], vars[1] = vars[1], vars[new_index*2+1]
        i = 0
        rule = str(score[0]+' ')
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
        rule_list.append(rule)
        # sys.exit(0)
    return rule_list


def rule_writer(rule_list, predicate, rule_type, folder_path, pos_neg):
    with open(folder_path+predicate+"_"+rule_type+pos_neg+".csv", 'wb') as resultFile:
        wr = csv.writer(resultFile,quoting = csv.QUOTE_NONE,escapechar=' ')
        for rule in rule_list:
            wr.writerow([rule,])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    parser.add_argument("-r", "--rule_type", default='amie')
    parser.add_argument("-p", "--pos_neg", default='')
    args = parser.parse_args()
    folder_path = 'dataset/'+args.test_predicate+'/rules/'+args.rule_type+'/'
    path = 'dataset/'+args.test_predicate+'/rules/'+args.rule_type+'/'+args.test_predicate+args.pos_neg+'.csv'
    if args.rule_type=='amie':
        rule_list = rule_parser_amie(path, args.test_predicate)
    else:
        rule_list = rule_parser_rudik(path, args.test_predicate, args.pos_neg)
    rule_writer(rule_list, args.test_predicate,args.rule_type, folder_path, args.pos_neg)
import argparse
import sys


def rule_parser(fname):
    with open(fname) as f:
        content = f.readlines()
    for con in content:
        print con
        i = 0
        pred = ''
        for c in con:
            if c == "?":
                x = con[i+1]
                print x
            if c == ":":
                pred = ''
                i+=1
                while con[i] != ">":
                    pred += con[i]
                    i+=1
                print pred
            i+=1
        sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    parser.add_argument("-r", "--rule_type", default='amie')
    args = parser.parse_args()
    path = 'dataset/'+args.test_predicate+'/rules/'+args.rule_type+'/'+args.test_predicate+'.csv'
    rule_parser(path)
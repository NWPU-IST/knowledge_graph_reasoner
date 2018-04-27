import csv
import argparse
from main import lpmln_reasoning, stats_computer
from resource_writer import update_resources
from reasoner import get_rule_predicates
import sys


def query_test(triples_list, id_list, true_labels, data_source, input, pos_neg):
    # print row
    inferred = []
    true_count = 0
    false_count = 0
    true_pos = 0
    true_neg = 0
    false_neg, false_pos = 0, 0
    true_neutral, false_neutral = 0, 0
    rule_predicates, rules = get_rule_predicates(data_source)
    lpmln_evaluation = [['sentence_id', 'true_label', 'sentence', 'lpmln_label',\
                         'lpmln-prob', 'lpmln-map', 'clingo', 'prob_all',\
                                 'clingo_all', 'map_all']]
    for t, triple in enumerate(triples_list):
        sentence_id = id_list[t]
        true_label = int(float(true_labels[t]))
        # if not pos_neg:
        #     if true_label != 0:
        #         true_count += 1
        #     else:
        #         false_count += 1
        # else:
        #     if true_label == 0:
        #         true_count += 1
        #     else:
        #         false_count += 1

        if true_label == 1:
            true_count += 1
        else:
            false_count += 1

        triple_check = triples_list[t]
        print sentence_id, triple_check, true_label, '\n'
        answer_all, answer_set, map, map_all, prob, label, map, prob = lpmln_reasoning(triple_check,\
                                                        rule_predicates, sentence_id, data_source, rules, pos_neg)
        if map:
            if not pos_neg:
                if true_label == 1 and len(map) > 0:
                    true_pos += 1
                    prediction = 1
                    inferred.append({'sid': sentence_id, 'class': 1,'sub': triple_check[0], 'obj': triple_check[1]})
                elif true_label == 0 and len(map) == 0:
                    true_neg += 1
                    prediction = 1
                else:
                    prediction = 0
            else:
                if true_label == 0 and len(map) > 0:
                    true_pos += 1
                    prediction = 1
                elif true_label == 1 and len(map) == 0:
                    true_neg += 1
                    prediction = 1
                else:
                    prediction = 0


        if prob:
            if true_label == 1 and label == '1':
                true_pos += 1
            elif true_label == 0 and label == '-1':
                true_neg += 1
            elif true_label == 1 and label == '-1':
                false_neg += 1
            elif true_label == 0 and label == '1':
                false_pos += 1
            elif true_label == 1 and (label == 'equal' or label == '0'):
                true_neutral += 1
            elif true_label == 0 and (label == 'equal' or label == '0'):
                false_neutral += 1

        lpmln_evaluation.append([sentence_id, true_label, triple_check, label, str(prob), str(map), str(answer_set), \
                                 str(answer_all), str(map_all)])
    stats_computer(true_count, true_pos, false_count, true_neg, data_source, true_neutral, false_neutral, false_neg, false_pos)

    update_resources(triple_flag=False, ambiverse_flag=False, file_triples=False, ambiverse_resources=False,\
                     lpmln_evaluation=lpmln_evaluation, data_source=data_source, input=input, inferred=inferred)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default='triples_test.csv')
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    parser.add_argument("-p", "--pos_neg", default='')
    parser.add_argument("-s", "--sampling", default='')
    args = parser.parse_args()
    with open('dataset/' + args.test_predicate + '/input/' + args.input) as f:
        reader = csv.DictReader(f)
        triples_list = []
        id_list = []
        true_labels = []
        for row in reader:
            if args.sampling:
                triples_list.append([row.get('sub'), row.get('obj')])
            else:
                triples_list.append([row.get('sub').split(":")[1], row.get('obj').split(":")[1]])
            true_labels.append(row.get('class'))
            id_list.append(row.get('sid'))
        # print triples_list
        # sys.exit()
        query_test(triples_list, id_list, true_labels, args.test_predicate, args.input, args.pos_neg)
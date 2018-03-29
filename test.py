import csv
import argparse
from main import lpmln_reasoning
from resource_writer import update_resources
from reasoner import get_rule_predicates


def query_test(triples_list, id_list, true_labels, data_source, input):
    rule_predicates, rules = get_rule_predicates(data_source)
    lpmln_evaluation = [['sentence_id', 'true_label', 'sentence', 'label', 'prediction','lpmln-prob', 'lpmln-map', 'clingo', 'prob_all',\
                                 'clingo_all', 'map_all']]
    for t, triple in enumerate(triples_list):
        sentence_id = id_list[t]
        true_label = true_labels[t]
        triple_check = triples_list[t]
        print sentence_id, triple_check, true_label, '\n'

        answer_all, answer_set, map, map_all, prob, label = lpmln_reasoning(triple_check, rule_predicates, sentence_id,\
                                                                     data_source, rules)
        compare = float(true_label)-float(label)
        if compare != 0:
            prediction = 0
        else:
            prediction = 1
        lpmln_evaluation.append([sentence_id, true_label, triple_check,label,str(prediction), str(prob), str(map), str(answer_set), \
                                 str(answer_all), str(map_all)])

    update_resources(triple_flag=False, ambiverse_flag=False, file_triples=False, ambiverse_resources=False,\
                     lpmln_evaluation=lpmln_evaluation, data_source=data_source, input=input)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default='triples_test.csv')
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    args = parser.parse_args()
    with open('dataset/' + args.test_predicate + '/input/' + args.input) as f:
        reader = csv.DictReader(f)
        triples_list = []
        id_list = []
        true_labels = []
        for row in reader:
            triples_list.append([row.get('sub').split(":")[1],row.get('obj').split(":")[1]])
            true_labels.append(row.get('class'))
            id_list.append(row.get('sid'))
        print triples_list
        query_test(triples_list, id_list, true_labels, args.test_predicate, args.input)
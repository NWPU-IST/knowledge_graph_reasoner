import argparse
import csv, sys
from nltk import word_tokenize
from sentence_analysis import sentence_tagger, get_nodes, triples_extractor
import sys
from resources_loader import load_files
from resource_writer import update_resources
import pprint
from kb_query import distance_one_query, distance_two_query
from reasoner import evidence_writer, get_rule_predicates, clingo_map, inference_map, inference_prob, domain_generator,\
    rule_evidence_writer, inference_prob_mcsat
from ambiverse_api import ambiverse_entity_parser
from config import top_k
import datetime


def fact_checker(sentence_lis, id_list, true_labels, data_source, input, pos_neg):
    true_count = 0
    false_count = 0
    true_pos = 0
    true_neg = 0
    rule_predicates, rules = get_rule_predicates(data_source)
    file_triples, ambiverse_resources = load_files(data_source)
    sentence_list = [word_tokenize(sent) for sent in sentence_lis]
    named_tags = sentence_tagger(sentence_list)
    lpmln_evaluation = [
        ['sentence_id', 'true_label', 'sentence', 'label', 'prediction', 'lpmln-prob', 'lpmln-map', 'clingo',
         'prob_all', \
         'clingo_all', 'map_all']]
    triple_flag = False
    ambiverse_flag = False
    for n, ne in enumerate(named_tags):
        sentence_id = id_list[n]
        true_label = true_labels[n]
        if not pos_neg:
            if true_label == 'T':
                true_count += 1
            else:
                false_count += 1
        else:
            if true_label == 'F':
                true_count += 1
            else:
                false_count += 1
        sentence_check = sentence_lis[n]
        print sentence_id, sentence_check, true_label, '\n'
        named_entities = get_nodes(ne)
        entity_dict = dict(named_entities)
        print "NER: " + str(entity_dict)
        if sentence_id in file_triples.keys():
            triple_dict = file_triples[sentence_id]
        else:
            triple_dict = triples_extractor(sentence_check, named_entities)
            if triple_dict:
                file_triples[sentence_id] = triple_dict
                triple_flag = True
        print "Relation Triples: " + str(triple_dict)
        if sentence_id in ambiverse_resources.keys():
            resource = ambiverse_resources[sentence_id]
        else:
            resource = ambiverse_entity_parser(sentence_check)
            ambiverse_resources[sentence_id] = resource
            ambiverse_flag = True
        print "Resource Extractor"
        print "=================="
        pprint.pprint(resource)
        for triples_k, triples_v in triple_dict.iteritems():
            for triple_v in triples_v:
                resource_v = [resource.get(trip_v).get('dbpedia_id') for trip_v in triple_v]
        print resource_v
        answer_all, answer_set, map, map_all, prob, label_prob = lpmln_reasoning(resource_v, rule_predicates, sentence_id,\
                                                                     data_source, rules, pos_neg)
        if not pos_neg:
            if true_label == 'T' and len(map) > 0:
                true_pos += 1
                prediction = 1
            elif true_label == 'F' and len(map) == 0:
                true_neg += 1
                prediction = 1
            else:
                prediction = 0
        else:
            if true_label == 'F' and len(map) > 0:
                true_pos += 1
                prediction = 1
            elif true_label == 'T' and len(map) == 0:
                true_neg += 1
                prediction = 1
            else:
                prediction = 0

        lpmln_evaluation.append(
            [sentence_id, true_label, sentence_check, label, str(prediction), str(prob), str(map), str(answer_set), \
             str(answer_all), str(map_all)])
    stats_computer(true_count, true_pos, false_count, true_neg, data_source)
    update_resources(triple_flag, ambiverse_flag, file_triples, ambiverse_resources, lpmln_evaluation, data_source, input)


def lpmln_reasoning(resource_v, rule_predicates, sentence_id, data_source, rules, pos_neg):
    evidence = []
    resource_v = [entity.decode('utf-8') for entity in resource_v]
    for entity in resource_v:
        print entity
        evidence = distance_one_query(entity, evidence)
        evidence = distance_two_query(entity, evidence)
    # print evidence
    if evidence:
        # print "Predicate Set:"
        # print rule_predicates
        print "Evidence Set:"
        query_map = False
        if query_map:
            evidence_set, entity_set = evidence_writer(evidence, sentence_id, data_source, resource_v, rule_predicates)
            map_all, map, label_map = inference_map(sentence_id, data_source, resource_v, pos_neg)
            print map, map_all, label_map
            # answer_all, answer_set = clingo_map(sentence_id, data_source, resource_v)
            answer_set, answer_all = '', ''
        else:
            map_all, map, label_map = '', '', ''
            answer_set, answer_all = '', ''
            print answer_set, answer_all

        query_prob = True
        if query_prob:
            evidence_set, entity_set = rule_evidence_writer(evidence, sentence_id, data_source, resource_v, \
                                                            rule_predicates, rules)
            print "Writing Domain"
            domain_generator(entity_set, sentence_id, data_source)
            # prob, label_prob = inference_prob(sentence_id, data_source, resource_v)
            prob, label_prob = inference_prob_mcsat(sentence_id, data_source, resource_v)
            print prob, label_prob
            sys.exit()
        else:
            prob, label_prob = '',''

        return answer_all, answer_set, map, map_all, prob, label_prob, label_map, query_prob, query_map
    return '', '', '', '', '', '','', query_prob, query_map


def stats_computer(true_count, true_pos, false_count, true_neg, data_source, true_neutral, false_neutral, false_neg, \
                   false_pos, true_none, false_none):
    pre = 0
    rec = 0
    # false_neg = true_count-true_pos
    # false_pos = false_count - true_neg
    if true_count:
        tp = float(true_pos)/float(true_count)
    else:
        tp = 0
    if false_count:
        tn = float(true_neg)/float(false_count)
    else:
        tn = 0
    print "True Count:", true_count, "True Pos: ", true_pos, "=>", tp, "False Neg: ", false_neg
    print "False Count: ", false_count, "True Neg: ", true_neg, "=>", tn, "False Pos: ", false_pos
    if true_pos + false_pos > 0:
        pre = float(true_pos) / float(true_pos + false_pos)
    if true_pos + false_neg > 0:
        rec = float(true_pos) / float(true_pos + false_neg)
    print "Precision: ", pre
    print "Recall: ", rec
    print "True Neutral: ", true_neutral
    print "False Neutral: ", false_neutral
    print "True None: ", true_none
    print "False None: ", false_none
    true_data_pos = str(round(tp,2)) + ' ('+str(true_pos)+'/'+str(true_count)+')'
    false_data_pos = str(round(1-tp,2)) + ' (' + str(false_neg)+'/'+str(true_count)+')'
    true_data_neg = str(round(tn,2))+ ' ('+str(true_neg)+'/'+str(false_count)+')'
    false_data_neg = str(round(1-tn,2))+' ('+str(false_pos)+'/'+str(false_count)+')'
    st = datetime.datetime.now()
    output_stats = str(st) + ' ' + data_source + ' top-' + str(top_k) + ' & ' + true_data_pos + ' & ' + false_data_pos\
                   + ' & ' + true_data_neg + ' & ' + false_data_neg + ' & ' + str(round(pre, 2)) + ' & ' + str(round(rec, 2))
    with open('output_all.txt', 'a') as the_file:
        the_file.write(str(output_stats)+'\n')
    print output_stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default='sentences_test.csv')
    parser.add_argument("-l", "--lpmln", default=False)
    parser.add_argument("-s", "--sentence", default='')
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    parser.add_argument("-p", "--pos_neg", default='')
    args = parser.parse_args()
    with open('dataset/' + args.test_predicate + '/input/' + args.input) as f:
        reader = csv.DictReader(f)
        sentences_list = []
        id_list = []
        true_labels = []
        for row in reader:
            sentences_list.append(row.get('sentence'))
            true_labels.append(row.get('label'))
            id_list.append(row.get('id'))
        fact_checker(sentences_list, id_list, true_labels, args.test_predicate, args.input, args.pos_neg)
import argparse
import csv, sys
from nltk import word_tokenize
from sentence_analysis import sentence_tagger, get_nodes, triples_extractor
import sys
from resources_loader import load_files
from resource_writer import update_resources
import pprint
from kb_query import distance_one_query, distance_two_query
from reasoner import evidence_writer, get_rule_predicates, clingo_map, inference_map, inference_prob, domain_generator
from ambiverse_api import ambiverse_entity_parser


def fact_checker(sentence_lis, id_list, true_label, data_source):
    rule_predicates = get_rule_predicates(data_source)
    file_triples, ambiverse_resources = load_files(data_source)
    sentence_list = [word_tokenize(sent) for sent in sentence_lis]
    named_tags = sentence_tagger(sentence_list)
    lpmln_evaluation = [['sentence_id', 'true_label', 'sentence', 'lpmln-prob', 'lpmln-map', 'clingo', 'prob_all',\
                                 'clingo_all', 'map_all']]
    triple_flag = False
    ambiverse_flag = False
    for n, ne in enumerate(named_tags):
        sentence_id = id_list[n]
        true_label = true_labels[n]
        sentence_check = sentence_lis[n]
        print sentence_id, sentence_check, '\n'
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
        evidence = []
        for entity in resource_v:
            evidence = distance_one_query(entity, evidence)
            evidence = distance_two_query(entity, evidence)
        if evidence:
            print "Predicate Set:"
            print rule_predicates
            print "Evidence Set:"
            evidence_set, entity_set = evidence_writer(evidence, sentence_id, data_source, resource_v, rule_predicates)
        domain_generator(entity_set, sentence_id)
        answer_all, answer_set = clingo_map(sentence_id, data_source, resource_v)
        print answer_set, answer_all
        map_all, map = inference_map(sentence_id, data_source, resource_v)
        print map, map_all
        # prob_all, prob  = inference_prob(sentence_id, data_source, resource_v)
        prob, prob_all = [], []
        print prob, prob_all
        lpmln_evaluation.append([sentence_id, true_label, sentence_check, str(prob), str(map), str(answer_set), str(prob_all),\
                                 str(answer_all), str(map_all)])
    update_resources(triple_flag, ambiverse_flag, file_triples, ambiverse_resources, lpmln_evaluation, data_source)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default='sentences_test.csv')
    parser.add_argument("-l", "--lpmln", default=False)
    parser.add_argument("-s", "--sentence", default='')
    parser.add_argument("-t", "--test_predicate", default='sample_case')
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
        fact_checker(sentences_list, id_list, true_labels, args.test_predicate)
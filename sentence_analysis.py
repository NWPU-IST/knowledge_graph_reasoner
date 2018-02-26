from nltk.tag import StanfordNERTagger,StanfordPOSTagger
# from nltk.parse.stanford import StanfordDependencyParser
import os, sys
from itertools import groupby
from nltk import word_tokenize
from StanfordOpenIEPython.main import stanford_ie
import argparse
from re import sub
from config import aux_verb
import csv

# stanford_parser_jar = str(os.environ['HOME'])+'/stanford-parser-full-2015-12-09/stanford-parser.jar'
# stanford_model_jar = str(os.environ['STANFORDTOOLSDIR'])+'/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar'

# st_ner = StanfordNERTagger('english.muc.7class.distsim.crf.ser.gz')
st_ner = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
# st_pos = StanfordPOSTagger('english-bidirectional-distsim.tagger')
# parser = StanfordDependencyParser(path_to_jar=stanford_parser_jar, path_to_models_jar=stanford_model_jar)


def triple_filter(ent, triples):
    triple_dict = {}
    entity_set = [x[0].encode('utf-8') for x in ent]
    if len(entity_set) < 2:
        for triple in triples:
            if triple[1].encode('utf-8') not in aux_verb:
                if entity_set[0] in triple:
                    triple_dict[triple[1]] = [[triple[0], triple[2]]]
    else:
        for triple in triples:
            if triple[1].encode('utf-8') not in aux_verb:
                key1 = [ent for ent in entity_set if ent in triple[0]]
                key2 = [ent for ent in entity_set if ent in triple[2]]
                if key1 and key2:
                    key1 = key1[0]
                    key2 = key2[0]
                    if triple[1] not in triple_dict.keys():
                        triple_dict[triple[1]] = [[key1, key2]]
                    else:
                        triple_list = [item for sublist in triple_dict[triple[1]] for item in sublist]
                        if key1 in triple_list and key2 in triple_list:
                            pass
                        else:
                            triple_dict[triple[1]].append([key1, key2])
        if not triple_dict and len(entity_set) > 2:
            for triple in triples:
                if triple[1] not in aux_verb:
                    key1 = [entity_set[0] for trip in triple if trip in entity_set[0]]
                    key2 = [entity_set[1] for trip in triple if trip in entity_set[1]]
                    if key1 and key2:
                        key1 = key1[0]
                        key2 = key2[0]
                        if triple[1] not in triple_dict.keys():
                            triple_dict[triple[1]] = [[key1, key2]]
                        else:
                            triple_list = [item for sublist in triple_dict[triple[1]] for item in sublist]
                            if key1 in triple_list and key2 in triple_list:
                                pass
                            else:
                                triple_dict[triple[1]].append([key1, key2])
    return triple_dict


def sentence_tagger(sentence_list):
    named_entities = st_ner.tag_sents(sentence_list)
    # POS_tagger = st_pos.tag_sents(sentence_list)
    # dependency_tagger = [[list(parse.triples()) for parse in dep_parse] for dep_parse in parser.parse_sents(sentence_list)]
    return named_entities


def get_nodes(tagged_words):
    ent = []
    for tag, chunk in groupby(tagged_words, lambda x:x[1]):
        if tag != "O":
            tuple1 = (sub(r'\s+([?.!,"])', r'\1', " ".join(w for w, t in chunk)), tag)
            ent.append(tuple1)
    return ent


def triples_extractor(sentence, named_entities):
    try:
        os.remove('sentences.txt')
    except:
        pass
    with open('sentences.txt', 'a') as text:
        text.write(sentence)
    triples_raw = stanford_ie("sentences.txt", verbose=False)
    # print triples_raw
    triples = [[trip.lstrip() for trip in triple] for triple in triples_raw]
    triple_dict = triple_filter(named_entities, triples)
    return triple_dict


def load_csv(csv_file):
    resources_v = []
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['sub'], row['obj'])
            resource_v = [row['sub'], row['obj']]
            resources_v.append(resource_v)
    return resources_v


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sentence", default='Bill Gates is married to Melinda Gates.')
    args = parser.parse_args()
    sentence_lis = [args.sentence]
    sentence_list = [word_tokenize(sent) for sent in sentence_lis]
    # print sentence_list
    named_tags = sentence_tagger(sentence_list)
    # print named_tags
    for ne in named_tags:
        sentence_check = sentence_lis[0]
        print sentence_check
        named_entities = get_nodes(ne)
        # print named_entities
        entity_dict = dict(named_entities)
        # print "NER: "+str(entity_dict)
        triple_dict = triples_extractor(sentence_check, named_entities)
        print "Relation Triples: "+str(triple_dict)

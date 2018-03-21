from os import path
import json
import csv
from resource_writer import json_serial


def load_files(data_source):
    if path.isfile('dataset/'+data_source+'/input/triples_raw.json'):
        with open('dataset/'+data_source+'/input/triples_raw.json') as json_data:
            file_triples = json.load(json_data)
    else:
        file_triples = {"a": "b"}

    if path.isfile('dataset/'+data_source+'/input/ambiverse_resources.json'):
        with open('dataset/'+data_source+'/input/ambiverse_resources.json') as json_data:
            ambiverse_resources = json.load(json_data)
    else:
        ambiverse_resources = {"a":"b"}

    return file_triples, ambiverse_resources


def load_kgminer_resource():
    nodes_id, edge_id = dict(), dict()
    if path.isfile('KGMiner/input_data/nodes_id.json'):
        with open('KGMiner/input_data/nodes_id.json') as json_data:
            nodes_id = json.load(json_data)
    else:
        process_input_data('KGMiner/input_data/infobox.nodes', 'KGMiner/input_data/nodes_id.json')

    if path.isfile('KGMiner/input_data/edge_types_id.json'):
        with open('KGMiner/input_data/edge_types_id.json') as json_data:
            edge_id = json.load(json_data)
    else:
        process_input_data('KGMiner/input_data/infobox.edgetypes', 'KGMiner/input_data/edge_types_id.json')
        load_kgminer_resource()
    return nodes_id, edge_id
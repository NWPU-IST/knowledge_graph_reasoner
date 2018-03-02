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
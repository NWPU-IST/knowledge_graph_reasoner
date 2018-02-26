import json
from os import remove, path
from datetime import datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


def update_resources(triple_flag, ambiverse_flag, file_triples, ambiverse_resources):
    if triple_flag:
        print "Updating Relation Triples"
        if path.isfile('dataset/' + data_source + '/triples_raw.json'):
            remove('dataset/' + data_source + '/triples_raw.json')
        with open('dataset/' + data_source + '/triples_raw.json', 'w') as fp:
            json.dump(file_triples, fp, default=json_serial)

    if ambiverse_flag:
        print "Updating Resources"
        if path.isfile('dataset/' + data_source + '/ambiverse_resources.json'):
            remove('dataset/' + data_source + '/ambiverse_resources.json')
        with open('dataset/' + data_source + '/ambiverse_resources.json', 'w') as fp:
            json.dump(ambiverse_resources, fp, default=json_serial)
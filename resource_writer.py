import json
from os import remove, path
from datetime import datetime
from config import rule_mining
import csv


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def update_resources(triple_flag, ambiverse_flag, file_triples, ambiverse_resources, lpmln_evaluation, data_source,\
                     input, const,data_size,lpmln_type):
    if triple_flag:
        print "Updating Relation Triples"
        if path.isfile('dataset/' + data_source + '/input/triples_raw.json'):
            remove('dataset/' + data_source + '/input/triples_raw.json')
        with open('dataset/' + data_source + '/input/triples_raw.json', 'w') as fp:
            json.dump(file_triples, fp, default=json_serial)

    if ambiverse_flag:
        print "Updating Resources"
        if path.isfile('dataset/' + data_source + '/input/ambiverse_resources.json'):
            remove('dataset/' + data_source + '/input/ambiverse_resources.json')
        with open('dataset/' + data_source + '/input/ambiverse_resources.json', 'w') as fp:
            json.dump(ambiverse_resources, fp, default=json_serial)

    if lpmln_evaluation:
        st = datetime.now()
        with open('dataset/' + data_source + '/output/top_set_' + const +'_' + rule_mining + '_'+str(st)+'_'+data_size+'_'+lpmln_type, 'wb') as csvfile:
            datawriter = csv.writer(csvfile)
            datawriter.writerows(lpmln_evaluation)
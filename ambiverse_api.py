import requests
import json
import spotlight
from kb_query import dbpedia_wikidata_equivalent

query_url = "https://api.ambiverse.com/v1/entitylinking/analyze"

# payload = "{\"text\" : \"Who is the CEO of Apple?\"}"
headers = {
    'content-type': "application/json",
    'accept': "application/json",
    'authorization': "Bearer 6ef8dad12d3cd996c7c843b555d3ad659fd15146"
    }


def ambiverse_entity_parser(text):
    print "ambiverse query"
    payload = '{\"text\" : \"'+text+'\", "language":"en", "coherentDocument": true}'
    response = requests.request("POST", query_url, data=payload, headers=headers)
    json_data = json.loads(response.text)
    print json_data
    entities = json_data['matches']

    resource = dict()
    for entity in entities:
        if entity.get('entity', {}):
            try:
                url = entity['entity']['url'].split('/')[-1]
                wikidata_url = entity['entity']['id'].split('/')[-1]
                confidence = entity['entity']['confidence']
            except:
                print entity
                url = ''
                confidence = 0
                wikidata_url = ''
            if '%' in url:
                url = url.replace('%20', '_')
                url = url.replace('%2C', ',')
                url = url.replace('%28', '(')
                url = url.replace('%29', ')')
                url = url.replace('%21', '!')
            resource[entity.get('text')] = {"dbpedia_id": url, "confidence": confidence, "wikidata_id": wikidata_url}
    return resource


def spotlight_entity_parser(text):
    responses = spotlight.annotate('http://localhost:2222/rest/annotate',text)
    resource = dict()
    for response in responses:
        json_data = response
        types = json_data.get('types','')
        if types:
            url = json_data.get('URI','')
            confidence = json_data.get('similarityScore', 0)
            wikidata_url = dbpedia_wikidata_equivalent(url)
            wikidata_url = wikidata_url[0][0].split('/')[-1]
            dbpedia_url = url.split('/')[-1]
            resource[json_data.get('surfaceForm','')] = {'dbpedia_id': dbpedia_url,'wikidata_id':wikidata_url, 'confidence':confidence}
    return resource



if __name__ == '__main__':
    ambiverse_resources = {'a': 'b'}
    # resource = ambiverse_entity_parser("Jonas Salk attended Clark University.")
    # print resource
    # print(len(resource))
    resource = spotlight_entity_parser('Jonas Salk attended Clark University.')
    print resource
    print(len(resource))


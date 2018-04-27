# -*- coding: utf-8 -*-

import sparql
from config import sparql_dbpedia, unwanted_predicates

suffixes_dbpedia_0 = '?p rdfs:label ?pl . FILTER langMatches( lang(?pl), "EN" ) .'

sparql_endpoint = sparql_dbpedia


def distance_one_query(id1, distance_one):
    query = (' SELECT distinct ?p ?id2 WHERE { <http://dbpedia.org/resource/' + id1 + '> ?p ?id2\
     . ' + suffixes_dbpedia_0 + ' FILTER (!regex(str(?pl), "Wikipage","i")) . FILTER (!regex(str(?pl), \
     "abstract","i")) . }')
    query_date = (' SELECT distinct ?p ?id2 WHERE { <http://dbpedia.org/resource/' + id1 + '> ?p ?id2\
     . ' + suffixes_dbpedia_0 + ' FILTER (!regex(str(?pl), "Wikipage","i")) . FILTER (!regex(str(?pl), \
     "abstract","i")) . FILTER (!regex(str(?pl), "Date","i")). FILTER (!regex(str(?pl), "Year","i"))}')
    try:
        result = sparql.query(sparql_endpoint, query)
        q1_values = [sparql.unpack_row(row_result) for row_result in result]
        # print query
    except:
        result = sparql.query(sparql_endpoint, query_date)
        q1_values = [sparql.unpack_row(row_result) for row_result in result]
        # print query_date
    if q1_values:
        for vals in q1_values:
            vals_0 = vals[0].split('/')[-1]
            if vals_0 not in unwanted_predicates:
                if isinstance(vals[1], basestring):
                    if '/' in vals[1]:
                        distance_one.append([id1, vals_0, vals[1].split('/')[-1]])
                    else:
                        distance_one.append([id1, vals_0, vals[1]])
    return distance_one


def distance_two_query(entity, distance_two):
    query = ' SELECT distinct ?p ?id2 ?p1 ?id3 WHERE { <http://dbpedia.org/resource/' + entity + '> ?p ?id2 . ?id2 ?p1 \
    ?id3 . FILTER (!regex(str(?p1), "owl","i")) . FILTER (!regex(str(?p1),"type","i")) . \
    FILTER (!regex(str(?p1),"comment","i")) . FILTER (!regex(str(?p1),"seeAlso","i")) . \
    FILTER (!regex(str(?p1),"label","i")) . FILTER (!regex(str(?p1),"caption","i")) . \
    FILTER (!regex(str(?p1),"homepage","i")) . FILTER (!regex(str(?p1),"name","i")). \
    FILTER (!regex(str(?p1),"color","i")) .}'
    try:
        result = sparql.query(sparql_endpoint, query)
        q1_values = [sparql.unpack_row(row_result) for row_result in result]
        # print query
    except:
        q1_values = []
    if q1_values:
        for vals in q1_values:
            vals_0 = vals[0].split('/')[-1]
            vals_2 = vals[2].split('/')[-1]
            if vals_0 not in unwanted_predicates:
                if not isinstance(vals[1], basestring):
                    distance_two.append([entity, vals_0, vals[1]])
                else:
                    distance_two.append([entity, vals_0, vals[1].split('/')[-1]])
            if vals_2 not in unwanted_predicates:
                if not isinstance(vals[3], basestring) and not isinstance(vals[1], basestring):
                    distance_two.append([vals[1], vals_2, vals[3]])
                elif isinstance(vals[3], basestring) and not isinstance(vals[1], basestring):
                    distance_two.append([vals[1], vals_2, vals[3].split('/')[-1]])
                elif not isinstance(vals[3], basestring) and isinstance(vals[1], basestring):
                    distance_two.append([vals[1].split('/')[-1], vals_2, vals[3]])
                else:
                    distance_two.append([vals[1].split('/')[-1], vals_2, vals[3].split('/')[-1]])
    return distance_two


def dbpedia_wikidata_equivalent(dbpedia_url):
    query = 'PREFIX owl:<http://www.w3.org/2002/07/owl#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> SELECT \
    ?WikidataProp WHERE { <'+dbpedia_url+'>  owl:sameAs ?WikidataProp . FILTER (CONTAINS \
    (str(?WikidataProp) , "wikidata.org")) .} '
    result = sparql.query(sparql_dbpedia, query)
    resources = [sparql.unpack_row(row_result) for row_result in result]
    return resources

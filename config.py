


aux_verb = ['was', 'is', 'become', 'to', 'of', 'in', 'the', 'for', 'where', 'etc']

unwanted_predicates = [u'thumbnail', u'person function', u'c',u'b',u's',u'n',u'v',u'mw', u'Caption', u'collapsible', u'd', u'q', u'signature',\
                       u'signature alt', u'species', u'voy', u'wikt', u'Guests', u'align', u'image', u'image caption',\
                       u'image size', u'logo', u'logo size',u'22-rdf-syntax-ns#type','soundRecording','rdf-schema#seeAlso',u'point',\
                       'endowment','rdf-schema#label','owl#differentFrom','description','filename','name','givenName', u'viafId',\
                       u'utcOffset','title','termPeriod',u'homepage','nick','rdf-schema#subClassOf','owl#unionOf']

top_k = 30
rule_mining = "amie"
# rule_mining = "rudik"
# rule_type = "hard"
rule_type = "soft"
dbpedia = 'local'
# dbpedia = 'api'
# sparql_dbpedia = 'http://dbpedia.org/sparql'
sparql_dbpedia = 'http://localhost:8890/sparql'
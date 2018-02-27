# knowledge_graph_reasoner
knowledge graph completion with reasoning

Execution Example:
1 Bill Clinton is married to Hillary Clinton. 

NER: {u'Bill Clinton': u'PERSON', u'Hillary Clinton': u'PERSON'}
Relation Triples: {'is married to': [['Bill Clinton', 'Hillary Clinton']]}

Ambiverse Resource Ids(DBpedia/Wikidata)(https://www.ambiverse.com/):
{u'Bill Clinton': {u'confidence': 1.0,
                   u'dbpedia_id': u'Bill_Clinton',
                   u'wikidata_id': u'Q1124'},
 u'Hillary Clinton': {u'confidence': 0.941563682522518,
                      u'dbpedia_id': u'Hillary_Clinton',
                      u'wikidata_id': u'Q6294'}}
                      
Logical Rules from AMIE/RUDIK:
0.9 spouse(A,B) :- spouse(B,A).
0.6 spouse(A,C) :- child(A,B) , parent(B,C) .
0.5 spouse(A,C) :- child(A,B) , child(C,B).
0.5 spouse(C,A) :- placeOfBurial(A,B) , restingPlace(C,B) .
0.4 spouse(A,C) :- child(A,B), relation(B,C) .

Evidence:
child("Bill_Clinton","Chelsea_Clinton").
child("Virginia_Clinton_Kelley","Bill_Clinton").
child("Jeff_Dwire","Bill_Clinton").
child("Roger_Clinton_Sr.","Bill_Clinton").
parent("Chelsea_Clinton","Bill_Clinton").
child("Hillary_Clinton","Chelsea_Clinton").
child("Dorothy_Howell_Rodham","Hillary_Clinton").
child("Hugh_E._Rodham","Hillary_Clinton").
parent("Chelsea_Clinton","Hillary_Clinton").

Output Using LPMLN2ASP(http://reasoning.eas.asu.edu/lpmln/Tutorial.html):
spouse('Bill_Clinton', 'Hillary_Clinton') 0.821829082107


Setup-Requirements:
Setting up the Stanford NLP:
1.Download the NLP Packages:
wget http://nlp.stanford.edu/software/stanford-ner-2015-12-09.zip
wget http://nlp.stanford.edu/software/stanford-postagger-full-2015-12-09.zip
wget http://nlp.stanford.edu/software/stanford-parser-full-2015-12-09.zip

2.Unzip Them
unzip stanford-ner-2015-12-09.zip
unzip stanford-parser-full-2015-12-09.zip
unzip stanford-postagger-full-2015-12-09.zip

3.Setting up Stanford-OpenIE for Relation Triples:
git clone https://github.com/philipperemy/Stanford-OpenIE-Python.git
cd Stanford-OpenIE-Python/
mv stanford-openie/ ../
make __init__.py

5.download nltk punkt

6. Setting up NLP Paths
export STANFORDTOOLSDIR=$HOME
export CLASSPATH=$STANFORDTOOLSDIR/stanford-ner-2015-12-09/stanford-ner.jar:$STANFORDTOOLSDIR/stanford-postagger-full-2015-12-09:$STANFORDTOOLSDIR/stanford-parser-full-2015-12-09/stanford-parser.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar:$STANFORDTOOLSDIR/stanford-openie/stanford-openie.jar

export STANFORD_MODELS=$STANFORDTOOLSDIR/stanford-ner-2015-12-09/classifiers:$STANFORDTOOLSDIR/stanford-postagger-full-2015-12-09/models:$STANFORDTOOLSDIR/stanford-openie/stanford-openie-models.jar

7. Setting up Virtuoso and local DBpedia:
http://kbreasoning.blogspot.com/2017/12/setting-up-local-dbpediawikidata-with.html


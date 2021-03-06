from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, SKOS, FOAF
import csv
import uuid
import json
import os

def addBindings(graph):
    graph.bind("arches", ARCHES)
    graph.bind("skos", SKOS)
    graph.bind("dcterms", DCTERMS)
    return graph
    

def getThesaurusFromXML(xml_file):
    '''parses an xml rdf file and returns the uuid of the ConceptScheme,
as well as the graph itself so more top concepts can be added to it.
'''
    
    g = Graph()
    scheme_graph = g.parse(xml_file)
    scheme_graph = addBindings(scheme_graph)
    
    schemes = []
    for s, v, o in g.triples((None, RDF.type , SKOS.ConceptScheme)):
        schemes.append(s)
    if len(schemes) > 1:
        raise Exception("these tools will only work with single-scheme files")

    scheme_id = schemes[0].split("/")[-1]
    return scheme_graph,scheme_id

def makeNewThesaurus(thesaurus_name):

    rdf_graph = Graph()
    rdf_graph = addBindings(rdf_graph)

    ## make thesaurus concept scheme
    thesaurus_id = str(uuid.uuid4())
    if mock_uuids:
        thesaurus_id = "THESAURUS - UUID"
    thesaurus_name = json.dumps({'value': new_thesaurus_name, 'id': str(uuid.uuid4())})

    rdf_graph.add((ARCHES[thesaurus_id], DCTERMS.title, Literal(thesaurus_name, lang=language)))
    rdf_graph.add((ARCHES[thesaurus_id], RDF.type, SKOS['ConceptScheme']))

    return rdf_graph,thesaurus_id

def makeTopConcept(rdf_graph,top_concept_name,thesaurus_id):
    
    topconcept_id = str(uuid.uuid4())
    if mock_uuids:
        topconcept_id = "TOP CONCEPT - UUID ({})".format(top_concept_name)
        
    content = json.dumps({'value': top_concept_name, 'id': str(uuid.uuid4())})

    rdf_graph.add((ARCHES[topconcept_id], RDF.type, SKOS['Concept']))
    rdf_graph.add((ARCHES[topconcept_id], SKOS['prefLabel'], Literal(content, lang=language)))
    rdf_graph.add((ARCHES[topconcept_id], SKOS.inScheme, ARCHES[thesaurus_id]))
    rdf_graph.add((ARCHES[thesaurus_id], SKOS['hasTopConcept'], ARCHES[topconcept_id]))

    return rdf_graph, topconcept_id

def makeConceptsFromCSV(rdf_graph,csvfile,scheme_id,collection_graph,header_row=False,
                        label_col=0,alpha_sort=False,uuid_col=False):

    ## make top concept
    top_concept_name = os.path.splitext(os.path.basename(csvfile))[0]
    rdf_graph, topconcept_id = makeTopConcept(rdf_graph,top_concept_name,scheme_id)

    unique_labels = []
    labels_uuids = {}
    with open(csvfile,"rb") as csvopen:
        reader = csv.reader(csvopen)
        if header_row:
            reader.next()
        for r in reader:
            label = r[label_col]
            if not label in unique_labels:
                unique_labels.append(label)
            else:
                continue
            if mock_uuids:
                uu = "CONCEPT - UUID ({})".format(label)
            else:
                if uuid_col:
                    uu = r[uuid_col]
                else:
                    uu = str(uuid.uuid4())
            labels_uuids[label]=uu

    if alpha_sort:
        unique_labels.sort()

    print os.path.basename(csvfile)
    print " ",len(unique_labels),"concepts will be made"

    ## iterate file contents and make concepts
    ## in EVERY case a sortorder is added to the concept. the order is based
    ## on the unique_labels list
    for sortorder,label in enumerate(unique_labels):
        
        concept_id = labels_uuids[label]
        val = json.dumps({'value': label, 'id': str(uuid.uuid4())})

        so_str = str(sortorder)
        so_str_pad = "{}{}".format("0"*(3-len(so_str)),so_str)
        so = json.dumps({'value': so_str_pad, 'id': str(uuid.uuid4())})
        
        rdf_graph.add((ARCHES[concept_id], SKOS.inScheme, ARCHES[scheme_id]))
        rdf_graph.add((ARCHES[concept_id], SKOS['prefLabel'], Literal(val, lang=language)))
        rdf_graph.add((ARCHES[concept_id], ARCHES['sortorder'], Literal(so, lang=language)))
        rdf_graph.add((ARCHES[concept_id], RDF.type, SKOS['Concept']))
        rdf_graph.add((ARCHES[topconcept_id], SKOS['narrower'], ARCHES[concept_id]))

    collection_graph = addCollection(collection_graph,top_concept_name,labels_uuids.values(),collection_graph)

    return rdf_graph,collection_graph

def addCollection(g,name,conceptids,xml_file=False):
 
    collection_id = str(uuid.uuid4())
    val = json.dumps({'value': name, 'id': str(uuid.uuid4())})
    g.add((ARCHES[collection_id], RDF.type, SKOS['Collection']))
    g.add((ARCHES[collection_id], SKOS['prefLabel'], Literal(val, lang=language)))

    for c in conceptids:
        g.add((ARCHES[collection_id], SKOS['member'], ARCHES[c]))
        g.add((ARCHES[c], RDF.type, SKOS['Concept'])) 

    return g
    
## create some variables for the RDF contents
ARCHES = Namespace('http://www.archesproject.org/')
language = 'en'
new_thesaurus_name = "FPAN-HMS"

## enable mock_uuids to make easier to recognize identifiers that are used
## throughout the output file. setting mock_uuids to True will NOT result in
## a valid thesaurus file
mock_uuids = False

## create output location variables
outdir = os.path.join(os.path.dirname(os.path.dirname(__file__)),"reference_data")
thesaurusfile = os.path.join(outdir,r"FPAN-thesaurus.xml")
collectionfile = os.path.join(outdir,"FPAN-collections.xml")

## create input location variable
csvdir = os.path.join("examplecsvs","csvswithuuids")

## if you want, everything could be added to an existing thesaurus xml
## this may not be desirable outside of testing
## otherwise, make a new thesaurus (existing files will be overwritten)
use_existing_thesaurus = False
use_existing_thesaurus_path = ''

if use_existing_thesaurus:
    rdf_graph,thesaurus_id = getThesaurusFromXML(use_existing_thesaurus_path)
else:
    rdf_graph,thesaurus_id = makeNewThesaurus(new_thesaurus_name)

## list of file names whose contents should be sorted alphabetically
sort_these_alphabetically = [
    "Site Type.csv",
    "Structure Use.csv",
    "Style.csv",
]

## set some basic config options for this particular set of CSV files
## if you don't have UUIDs in your files, set uuid_col to False
## a new concept will be made for each unique entry in the label column
config = {
    'alpha_sort':False,
    'uuid_col':-1,
    'label_col':2,
    'header_row':False
}

collection_graph = Graph()
collection_graph = addBindings(collection_graph)

## iterate all csv files and create a new top concept and collection from
## each file
for f in [i for i in os.listdir(csvdir) if i.endswith(".csv")]:
    
    csv_conf = config
    csv_conf['alpha_sort'] = f in sort_these_alphabetically

    csvfilepath = os.path.join(csvdir,f)
    rdf_graph,collection_graph = makeConceptsFromCSV(rdf_graph,csvfilepath,thesaurus_id,
            collection_graph,
            alpha_sort=csv_conf['alpha_sort'],
            label_col=csv_conf['label_col'],
            uuid_col=csv_conf['uuid_col'],
            header_row=csv_conf['header_row'])

collection_graph.serialize(destination=collectionfile,format="pretty-xml")
rdf_graph.serialize(destination=thesaurusfile,format="pretty-xml")
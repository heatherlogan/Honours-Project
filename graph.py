from py2neo import Graph, Node, Relationship, NodeMatcher
from pubmed_parse import *
import itertools
from main import main_main
from ontology_stuff import build_onto_objects

from analyse import *

def graph_relations(relations):

    graph = Graph("http://localhost:7474/db/data/", user="neo4j", password="piggybank13")

    matcher = NodeMatcher(graph)

    all_terms = []
    for t1, relation, t2 in relations:
        all_terms.append(t1)
        all_terms.append(t2)

    all_terms = list(set(all_terms))
    print((all_terms))

    for i, term in enumerate(all_terms):
        label, type = term[0], term[1]

        print(label, type)
        if label and type:
            graph.create(Node(type, name=label))

    for t1, relation, t2 in relations:
        t1_label, t1_type = t1[0], t1[1]
        t2_label, t2_type = t2[0], t2[1]

        node1 = matcher.match(t1_type, name=t1_label).first()
        node2 = matcher.match(t2_type, name=t2_label).first()
        rel = Relationship(node1, relation, node2)
        print(i, rel)
        graph.create(rel)


def get_obj(classno):
    return next((x for x in onto_objects if x.classnum == classno), None)

def get_descendants(obj):
    return [get_obj(str(x).replace('asdpto.', '')).label for x in obj.descendants()]


def get_group(tag):

    out = ""

    group_labels = {
    'Comorbidities': get_descendants(get_obj('Class_365')) + ["'Comorbidities'"],
    'Complaints and indications' :get_descendants(get_obj('Class_406')) + ["'Complaints and Indications'"],
    'Diagnosis': get_descendants(get_obj('Class_97'))+ ["'Diagnosis'"],
    'Exposures': get_descendants(get_obj('Class_148'))+ ["'Exposures'"],
    'Perinatal History': get_descendants(get_obj('Class_385')) + ["'Perinatal History'"],
    'Cognitive Abilties': get_descendants(get_obj('Class_158')) + ["'Cognitive Abilities'"],
    'Emotional Traits': get_descendants(get_obj('Class_160')) + ["'Emotional Traits'"],
    'Executive Function': get_descendants(get_obj('Class_155')) + ["'Executive Function'"],
    'Language Ability': get_descendants(get_obj('Class_156')) + ["'Language Ability'"],
    'Stereotyped, Restricted and Repetitive Behaviours': get_descendants(get_obj('Class_166')) + ["'Stereotyped, Restricted, and Repetitive Behavior'"],
    'Adaptive Life Skills': get_descendants(get_obj('Class_538')) + ["'Adaptive Life Skills'"],
    'Interpersonal Interactions': get_descendants(get_obj('Class_283')) + ["'Interpersonal Interactions'"],
    'Recognition of Social Norms': get_descendants(get_obj('Class_66')) + ["'Recognition of Social Norms'"],
    }

    for label, descendants in group_labels.items():
        if tag in [d.replace(" ", "_").replace("'", "").replace(",", '').lower() for d in descendants]:
            out = label
            break
    return out



def format_relations():

    relations = []
    syns = get_synonyms()

    relation_file = open('files/system_output/final_re.txt', 'r').readlines()

    for line in relation_file:
        line = line.strip()
        arg1_tag = ""
        arg2_tag = ""
        if line.startswith("("):
            line2 = line.strip().replace(')', '').replace('(', '').replace("'", '')
            arg1, rel, arg2 = line2.split(', ')
            for gene, synonyms in syns.items():
                for arg in arg1.split():
                    if arg.upper() in synonyms:
                        arg1 = gene
                        arg1_tag = "Gene"
                        break
                for arg in arg2.split():
                    if arg.upper() in synonyms:
                        arg2 = gene
                        arg2_tag = "Gene"
                        break

            if arg1_tag == "":
                pheno_map = main_main(arg1)
                if len(pheno_map)>0:
                    arg1 = pheno_map[0][1]
                    arg1_tag = get_group(arg1)
            if arg2_tag == "":
                pheno_map = main_main(arg2)
                if len(pheno_map) > 0:
                    arg2 = pheno_map[0][1]
                    arg2_tag = get_group(arg2)

        if arg1_tag != '' and arg2_tag != '':
            relation = ((arg1, arg1_tag), rel.replace(' ', '_'), (arg2, arg2_tag))
            relations.append(relation)

    return relations


onto_objects = build_onto_objects()


if __name__ == "__main__":

    relations_ex = []
    relations = format_relations()
    full_relations = []
    graph_relations(full_relations)
    syns = get_synonyms()
    sfari_genes = [x.upper() for x in list(itertools.chain.from_iterable((syns.values())))]
    # graph_relations(relations)


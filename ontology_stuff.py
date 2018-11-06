from owlready2 import *
from search import *

# owlready doc: https://media.readthedocs.org/pdf/owlready2/latest/owlready2.pdf

# uses ontology no

onto = get_ontology("file:///Users/heatherlogan/PycharmProjects/Honours_Proj/files/asdpto.owl").load()

onto_objects = []
leaf_nodes = []

class Node:
    def __init__(self, classnum, label, definition, ancestors):
        self.classnum = classnum
        self.label = label
        self.definition = definition
        self.ancestors = ancestors


def get_queries():

    query_list = []
    count = 0

    for c in onto.classes():

        iri = onto.base_iri + c.name
        label = str(IRIS[iri].label)
        definition = str(IRIS[iri].definition)

        string = (label + "\n" + definition)
        count += 1
        query = str(count) + " " + (re.sub('([^\s\w]|_)+', '', string))
        query_list.append(query)

    return query_list


def build_onto_objects():

    for c in onto.classes():

        descendants = []
        ancestors = []

        iri = onto.base_iri + c.name
        label = str(IRIS[iri].label)
        definition = str(IRIS[iri].definition)
        ancestors.append([a for a in c.ancestors()])

        node = Node(c.name, label, definition, c.ancestors)

        for d in c.descendants():
            descendants.append(str(d))
        if len(descendants)==1:
            leaf_nodes.append(node)




def check_nums():

    # just for counting major branches leading to leaf nodes

    build_onto_objects()

    comorbities = []
    complaints = []
    diagnosis = []
    exposures = []
    perinatal_history = []

    cognitive = []
    emotional = []
    execfunct = []
    language = []
    motorskills = []
    behav =[]

    lifeskills = []
    interpersonal = []
    socialnorms = []

    for node in leaf_nodes:
        for a in node.ancestors():
            if str(a) == 'asdpto.Class_365':
                comorbities.append(node)
            if str(a) == 'asdpto.Class_406':
                complaints.append(node)
            if str(a) == 'asdpto.Class_97':
                diagnosis.append(node)
            if str(a) == 'asdpto.Class_148':
                exposures.append(node)
            if str(a) == 'asdpto.Class_385':
                perinatal_history.append(node)

            if str(a) == 'asdpto.Class_158':
                cognitive.append(node)
            if str(a) == 'asdpto.Class_160':
                emotional.append(node)
            if str(a) == 'asdpto.Class_155':
                execfunct.append(node)
            if str(a) == 'asdpto.Class_156':
                language.append(node)
            if str(a) == 'asdpto.Class_753':
                motorskills.append(node)
            if str(a) == 'asdpto.Class_166':
                behav.append(node)

            if str(a) == 'asdpto.Class_538':
                lifeskills.append(node)
            if str(a) == 'asdpto.Class_283':
                interpersonal.append(node)
            if str(a) == 'asdpto.Class_66':
                socialnorms.append(node)

    print(len(comorbities))
    print(len(complaints))
    print(len(diagnosis))
    print(len(exposures))
    print(len(perinatal_history))
    print('\n')
    print(len(cognitive))
    print(len(emotional))
    print(len(execfunct))
    print(len(language))
    print(len(motorskills))
    print(len(behav))
    print('\n')
    print(len(lifeskills))
    print(len(interpersonal))
    print(len(socialnorms))


def search_ontology(name):
    pass


if __name__=='__main__':

    # queries = get_queries()

    check_nums()





    # query_idx(queries)
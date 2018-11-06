from owlready2 import *
from search import *

# owlready doc: https://media.readthedocs.org/pdf/owlready2/latest/owlready2.pdf

# uses ontology no

onto = get_ontology("file:///Users/heatherlogan/PycharmProjects/Honours_Proj/files/asdpto.owl").load()


class Node:

    def __init__(self, classnum, label, definition, parent, ancestors, descendants):
        self.classnum = classnum
        self.label = label
        self.definition = definition
        self.parent = parent
        self.ancestors = ancestors
        self.descendants = descendants


def get_queries():

    query_list = []
    count = 0

    for c in onto.classes():

        iri = onto.base_iri + c.name
        label = str(IRIS[iri].label)
        definition = str(IRIS[iri].definition)

        string = (label + "\n" + definition)
        count += 1
        query = str(count) + " " + string
        query_list.append(query)

    return query_list


def build_onto_objects():

    onto_objects = []

    for c in onto.classes():

        descendants = []
        ancestors = []

        iri = onto.base_iri + c.name
        label = (re.sub('([^\s\w]|_)+', '', str(IRIS[iri].label))).strip()
        definition = (re.sub('([^\s\w]|_)+', '', str(IRIS[iri].definition))).strip()
        ancestors.append([a for a in c.ancestors()])
        parent = c.is_a

        node = Node(c.name, label, definition, parent, ancestors, c.descendants)
        onto_objects.append(node)

    return onto_objects


def get_leaf_nodes():

    onto_objects = build_onto_objects()
    leaf_nodes = []

    for node in onto_objects:
        str_descendants = []
        for d in node.descendants():
            str_descendants.append(str(d))
        if (len(str_descendants)) == 1:
            leaf_nodes.append(node)

    return leaf_nodes


def search_ontology(name):
    pass


if __name__=='__main__':

    # queries = get_queries()
    print(len(get_leaf_nodes()))

    # query_idx(queries)
from owlready2 import *
from nltk.corpus import stopwords

# owlready doc: https://media.readthedocs.org/pdf/owlready2/latest/owlready2.pdf

onto = get_ontology("file:///Users/heatherlogan/PycharmProjects/Honours_Proj/files/asdpto.owl").load()

stopwords = list(set(stopwords.words('english')))

class Node:

    def __init__(self, classnum, label, definition, parent, ancestors, descendants):
        self.classnum = classnum
        self.label = label
        self.definition = definition
        self.parent = parent
        self.ancestors = ancestors
        self.descendants = descendants


def build_onto_objects():

    onto_objects = []

    for c in onto.classes():

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


def preprocess_query(query):

    preprocessed = []

    tokenized_text = list(filter(None, re.split('[\W]', query)))
    for word in tokenized_text:
        word = word.lower()
        if word not in stopwords:
            preprocessed.append(word)

    return " ".join(preprocessed)



def get_queries():

    query_list = []

    for node in get_leaf_nodes():

        query = preprocess_query(node.label + " " + node.definition)

        query_list.append(node.classnum + ": " + query)

    return query_list



if __name__=='__main__':

    queries = get_queries()



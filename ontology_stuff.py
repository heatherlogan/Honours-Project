from owlready2 import *
from search import *

# owlready doc: https://media.readthedocs.org/pdf/owlready2/latest/owlready2.pdf

# uses ontology no

onto = get_ontology("file:///Users/heatherlogan/PycharmProjects/Honours_Proj/files/asdpto.owl").load()


def get_ontology():

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


if __name__=='__main__':

    queries = get_ontology()

    query_idx(queries)
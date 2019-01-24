import pymedtermino
from owlready2 import *
from nltk.corpus import stopwords, wordnet
from nltk.stem import snowball, WordNetLemmatizer
from named_entity_recognition import *
from pymedtermino.all import *
from pymedtermino import *
from pymedtermino.snomedct import *

# owlready doc: https://media.readthedocs.org/pdf/owlready2/latest/owlready2.pdf

onto = get_ontology("file:///Users/heatherlogan/PycharmProjects/Honours_Proj/files/asdpto.owl").load()

pymedtermino.LANGUAGE = "en"
pymedtermino.REMOVE_SUPPRESSED_CONCEPTS = True

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
        label = (re.sub('[][]', '', str(IRIS[iri].label))).strip()
        definition = (re.sub('[][]', '', str(IRIS[iri].definition))).strip()
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

    query_list = {}
    objs = build_onto_objects()

    for node in get_leaf_nodes():

        parent = next(x for x in objs if x.classnum == re.sub("asdpto.","", str(node.parent[0])))

        query = preprocess_query(parent.label + " " + node.label + " " + node.definition)

        query_list[node.label] = (query)

    return query_list

def entity_extract2(sentence, pattern):

    if pattern=='default':
        pattern = r""" Ents: {[0-9]*<JJ>*(<NN>|<NNS>|<NNP>)+}"""

    named_ents = {}

    r = sentence.split()
    pos_s = nltk.pos_tag(r)
    chunkParser = nltk.RegexpParser(pattern)
    chunked = chunkParser.parse(pos_s)

    for chunk in chunked:
        string = []
        if type(chunk) != tuple:
            [string.append(term) for term, tag in chunk]
        if string:
            string = " ".join(string)
            if ',' in string:
                strs = string.split(',')
                for s in strs:
                    named_ents[s.strip()] = []
            else:
                named_ents[string.strip()] = []

    return named_ents


def extract_autism_entities():

    file = open("files/asdpto_ents.txt", 'w')

    onto_objects = build_onto_objects()

    medical_entities = []
    onto_titles = []
    #
    #
    return [onto.label.replace("'", "") for onto in onto_objects]
    # #
    # #     [medical_entities.append(onto) for a in onto.ancestors for  i in a if str(i) == "asdpto.Class_154"]
    # #
    #     entities = entity_extract2(onto.definition, 'default')
    #     entities = filter(None, entities)
    #
    #     file.write("{}\n".format(re.sub("'", '', "".join([o.lower() for o in onto.label]))))
    #
    #     for entity in entities:
    #         entity = re.sub(r'([^\s\w]|_)+',' ',  entity)
    #         file.write("{}\n".format(entity.lower().strip()))
    #     file.write("\n")
    #
    # file.close()

if __name__=="__main__":

    file = open('files/asdpto_ents.txt', 'r').readlines()
    file2 = open('files/asdpto_ents2.txt', 'w')

    autism_ents = []
    autism_ents.append([x.strip() for x in file])

    autism_ents = sorted(list(set(filter(None, autism_ents[0]))))

    for ent in autism_ents:
        file2.write('{}\n'.format(ent))



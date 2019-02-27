from owlready2 import *
from NER import *
from nltk import ngrams
from nltk.stem import PorterStemmer
# owlready doc: https://media.readthedocs.org/pdf/owlready2/latest/owlready2.pdf

onto = get_ontology("file:///Users/heatherlogan/PycharmProjects/Honours_Proj/files/asdpto.owl").load()

lemmatiz = WordNetLemmatizer()

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
    seen_classes = []

    for c in onto.classes():

        if c not in seen_classes:

            ancestors = []

            iri = onto.base_iri + c.name
            label = (re.sub('[][]', '', str(IRIS[iri].label))).strip()
            definition = (re.sub('[][]', '', str(IRIS[iri].definition))).strip()
            ancestors.append([a for a in c.ancestors()])
            parent = c.is_a

            node = Node(c.name, label, definition, parent, ancestors, c.descendants)
            onto_objects.append(node)

        seen_classes.append(c)

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


def extract_autism_entities():

    file = open("files/asdpto_ents.txt", 'w')

    onto_objects = list(set(build_onto_objects()))
    for object in onto_objects:
        keywords = []
        phrases = []
        label = re.sub(r'([^\s\w]|_)+', '', object.label.lower())
        phrases.append(label)
        label2 = [o for o in label.split() if o not in stopwords]
        bigram_label = ngrams(label2, 2)
        ents = [k for k,v  in entity_extract(object.definition.lower(), 'default').items()]
        pos_tags = nltk.pos_tag(ents)
        keyword_POS = ('NN', "NNS")

        for p in pos_tags:
            if p[1] in keyword_POS:
                keywords.append(p[0].strip())

        for b in bigram_label:
            ptag = nltk.pos_tag([' '.join(b).strip()])
            if ptag[0][1] in keyword_POS:
                phrases.append(ptag[0][0].strip())

        file.write("{}\n{}\n".format(object.classnum, object.label))

        for k in sorted(keywords):
            file.write("\t{}\n".format(k))

        for ph in sorted(list(set(phrases))):
            file.write('\t{}\n'.format(ph))

        file.write('\n')
    file.close()


if __name__=="__main__":

    file = open("files/autism_terms/social_sub_ents.txt", 'w')

    onto_objects = build_onto_objects()
    social_ents = []

    for onto in onto_objects:

        [social_ents.append(onto) for a in onto.ancestors for i in a if str(i) == "asdpto.Class_153"]

    for m in social_ents:
        file.write('{}: {}\n{}\n\n\n\n'.format(m.classnum, m.label, m.definition))
        print(m.classnum, m.label)

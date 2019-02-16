import re
from collections import defaultdict, Counter
from nltk.parse.stanford import StanfordDependencyParser

class_path = "/Users/heatherlogan/Desktop/stanford-parser-full-2018-10-17/stanford-parser.jar"
models_path = "/Users/heatherlogan/Desktop/stanford-english-corenlp-2018-02-27-models.jar"


def sort_relations():

    file = open("files/semantics/semantic_network_relations.txt", 'r').readlines()
    acronym_file = open('files/semantics/semantic_types.txt', 'r').readlines()

    acronym = {}

    for line in acronym_file:
        ac, code, full = line.strip().split("|")
        acronym[full] = ac

    umls_relations = defaultdict(list)
    term_rel = defaultdict(list)

    for line in file:

        line = line[:-2]
        term1, relation, term2 = line.split('|')
        umls_relations[relation].append((term1, term2))
        term_rel[term1].append(relation)

    for relation, tup_list in umls_relations.items():
        term_relation = defaultdict(list)
        for tup in tup_list:
            term_relation[tup[0]].append(tup[1])

        for key, val in term_relation.items():
            # for v in val:
            #     print(key, relation, v)
            term_rel[key].append((relation, val))

    for term, items in term_rel.items():
        print("{}:  {}".format(term, acronym[term]))
        for item in items:
            if type(item)==tuple:
                print('\t', item[0])
                print('\t\t', item[1])



if __name__=="__main__":

    # example sentences

    text = "CHUNK1 is caused by a CHUNK2 that involves CHUNK4, CHUNK5 and CHUNK6."
    text2 = "Given that autism has been suggested to involve deficits in cognitive empathy"
    text1 = "Given that ENTITY1 has been suggested to involve ENTITY2 in ENTITY3"
    texts = "Research has linked Mirror-Touch Synaesthesia with enhanced empathy."
    text5 = "The sigmaB-dependent promoter drives expression of yvyD under stress conditions and after glucose starvation whereas a singmaH-dependent promoter is responsible for yvyD transcription."

    dependency_parser = StanfordDependencyParser(path_to_jar=class_path, path_to_models_jar=models_path)

    result = dependency_parser.raw_parse(text5)
    dep = result.__next__()

    trips = list(dep.triples())

    for x in trips:
        print(x)

    tree = str(dep.to_dot())
    print(tree)

    print("\n\n")

    entities = ['amod', 'compound', 'dobj']

    tree_triples = []

    relations = [node for node in tree.split('\n') if '->' in node]
    for relation in relations:
        path, label = relation.split('[label="')
        start, end = path.split(' -> ')
        relation = label.replace('"]', '').strip()
        tree_triples.append((start, end, relation))

    treestobeparsed = []


    for t in tree_triples:
        print(t)

    print('\n\n')

    subject_labels = ['nsubj', 'nsubjpass']
    c = Counter(elem[2] for elem in tree_triples if elem[2] in subject_labels)
    if sum(c.values()) > 1:
        split_indices =[]
        for triple in tree_triples:
            if triple[2] in subject_labels:
                split_indices.append(tree_triples.index(triple))
        for idx in split_indices:
            if split_indices.index(idx) == 0:
                print(tree_triples[0:split_indices[1]])
            elif split_indices.index(idx) != len(split_indices)-1:
                print(tree_triples[idx-1:split_indices[idx]])
            else:
                print(tree_triples[idx:len(tree_triples)-1])
    else:
        print("Build relations as normal")



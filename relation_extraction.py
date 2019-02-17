import re
from collections import defaultdict, Counter
from nltk.parse.stanford import StanfordDependencyParser

class_path = "/Users/heatherlogan/Desktop/stanford-parser-full-2018-10-17/stanford-parser.jar"
models_path = "/Users/heatherlogan/Desktop/stanford-english-corenlp-2018-02-27-models.jar"


def format_relations():
    # takes in (subject, relation, possible effectors)
    # calculates possible combinations based on incoming and outgoing edges
    #

    pass


def build_paths(tree):
    def build(start):
        trace = [start]

        def path(inc):
            incoming = [edge[1] for edge in tree if edge[0] == inc]
            if len(incoming) == 1:
                trace.append(incoming[0])
                path(incoming[0])

        path(start)
        return trace

    for t in tree:
        print(t)

    def break_conjunctions(num, limit):
        conjunctions = [edge[1] for edge in tree if edge[2] == 'conj'
                        and int(num) <= int(edge[0]) <= int(limit)]
        return conjunctions

    def path_to_merge(num):
        merge_path = [num]

        def outgoings(n):
            return [edge for edge in tree if edge[0] == n]

        if outgoings(num):
            for outgoing in outgoings(num):
                if any([x for x in ['mod', 'aux', 'case', 'nummod', 'mark', 'acl'] if x in outgoing[2]]):
                    merge_path.append(outgoing[1])
                    path_to_merge(outgoing)
        return merge_path

    # nodes with incoming edges as nsubj or nsubjpass are potential start points

    start_subj = [edge[1] for edge in tree if 'subj' in edge[2]]

    if start_subj:

        main_relation = [edge[0] for edge in tree if edge[1] == start_subj[0]]

        outgoing_from_starts = start_subj + [edge[1] for edge in tree if edge[0] == start_subj[0]]

        all_subjs = []

        for effectee in outgoing_from_starts:
            all_ent_starters = break_conjunctions(effectee, main_relation[0])
            for start in start_subj + all_ent_starters:
                mergepath = path_to_merge(start)
                if mergepath not in all_subjs:
                    all_subjs.append(mergepath)
    else:
        main_relation = [edge[1] for edge in tree if edge[2] == 'root']


    outgoing_relation = [edge for edge in tree if edge[0] == main_relation[0]]

    possible_effectees = []

    for edge in outgoing_relation:
        if edge[2] in ['aux', 'auxpass']:
            # combine with relation
            main_relation.append(edge[1])
        if edge[2] in ['dobj', 'xcomp', 'nmod', 'amod', 'advcl', 'numod']:
            possible_effectees.append(edge[1])

    all_effectees = []
    for effectee in possible_effectees:
        all_ent_starters = break_conjunctions(effectee, len(node_lookup.keys()))
        for start in [effectee] + all_ent_starters:
            mergepath = path_to_merge(start)
            all_effectees.append(mergepath)


    # output = (subject, relation, entities)
    if not start_subj:
        all_subjs = []

    print("Subject Entities:", [x for x in all_subjs])
    print("Main Relation:", [i for i in main_relation])
    print("Effectees:", [i for i in all_effectees])

    return all_subjs, main_relation, all_effectees


if __name__ == "__main__":

    text = "Individuals with ASD showed reduced interpersonal interactions."
    text2 = "Additionally, CHUNK1 of their own CHUNK2 may lead to CHUNK3 of CHUNK4 actions"
    text3 = "Chunk's with Chunk2 showed reduced Chunk"
    text5 = "Individuals with Autism Spectrum Conditions have difficulties in " \
            "understanding and responding appropriately to others"
    text6 = "Additionally, developmental experience of their own atypical " \
            "kinematic progiles may lead to disrupted perception of others actions."

    text7 = "Autism spectrum disorders are a range of complex neurodevelopmental conditions principally characterized by " \
            "dysfunctions linked to mental development."

    text8 = "CHUNK are a CHUNK2 of CHUNK3 principally characterized by " \
            "CHUNK4 linked to CHUNK6"
    text9 = "two missense novel SNVs were found in the same child: ALDH1A3 and FOXN1."

    text10 = " Chromatin immunoprecipitation assay using Retinoid Acid Receptor B as the " \
             "immunoprecipitation target suggests RA regulation of Aldh1a3 and Foxn1 in mice."
    text11 = "CHUNK1 assay using CHUNK2 as the CHUNK3 suggests CHUNK4 of CHUNK5 and CHUNK6 in CHUNK7."
    text12= "RA regulation of Aldh1a3 and Foxn1 in mice."

    dependency_parser = StanfordDependencyParser(path_to_jar=class_path, path_to_models_jar=models_path)

    result = dependency_parser.raw_parse(text10)
    dep = result.__next__()

    trips = list(dep.triples())

    for trip in trips:
        print(trip)

    pos_tagged = {}
    for pos in trips:
        pos_tagged[pos[0][0]] = pos[0][1]
        pos_tagged[pos[2][0]] = pos[2][1]

    tree = str(dep.to_dot())

    for i in tree.split("\n"):
        print(i)

    tree_split = list(filter(None, [line.strip() for line in tree.split("\n") if line != "\n"]))

    node_lookup = {}
    nodes = [node for node in tree_split if node[0].isdigit() and '->' not in node]
    for node in nodes:
        num, label = node.split(' [label="')
        node_lookup[num] = label[label.find("(") + 1:label.find(")")]

    relations = [edge for edge in tree_split if '->' in edge]
    tree_triples = []
    for relation in relations:
        path, label = relation.split(' [label="')
        start, end = path.split(' -> ')
        relation = label.replace('"]', '').strip()
        tree_triples.append((start, end, relation))
    subject_labels = ['nsubj', 'nsubjpass']

    c = Counter(elem[2] for elem in tree_triples if elem[2] in subject_labels)
    if sum(c.values()) > 1:
        split_indices = []
        for triple in tree_triples:
            if triple[2] in subject_labels:
                split_indices.append(tree_triples.index(triple))
        for idx in split_indices:
            if split_indices.index(idx) == 0:
                # print(tree_triples[0:split_indices[1]-1])
                build_paths(tree_triples[0:split_indices[1] - 1])
                print("\n")
            elif split_indices.index(idx) != len(split_indices) - 1:
                build_paths(tree_triples[idx:split_indices[idx]])
                print("\n")
            else:
                build_paths(tree_triples[idx - 1:len(tree_triples)])
                print("\n")
    else:
        build_paths(tree_triples)

    dep.tree().draw()

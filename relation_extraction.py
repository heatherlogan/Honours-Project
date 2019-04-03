import itertools
from collections import defaultdict, Counter
from nltk.parse.stanford import StanfordDependencyParser
import nltk
from indexer import reload_corpus
from analyse import format_results
from NER import process_text, stopwords
from main import *
from relation_mapping import get_synonyms

class_path = "/Users/heatherlogan/Desktop/stanford-parser-full-2018-10-17/stanford-parser.jar"
models_path = "/Users/heatherlogan/Desktop/stanford-english-corenlp-2018-10-05-models.jar"


def format(combination, full_tree, node_lookup):

    output = []
    def node_to_text(int_list):

        txt_string = []

        # for i in range(min(int_list) - 1, max(int_list)):
        for i in sorted(int_list):
            try:
                # try as some nodes are missed in the tree
                txt_string.extend([node_lookup[str(i)]])
            except KeyError:
                pass
        return " ".join(txt_string)


    subject, relation, effector = combination

    subject_text = node_to_text(sorted([int(x) for x in subject]))
    # # if anaphor(subject_text):
    # #     subject_text = output_relations[len(output_relations) - 1][2]
    relation = sorted([int(x) for x in relation])
    relation_text = node_to_text(relation)

    if (-1 in relation and 'no ' not in relation_text and 'not ' not in relation_text): relation_text = "not_" + node_to_text(relation)
    effector_text = node_to_text(sorted([int(x) for x in effector]))

    return (subject_text, relation_text, effector_text)


def sort_combinations(subjects, relations, effectors, full_tree, node_lookup):
    # print("Subj:",subjects, "\nRelation: ", relations, "\nEffectors: ",effectors)

    combined = []

    # check negations; if negative child node attached to relation subject or entity then negate relation
    def negated(nodes):
        return any([x for x in full_tree if x[0] in
                    [i[0] for i in nodes] and x[2] == 'neg'])


    if any([i for i in relations if 'correlat' in node_lookup[i]]):
        for i, effector in enumerate(effectors):
            combined.append((effectors[i-1], relations, effectors[i]))

    for subject in subjects:
        for effector in effectors:
            if effector != subject:
                if negated(subject) or negated(effector) or negated(full_tree[0]):
                    relations.append('-1')

            # check path between subject and effectee
            combined.append((subject, relations, effector))
    formatted = []


    for comb in combined:
        formatted.append(format(comb, full_tree, node_lookup))

    return formatted


def cleanoutput(output):

    cleaned = []

    for out in output:
        e1, r, e2 = out
        e1 = e1.split()
        e2 = e2.split()
        #remove leading/ending stopwords
        if e1[0] in stopwords and len(e1)>1: e1 = e1[1:]
        if e1[-1] in stopwords and len(e1)>1: e1 = e1[:-1]
        if e2[0] in stopwords and len(e2)>1: e2 = e2[1:]
        if e2[-1] in stopwords and len(e2)>1: e2 = e2[:-1]
        e1 = ' '.join(e1)
        e2 = ' '.join(e2)
        fin = (e1, r, e2)
        cleaned.append(fin)

    return cleaned


def filteroutput(output):

    filtered_outputs = output.copy()

    for ent in output:
        e1, r, e2 = ent
        if e1==e2 or e1 in e2 or e2 in e1 or r in e1 or r in e2:
            filtered_outputs.remove(ent)
        elif not any([i.isalpha() for i in e1]) or not  any([i.isalpha() for i in e2]):
            filtered_outputs.remove(ent)
        else:
            e1_pos = nltk.pos_tag(e1.split())
            if not any([x for x in e1_pos if 'NN' in x[1]]):
                filtered_outputs.remove(ent)
            else:
                e2_pos = nltk.pos_tag(e2.split())
                if not any([x for x in e2_pos if 'NN' in x[1]]):
                    filtered_outputs.remove(ent)

    # remove duplicates with reverse e1,e2s
    final_output = filtered_outputs.copy()
    for fst,snd in itertools.combinations(filtered_outputs, 2):
        if fst==snd:
            if fst in final_output: final_output.remove(fst)
        else:
            fst_e1, fst_r, fst_e2 = fst
            snd_e1, snd_r, snd_e2 = snd
            if fst_r==snd_r:
                if fst_e1 == snd_e2 and fst_e2==snd_e1:
                    if fst in final_output: final_output.remove(fst)

    return final_output


def build_paths(tree, full_tree, node_lookup ):

    combine_relations = ['mod', 'aux', 'case', 'dep', 'det', 'case', 'cc'
                        'nummod', 'mark', 'dobj', 'nmod', 'amod', 'advmod', 'compound', 'acl', 'neg']

    effectee_dependencies = ['dobj', 'nmod', 'amod', 'advcl', 'numod', 'xcomp', 'ccomp', 'acl']
    num_of_recursions = 0

    def break_conjunctions_2(edge_list):
        broken = edge_list.copy()
        new = []
        for i, edge in enumerate(edge_list):
            if edge[2]=='conj':
                new2 = []
                try: broken.remove(edge)
                except ValueError: pass
                new2.append(edge)
                for child in [x for x in edge_list if x[0] == edge[1]]:
                    try: broken.remove(child)
                    except ValueError: pass
                    new2.append(child)
                new.append(new2)
        new.append(broken)
        return new

    def outgoings(n):
        return [edge for edge in tree if edge[0] == n]

    #

    def path_to_merge2(num_lst, num_of_recursions):

        num_of_recursions += 1

        # looks at path dependencies that suggest multiple nodes should be merged as an entity
        merge_path = []
        if len(num_lst)==0: return num_lst
        if len(num_lst)==1: return num_lst
        for num in num_lst:
            for outgoing in outgoings(num):
                if any([x for x in combine_relations if x in outgoing[2]]) or 'mod' in outgoing[2]:
                    merge_path.append(outgoing[0])
                    merge_path.append(outgoing[1])
                    if num_of_recursions < 20:
                        try:
                            path_to_merge2(outgoing[1], num_of_recursions)
                        except RecursionError:
                            break
        return list(set(merge_path))


    # all paths from a node to end of tree
    def tracepath(num):
        trace = []

        def p(i):
            outgoing_edges = [edge for edge in tree if edge[0] == i]
            if len(outgoing_edges)>0:
                trace.append(outgoing_edges)
                for j in outgoing_edges:
                    p(j[1])
        p(num)
        trace = list(itertools.chain.from_iterable(trace))
        return trace
    # nodes with incoming edges as nsubj or nsubjpass are potential start points

    all_subjs = []
    start_subj = [edge[1] for edge in tree if 'subj' in edge[2]]

    # finds the main relation incoming from the start subj

    if start_subj:
        main_relation = [edge[0] for edge in tree if edge[1] == start_subj[0]]
        outgoing_from_starts = tracepath(start_subj[0])
        if outgoing_from_starts:
            split_lists = break_conjunctions_2(outgoing_from_starts)
            for lst in split_lists:
                if lst:
                    lst2 = [edge[1] for edge in lst]
                    if any([x[1] for x in outgoings(lst[0][0]) if x[1] in lst2 and x[2] in combine_relations]):
                        lst2.append(lst[0][0])
                    mergepath = path_to_merge2(lst2, num_of_recursions)
                    all_subjs.append(mergepath)

                else:
                    all_subjs.append(sorted(path_to_merge2([start_subj])))
        else:
            p = start_subj + [edge[1] for edge in outgoing_from_starts]
            all_subjs.append(p)

    else:
        main_relation = [edge[1] for edge in tree if edge[2] == 'root']
    #

    # if main relation is not a verb, check if outgoings have verb
    if main_relation:
        mainrelation_pos = nltk.pos_tag([node_lookup.get(main_relation[0])])
        if len(mainrelation_pos)>0:
            if not (mainrelation_pos[0][1]).startswith('V'):
                outgoing_relation = [edge for edge in tree if edge[0] == main_relation[0]]
                if outgoing_relation:
                    for i in outgoing_relation:
                        pos_tag = (node_lookup[i[1]])
                        if pos_tag.startswith("VB") and outgoings(i):
                            main_relation = i

    # special case for correlation/correlates
    # if correlation is in sentence, set that to main relation
    # check for previous negations
    # then subjects/effectees are children of correlation root (maybe take between?)

    prev_main = main_relation

    for t in tree:
        if 'correlat' in node_lookup[t[1]]:
            main_relation = [t[1]]

    all_effectees = []
    possible_effectees = []


    if main_relation:
        outgoing_relation = [edge for edge in tree if edge[0] == main_relation[0]]
        for edge in outgoing_relation:
            if edge[2] in ['compound', 'advmod', 'aux', 'auxpass', 'neg']:
                # combine with relation
                main_relation.append(edge[1])
            # outgoing from main relation that are possible effectees
            if edge[2] in effectee_dependencies :
                possible_effectees.append(edge[1])
            # if edge is a conj and relation = between

            if 'correlat' in node_lookup[main_relation[0]] and edge[2]=='conj':
                possible_effectees.append(edge[1])

    # print(node_lookup[main_relation[0]], possible_effectees)
    try:
        if 'correlat' in node_lookup[main_relation[0]] and len(possible_effectees)<=2:
            #
            def outgoing(e):
                return [edge for edge in tree if edge[0] == e]
            outgoing_relation = outgoing(prev_main[0])

            for edge in outgoing_relation:
                if edge[2] in ['compound', 'advmod', 'aux', 'auxpass', 'neg']:
                    # combine with relation
                    main_relation.append(edge[1])
                # outgoing from main relation that are possible effectees
                if any([e for e in outgoing(edge[1]) if node_lookup[e[1]]=='between']):
                    possible_effectees.append(edge[1])
                if edge[2] in effectee_dependencies or edge[2]=='conj':
                    possible_effectees.append(edge[1])
                # if edge is a conj and relation = between

    except IndexError:
        pass

        # if no possible effectees, look for verbs inside subject
    for effectee in possible_effectees:
        split_lists = break_conjunctions_2(tracepath(effectee))
        for lst in split_lists:
            if lst:
                # if lst[0][0] is direct parent node, append
                lst2 = [edge[1] for edge in lst]
                if any([x[1] for x in outgoings(lst[0][0]) if x[1] in lst2 and x[2] in combine_relations]):
                    lst2.append(lst[0][0])
                mergepath = path_to_merge2(lst2, num_of_recursions)
                all_effectees.append(sorted(mergepath))
            else:
                all_effectees.append(sorted(path_to_merge2([effectee], num_of_recursions)))

    output = sort_combinations(all_subjs, main_relation, all_effectees, full_tree, node_lookup)

    return output



def re_main(text):

    dependency_parser = StanfordDependencyParser(path_to_jar=class_path, path_to_models_jar=models_path)
    output_relations = []
    sentences = nltk.sent_tokenize(text)
    length = len(sentences)

    for i, sentence in enumerate(sentences):

        result = dependency_parser.raw_parse(sentence)
        dep = result.__next__()
        trips = list(dep.triples())
        tree = str(dep.to_dot())

        # for trip in trips: print(trip)

        # part of speech tags to reference
        pos_tagged = {}
        for pos in trips:
            pos_tagged[pos[0][0]] = pos[0][1]
            pos_tagged[pos[2][0]] = pos[2][1]

        tree_split = list(filter(None, [line.strip() for line in tree.split("\n") if line != "\n"]))

        # for i in tree_split:  print(i)

        # dictionary of node num: label to lookup
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

        # if there's multiple subjects, split tree

        c = Counter(elem[2] for elem in tree_triples if 'subj' in elem[2])
        tree = []
        if sum(c.values()) > 1:
            split_indices = []
            for triple in tree_triples:
                if 'subj' in triple[2]:
                    # node number of each sub
                    # parent node is likely main relation
                    incoming = [x for x in tree_triples if x[1] == triple[0]]
                    split_indices.append(tree_triples.index(incoming[0]))

            for idx in split_indices:
                # if first indicy
                if split_indices.index(idx) == 0:
                    tree = (tree_triples[0:split_indices[1] - 1])
                elif split_indices.index(idx) != len(split_indices) - 1:
                    tree = (tree_triples[idx:split_indices[split_indices.index(idx)+1]])
                else:
                    tree = (tree_triples[idx:len(tree_triples)])
        else:
            tree = tree_triples

        if tree:
            out = build_paths(tree, tree_triples, node_lookup)
            output_relations.append(out)

    copyoutput = output_relations.copy()
    output = list(itertools.chain.from_iterable(copyoutput))
    filtered = filteroutput(output)
    cleaned = cleanoutput(filtered)

    # dep.tree().draw()

    return cleaned


if __name__=="__main__":

    sentence_file = open('files/evaluation_files/relations_gene_onto.txt', 'r').readlines()
    write_file = open('files/evaluation_files/re_output.txt', 'w')

    results = {}

    for line in sentence_file:
        if not line.startswith('PMC') and line != '\n':
            sentence = line.strip()
            relations = re_main(sentence)
            write_file.write("\nsentence: {}\n".format(sentence))
            for relation in relations:

                write_file.write("{}\n".format(relation))
                print(relation)


    write_file.close()


    # gene_corpus_file = open('files/papers/asd_gene_corpus.txt', 'r').readlines()
    # gene_corpus = reload_corpus(gene_corpus_file)
    #
    # pheno_corpus_file = open('files/papers/asd_pheno_corpus.txt', 'r').readlines()
    # pheno_corpus = reload_corpus(pheno_corpus_file)
    #
    # corpus = list(set(gene_corpus + pheno_corpus))
    #
    # write_file = open('files/papers/sentences_for_relation_gene.txt', 'w')
    #
    #
    # for i, paper in enumerate(gene_corpus):
    #     sentence_list = []
    #     if paper.abstract:
    #         text = process_text(paper.abstract+ paper.text)
    #         for sentence in nltk.sent_tokenize(text):
    #             sentence = sentence.lower()
    #             if len(sentence.split())<40:
    #                 sfari = [k for k, v in get_sfari(sentence).items()]
    #                 if len(sfari)>0:
    #                     maps = main_main(sentence)
    #                     if maps:
    #                         print(sentence)
    #                         sentence_list.append(sentence)
    #
    #     if len(sentence_list)>0:
    #         sentence_list = list(set(sentence_list))
    #         write_file.write("\nPMC{}:\n".format(paper.id))
    #         for sentence in sentence_list:
    #             write_file.write("{}\n".format(sentence))
    #
    # write_file.close()



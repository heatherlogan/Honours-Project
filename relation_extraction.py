import itertools
from collections import defaultdict, Counter
from nltk.parse.stanford import StanfordDependencyParser
import nltk

class_path = "/Users/heatherlogan/Desktop/stanford-parser-full-2018-10-17/stanford-parser.jar"
models_path = "/Users/heatherlogan/Desktop/stanford-english-corenlp-2018-02-27-models.jar"

def build_paths(tree):

    # print(tree)

    output_relations = []

    def format(subject, relation, effector):

        # possible anaphors are phrases without inner noun phrases
        # works for 'this' 'that' etc

        def anaphor(text):
            pt = nltk.pos_tag(text.split())
            if len(pt) == 1 and all(['NN' not in x[1] for x in pt[0]]):
                return True
            else:
                return False


        def node_to_text(int_list):

            txt_string = []

            for i in range(min(int_list) - 1, max(int_list)):
                try:
                    # try as some nodes are missed in the tree
                    txt_string.extend([node_lookup[str(i + 1)]])
                except KeyError:
                    pass
            return " ".join(txt_string)

        subject_text = node_to_text(sorted([int(x) for x in subject]))

        # if anaphor(subject_text):
        #     subject_text = output_relations[len(output_relations) - 1][2]

        relation = sorted([int(x) for x in relation])
        relation_text = node_to_text(relation) if -1 not in relation else "not_" + node_to_text(relation[1:])
        effector_text = node_to_text(sorted([int(x)for x in effector]))

        output_relations.append((subject_text, relation_text, effector_text))

        print((subject_text, relation_text, effector_text))
        print("\t{}({}, {})".format(relation_text, subject_text, effector_text))


    def sort_combinations(subjects, relations, effectors):

        # print("Subj:",subjects, "\nRelation: ", relations, "\nEffectors: ",effectors)

        # check negations; if negative child node attached to subject or entity then negate relation
        def negated(nodes):
            return any([x for x in tree_triples if x[0] in [i[0] for i in nodes] and x[2]=='neg'])

        for subject in subjects:
            for effector in effectors:
                if effector != subject:
                    if negated(subject) or negated(effector):
                        relations.append('-1')

                format(subject, relations, effector)


    def break_conjunctions(num, limit):
        conjunctions = [edge[1] for edge in tree if edge[2] == 'conj'and int(num) <= int(edge[0]) <= int(limit)]
        return conjunctions

    def path_to_merge(num):
        merge_path = [num]

        def outgoings(n):
            return [edge for edge in tree_triples if edge[0] == n]

        if outgoings(num):
            for outgoing in outgoings(num):
                if any([x for x in combine_relations if x in outgoing[2]]) or 'mod' in outgoing[2]:
                    merge_path.append(outgoing[1])
                    path_to_merge(outgoing)
                else:
                    break

        return merge_path

    # nodes with incoming edges as nsubj or nsubjpass are potential start points

    all_subjs = []
    start_subj = [edge[1] for edge in tree if 'subj' in edge[2]]

    if start_subj:
        main_relation = [edge[0] for edge in tree if edge[1] == start_subj[0]]
        outgoing_from_starts = start_subj + [edge[1] for edge in tree_triples if edge[0] == start_subj[0]]
        for effectee in outgoing_from_starts:
            for start in start_subj + break_conjunctions(effectee, main_relation[0]):
                mergepath = path_to_merge(start)
                if mergepath not in all_subjs: all_subjs.append(mergepath)
    else:
        main_relation = [edge[1] for edge in tree if edge[2] == 'root']

    outgoing_relation = [edge for edge in tree if edge[0] == main_relation[0]]

    possible_effectees = []

    for edge in outgoing_relation:
        if edge[2] in ['compound']:
            # combine with relation
            main_relation.append(edge[1])
        if edge[2] in ['dobj', 'nmod', 'amod', 'advcl', 'numod', 'xcomp', 'ccomp']:
            possible_effectees.append(edge[1])

    all_effectees = []
    for effectee in possible_effectees:
        all_ent_starters = break_conjunctions(effectee, max([int(x[0]) for x in tree]))
        for start in [effectee] + all_ent_starters:
            mergepath = path_to_merge(start)
            all_effectees.append(mergepath)

    # if there's no start subjects then all effectees are possible combinations of each

    # print("All subjs-{}\nMain relation-{}\nAll_effectees:{}\n".format(all_subjs, main_relation, all_effectees))

    return sort_combinations(all_subjs, main_relation, all_effectees)




if __name__ == "__main__":

    combine_relations = ['acl', 'acl:recl', 'mod', 'aux', 'case', 'dep', 'det', 'case', 'cc'
                                    'nummod', 'mark', 'acl', 'dobj', 'conj',
                                    'nmod', 'amod', 'advmod', 'compound']

    dependency_parser = StanfordDependencyParser(path_to_jar=class_path, path_to_models_jar=models_path)

    # temps

    shank_abs = "SHANK proteins are crucial for the formation and plasticity of excitatory synapses. " \
                "Although mutations in all three SHANK genes are associated with autism spectrum disorder , " \
                "SHANK3 appears to be the major Autism Spectrum Disorder gene with a prevalence of approximately 0.5% for SHANK3 mutations " \
                "in Autism Spectrum Disorder, with higher rates in individuals with Autism Spectrum Disorder and intellectual disability . " \
                "Interestingly, the most relevant mutations are typically de novo and often are frameshift or nonsense mutations resulting in a" \
                " premature stop and a truncation of SHANK3 protein. We analyzed three different SHANK3 stop mutations that we identified " \
                "in individuals with Autism Spectrum Disorder and/or intellectual disability, one novel and two that we recently described . " \
                "The mutations were inserted into the human SHANK3a sequence and analyzed for effects on subcellular localization and neuronal " \
                "morphology when overexpressed in rat primary hippocampal neurons. Clinically, all three individuals harboring these mutations had " \
                "global developmental delays and intellectual disability. In our in vitro assay, c.1527G > A and c.2497delG both result in proteins " \
                "that lack most of the SHANK3a C-terminus and accumulate in the nucleus of transfected cells. Cells expressing these mutants exhibit " \
                "converging morphological phenotypes including reduced complexity of the dendritic tree, less spines, and less excitatory, but not " \
                "inhibitory synapses. In contrast, the truncated protein based on c.5008A > T, which lacks only a short part of the sterile alpha " \
                "motif domain in the very SHANK3a C-terminus, does not accumulate in the nucleus and has minor effects on neuronal morphology. " \
                "In spite of the prevalence of SHANK3 disruptions in Autism Spectrum Disorder and intellectual disability, " \
                "only a few human mutations have been functionally characterized; here we characterize three additional mutations. " \
                "Considering the transcriptional and functional complexity of SHANK3 in healthy neurons, we propose that any heterozygous " \
                "stop mutation in SHANK3 will lead to a dysequilibrium of SHANK3 isoform expression and alterations in the stoichiometry of" \
                " SHANK3 protein complexes, resulting in a distinct perturbation of neuronal morphology. This could explain why the clinical " \
                "phenotype in all three individuals included in this study remains quite severe - regardless of whether there are disruptions " \
                "in one or more SHANK3 interaction domains."

    pers_abs = "Maintaining an appropriate distance from others is important for establishing effective communication and good interpersonal relations. Autism spectrum disorder is a developmental disorder associated with social difficulties, and it is thus worth examining whether individuals with ASD maintain typical or atypical degrees of social distance. Any atypicality of social distancing may impact daily social interactions. We measured the preferred distances when individuals with ASD and typically developing individuals approached other people and objects or when other people approached them. Individuals with ASD showed reduced interpersonal distances compared to TD individuals. The same tendency was found when participants judged their preferred distance from objects. In addition, when being approached by other people, both individuals with ASD and TD individuals maintained larger interpersonal distances when there was eye contact, compared to no eye contact. These results suggest that individuals with ASD have a relatively small personal space, and that this atypicality exists not only for persons but also for objects."

    s = "WAGR syndrome is characterized by Wilm’s tumor, aniridia, genitourinary abnormalities and intellectual disabilities. WAGR is caused by a chromosomal deletion that includes the PAX6, WT1 and PRRG4 genes. PRRG4 is proposed to contribute to the autistic symptoms of WAGR syndrome, but the molecular function of PRRG4 genes remains unknown. The Drosophila commissurelessissureless gene encodes a short transmembrane protein characterized by PY motifs, features that are shared by the PRRG4 protein. Comm intercepts the Robo axon guidance receptor in the ER/Golgi and targets Robo for degradation, allowing commissurelessissural axons to cross the CNS midline. Expression of human Robo1 in the fly CNS increases midline crossing and this was enhanced by co-expression of PRRG4, but not CYYR, Shisa or the yeast Rcr genes. In cell culture experiments, PRRG4 could re-localize hRobo1 from the cell surface, suggesting that PRRG4 is a functional homologue of Comm. Comm is required for axon guidance and synapse formation in the fly, so PRRG4 could contribute to the autistic symptoms of WAGR by disturbing either of these processes in the developing human brain."

    s2 = "Comm intercepts the Robo axon guidance receptor in the ER/Golgi and targets Robo for degradation."

    s3 = 'Our results reveal disorder overlap and specificity at the genetic and gene expression level. They suggest new pathways contributing to distinct pathophysiology in psychiatric disorders and shed light on potential shared genomic risk factors.'


    for sentence in nltk.sent_tokenize(s3):

        output_relations = []

        print("\n", sentence, "\n")

        result = dependency_parser.raw_parse(sentence)
        dep = result.__next__()
        trips = list(dep.triples())
        tree = str(dep.to_dot())

        for trip in trips:
            print(trip)

        # part of speech tags to reference
        pos_tagged = {}
        for pos in trips:
            pos_tagged[pos[0][0]] = pos[0][1]
            pos_tagged[pos[2][0]] = pos[2][1]
        #
        for i in tree.split("\n"):
             print(i)

        tree_split = list(filter(None, [line.strip() for line in tree.split("\n") if line != "\n"]))

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
        if sum(c.values()) > 1:
            split_indices = []
            for triple in tree_triples:
                if 'subj' in triple[2]:
                    split_indices.append(tree_triples.index(triple))
            for idx in split_indices:
                if split_indices.index(idx) == 0:
                    build_paths(tree_triples[0:split_indices[1] - 1])
                elif split_indices.index(idx) != len(split_indices) - 1:
                    build_paths(tree_triples[idx:split_indices[split_indices.index(idx)+1]])
                else:
                    build_paths(tree_triples[idx:len(tree_triples)])
        else:
            build_paths(tree_triples)


        dep.tree().draw()

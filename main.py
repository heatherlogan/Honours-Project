from relation_extraction import *
from NER import *
from relation_mapping import *
from indexer import *
import nltk
from analyse import format_results


def sort_final_mapping(mapping_list):

    def get_obj(name):
        return next((x for x in onto_objects if x.label == name), None)

    def string_ancestors(name):
        return [str(x).replace('asdpto.', '') for x in get_obj(name).ancestors[0]]

    if len(mapping_list)==1:
        return mapping_list[0]
    else:
        copylist = mapping_list.copy()
        combs = itertools.combinations(mapping_list,2)
        for c1, c2 in combs:
            if get_obj(c1).classnum in string_ancestors(c2):
                if c1 in copylist: copylist.remove(c1)
            elif get_obj(c2).classnum in string_ancestors(c1):
                if c1 in copylist: copylist.remove(c1)
        if len(copylist)>0:
            return copylist[0]
        else:
            return mapping_list[0]

def main(text):

    SFARI_genes = []
    non_SFARI_genes = []
    mutations = []
    pheno_terms = []
    all_ents = []

    def get_name(classno):
        return next((x for x in onto_objects if x.classnum == classno), None).label

    # preprocess
    text = process_text(text)
    sentences = nltk.sent_tokenize(text)
    # possible verb - nounphrase - possible adverb - TO/IN - nounphrase
    pattern = r""" Ents: {(<VB>|<VBN>|<VBG>|<VBD>)*<JJ>*(<NN>|<NNS>|<NNP>)+(<RB>|<RBR>|<RBS>)*(<IN>)+<CD>*<JJ>*(<NN>|<NNS>|<NNP>)+}"""

    # independently search genes/ontology concepts and return counts
    #
    length = len(sentences)
    relevant_sentences = []

    for i, sentence in enumerate(sentences):

        print('{:.3f}'.format((i/length)*100))

        sentence = re.sub(r"[:;]", ',', sentence)
        mentioned_sfari = get_sfari(sentence)
        mentioned_non_sfari = get_non_sfari(sentence)

        mentioned_mutations = mutation_search(sentence)

        SFARI_genes.extend(mentioned_sfari)

        [SFARI_genes.append(gene) for gene in mentioned_sfari]
        [non_SFARI_genes.append(gene) for gene in mentioned_non_sfari]
        [mutations.append(mutation) for mutation in mentioned_mutations]

        if mentioned_sfari or mentioned_non_sfari or mentioned_mutations:
            relevant_sentences.append(sentence)

        entities_ext = entity_extract(sentence, pattern)
        entities_NP = entity_extract(sentence, r""" Ents: {[0-9]*<JJ>*<VB>*(<NN>|<NNS>|<NNP>)+}""")


        for entity in entities_ext:
            # inner noun phrases
            inner_mappings = defaultdict(list)
            mapping = []
            inner_ents = entity_extract(entity, 'default')
            entity = entity.strip()
            stemmed_ent = sorted([stemmer.stem(ent) for ent in entity.split()])

            for node, phrases in onto_terms.items():
                for phrase in phrases:
                    if '*i' in phrase:
                        for word in illness_syns:
                            if phrase2 == stemmed_ent or all([p in stemmed_ent for p in phrase2]):
                                mapping.append(get_name(node))

                    elif '*d' in phrase:
                        for word in deficit_syns:
                            phrase2 = sorted(phrase.replace('*d', word).split())
                            if phrase2 == stemmed_ent or all([p in stemmed_ent for p in phrase2]):
                                mapping.append(get_name(node))

                    elif '*s' in phrase:
                        for word in skills_syns:
                            phrase2 = sorted(phrase.replace('*s', word).split())
                            if phrase2 == stemmed_ent or all([p in stemmed_ent for p in phrase2]):
                                mapping.append(get_name(node))
                    else:
                        phrase2 = sorted(phrase.split())
                        if phrase2 == stemmed_ent or all([p in stemmed_ent for p in phrase2]):
                            mapping.append(get_name(node))

                    if inner_ents:
                        for e in inner_ents:
                            stem_inner_ent = ([stemmer.stem(e1) for e1 in e.split()])
                            # if inner ents are mapped to same
                            if sorted(phrase.split()) == stem_inner_ent or all([p in stem_inner_ent for p in sorted(phrase.split())]):
                                inner_mappings[e].append(get_name(node))

            if len(mapping) > 0 and len(inner_mappings) == 0:
                final_mapping = sort_final_mapping(mapping)
                pheno_terms.append((entity.strip(), final_mapping))
                if sentence not in relevant_sentences:
                    relevant_sentences.append(sentence)
            else:
                for e, map in inner_mappings.items():
                    final_mapping = sort_final_mapping(map)
                    pheno_terms.append((e.strip(), final_mapping))
                if sentence not in relevant_sentences:
                    relevant_sentences.append(sentence)

        pheno_ents = [p[0] for p in pheno_terms]
        #
        for entity in entities_NP:
            stemmed_ent = sorted([stemmer.stem(e) for e in entity.split()])
            mapping2 = []
            all_ents.append(entity)
            if entity not in pheno_ents:
                for node, phrases in onto_terms.items():
                    for phrase in phrases:
                        if "*i" in phrase:
                            for word in illness_syns:
                                phrase2 = sorted(phrase.replace('*i', word).split())
                                if phrase2 == stemmed_ent or all([p in stemmed_ent for p in phrase2]):
                                    mapping2.append(get_name(node))
                        elif "*d" in phrase:
                            for word in deficit_syns:
                                phrase2 = sorted(phrase.replace('*d', word).split())
                                if phrase2 == stemmed_ent or all([p in stemmed_ent for p in phrase2]):
                                    mapping2.append(get_name(node))
                        elif "*s" in phrase:
                            for word in skills_syns:
                                phrase2 = sorted(phrase.replace('*s', word).split())
                                if phrase2 == stemmed_ent or all([p in stemmed_ent for p in phrase2]):
                                    mapping2.append(get_name(node))
                        else:
                            if sorted(phrase.split()) == stemmed_ent or all([p in stemmed_ent for p in phrase.split()]):
                                mapping2.append(get_name(node))

            if len(mapping2) > 0:
                final_mapping2 = sort_final_mapping(mapping2)
                pheno_terms.append((entity.strip(), final_mapping2))
                if sentence not in relevant_sentences: relevant_sentences.append(sentence)

    # get basic relations - pass full text

    if SFARI_genes:
        count_sfari = Counter(SFARI_genes)
        write_file.write("SFARI Genes: ")
        for gene, count in count_sfari.items():
            write_file.write("{}: {},".format(gene, count))

    if non_SFARI_genes:
        count_non_sfari = Counter(non_SFARI_genes)
        write_file.write("\nNon SFARI Genes: ")
        for gene, count in count_non_sfari.items():
            write_file.write("{}: {},".format(gene, count))

    write_file.write('\nASD_Terms:')
    for term in pheno_terms:
        write_file.write('({}), '.format(term))

    write_file.write('\n')
    # text = ' '.join(relevant_sentences)
    # relations = re_main(text)
    # #
    # print("\n\n******RELATIONS******")
    # write_file.write('Relations\n')
    # for relation in relations:
    #     write_file.write("\t{}\n".format(relation))


    # # mappings
    # print('mapping')
    # mappings = map_main(relations)
    #
    # Mapping
    # print("\n\n******MAPPING******")
    #
    # for mapping in mappings:
    #     print(mapping, ",")
    #
    # print("\n\n")
    # # add to neo4j
    #
    # graph_relations(mappings)
    #
    # print("graphing done")

if __name__=="__main__":

    illness_syns = [stemmer.stem(x) for x in ['illness', 'disorder', 'disability', 'disease', 'infection', 'syndrome', 'virus' ]]
    deficit_syns = [stemmer.stem(x) for x in ['atypicality', 'deficit', 'disability', 'dysfunction', 'delay', 'abnormality', 'complication', 'condition', 'problem',
                    'impairment', 'malformation', 'issue', 'imbalanced', 'disturbance', 'difficulty', 'difficulties', 'differences', 'diagnosis', 'affliction', 'disabled']]
    skills_syns = [stemmer.stem(x) for x in ['skills', 'proficiency', 'abilities', 'ability', 'capability', 'development',
                                             'understanding', 'talent', 'comprehension', 'function', 'control']]

    onto_terms = load_onto_terms()
    onto_objects = build_onto_objects()

    file = open('files/papers/asd_gene_corpus.txt').readlines()
    write_file = open("files/system_output/gene_output_3.txt", 'w')

    papers = reload_corpus(file)

    results_file = open('files/system_output/gene_output_full.txt', 'r').readlines()
    results = format_results(results_file)
    downloaded_ids = [str(result.id) for result in results]
    count = 0
    for paper in papers:
        if str(paper.id) not in downloaded_ids:
            pass
            print(str(paper.id))
            # count += 1
            # write_file.write('\n\nPMCID:{}\n'.format(paper.id))
            # text = paper.abstract + paper.text
            # main(text)
    write_file.close()


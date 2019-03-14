from nltk import PorterStemmer
from NER import *
from pubmed_parse import get_synonyms, sort_hgnc
from collections import defaultdict
from ontology_stuff import build_onto_objects

stemmer = PorterStemmer()


def load_onto_terms():

    def format_terms(file):
        terms = defaultdict(list)

        for line in file:
            if line.startswith("Class_"):
                classno, name = line.strip().split(": ")
            elif not line == "\n":
                if line.startswith('semtypes:'):
                    semtypes = re.findall('\[.*?\]', line)
                    terms[classno].append(semtypes)
                else:
                    stemmed_line = " ".join([stemmer.stem(x) for x in line.strip().split()])
                    terms[classno].append(stemmed_line)
        return terms

    file = open('files/autism_terms/asdpto_terms_new.txt', 'r').readlines()
    terms = format_terms(file)
    return terms

def relevant_terms():

    gene_terms = [stemmer.stem(term) for term in ['gene', 'genetic', 'genome', 'genotype' 'allele', 'carrier',
                  'chromosome', 'dominant', 'DNA', 'heterozygoes', 'recessive',
                  'X-linked', 'homologous', 'RNA', 'translation', 'transcription',
                  'X-', 'exome', 'haploid' ]]

    mutation_terms = [stemmer.stem(term) for term in ['mutation', 'mutant', 'mutate', 'de novo', 'denovo', 'novo', 'homozygous', 'monozygous',
                      'insertion', 'deletion', 'duplication', 'substitution', 'inversion', 'translocation', 'nonsense', 'frameshift',
                      'mutation', 'CNV', 'SNV', 'SNP', 'variant', 'misssense', 'single nucleotide polymorphism', 'single nucleotide variant', 'truncate',
                      'copy number variant']]
    return gene_terms, mutation_terms


def sort_onto_mappings(classno_list, onto_objects):

    # eliminates double mappings that are ancestors,
    # returns list of ancestors for each mapping
    copylist = classno_list.copy()


    def get_obj(classno):
        return next((x for x in onto_objects if x.classnum == classno), None)

    def string_ancestors(classno):
        return [str(x).replace('asdpto.', '') for x in get_obj(classno).ancestors[0]]

    if len(classno_list)>1:
        combs = itertools.combinations(classno_list,2)
        for c1, c2 in combs:
            if c1 in string_ancestors(c2):
                if c1 in copylist: copylist.remove(c1)
            elif c2 in string_ancestors(c1):
                if c1 in copylist: copylist.remove(c1)
    return copylist


def map_main(relations):

    gene_terms, mutation_terms = relevant_terms()
    SFARI_genes = set(itertools.chain.from_iterable(get_synonyms().values()))
    non_SFARI_genes = set(itertools.chain.from_iterable(sort_hgnc().values())) - SFARI_genes
    SFARI_genes, non_SFARI_genes = list(SFARI_genes), list(non_SFARI_genes)
    onto_terms = load_onto_terms()
    onto_objects = build_onto_objects()
    node_mappings = {}
    final_relations = []
    # relevant semantic types

    semtype_maps = {
        '[gngm]': 'Genes',
        '[diap]': 'Diagnosis',
        '[cgab]': 'Congenital Abnormalities'
    }

    for subj, rel, effectee in relations:

            subject_mappings = []
            effectee_mappings = []
            subj_onto_mappings = []
            effectee_onto_mappings = []

            stemmed_subj = " ".join([stemmer.stem(x) for x in subj.split()])
            stemmed_eff = " ".join([stemmer.stem(x) for x in effectee.split()])

            # search for mutations and mutation terms
            m1, m2 = mutation_search(subj), mutation_search(effectee)
            if len(m1) > 0: subject_mappings.append('Mutations')
            if len(m2) > 0: effectee_mappings.append('Mutations')
            if any([stemmer.stem(x) for x in subj.split() if stemmer.stem(x) in mutation_terms]): subject_mappings.append('Mutations')
            if any([stemmer.stem(x) for x in effectee.split() if stemmer.stem(x) in mutation_terms]): effectee_mappings.append('Mutations')

            # search for SFARI genes
            if any([x for x in subj.split() if x in SFARI_genes]): subject_mappings.append('SFARI Genes')
            if any([x for x in effectee.split() if x in SFARI_genes]): effectee_mappings.append('SFARI Genes')

            # search for non SFARI genes/ gene terms
            if any([x for x in subj.split() if x in non_SFARI_genes]): subject_mappings.append('Genes')
            if any([x for x in effectee.split() if x in non_SFARI_genes]): effectee_mappings.append('Genes')
            if any([stemmer.stem(x) for x in subj.split() if stemmer.stem(x) in gene_terms and 'SFARI Genes' not in subject_mappings]): subject_mappings.append('Genes')
            if any([stemmer.stem(x) for x in effectee.split() if stemmer.stem(x) in gene_terms and 'SFARI Genes' not in subject_mappings]): effectee_mappings.append('Genes')

            s = annotate(subj)
            e = annotate(effectee)

            # map to onto if semantic type is in related
            if s == '[gngm]': subject_mappings.append('Genes')
            if e == '[gngm]': effectee_mappings.append('Genes')

            # search for matches in onto
            for node, phrases in onto_terms.items():
                for phrase in phrases:
                    if type(phrase) != list and "{} ".format(phrase) in stemmed_subj or phrase==stemmed_subj:
                        subj_onto_mappings.append(node)
                    if type(phrase) != list and "{} ".format(phrase) in stemmed_eff or phrase==stemmed_eff:
                        effectee_onto_mappings.append(node)

            if subj_onto_mappings: subject_mappings.extend(sort_onto_mappings(subj_onto_mappings, onto_objects))
            if effectee_onto_mappings: effectee_mappings.extend(sort_onto_mappings(effectee_onto_mappings, onto_objects))

            # map to onto if semantic type is in related

            # add to dict to format
            node_mappings[(subj, s)] = list(set(subject_mappings))
            node_mappings[(effectee, e)] = list(set(effectee_mappings))

    for e1, rel, e2 in relations:
        new_e1, new_e2 = {}, {}
        for k, v in node_mappings.items():
            if e1==k[0]: new_e1 = k
            if e2 == k[0]: new_e2 = k
            if type(new_e1)==tuple and type(new_e2)==tuple:
                final_relations.append((new_e1, rel, new_e2 ))

    temp = {'Genes':('Genes', '[heading]'),
            'SFARI Genes' : ('SFARI Genes', '[heading]'),
            'Mutations': ('Mutations', '[heading]')
            }

    # get onto, set type to is_a for the node it's mapped to
    def get_name(classno):
        return next((x for x in onto_objects if x.classnum == classno), None).label

    for entity, mappings in node_mappings.items():
        for map in mappings:
            if 'Class' in map:
                label = get_name(map)
                final_relations.append((entity, 'is_a', (label, '[pheno]')))
                final_relations.append(((label, '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')))
            else:
                final_relations.append((entity, 'is_a', temp.get(map)))

    print('\n\n\n')

    return list(set(final_relations))




if __name__=='__main__':

    gene_terms, mutation_terms = relevant_terms()
    SFARI_genes = set(itertools.chain.from_iterable(get_synonyms().values()))
    non_SFARI_genes = set(itertools.chain.from_iterable(sort_hgnc().values())) - SFARI_genes
    SFARI_genes, non_SFARI_genes = list(SFARI_genes), list(non_SFARI_genes)
    onto_terms = load_onto_terms()
    onto_objects = build_onto_objects()
    node_mappings = {}
    final_relations = []

    semtype_maps = {
        '[gngm]': 'Genes',
        '[diap]': 'Diagnosis',
        '[cgab]': 'Congenital Abnormalities'
    }

    relations = []
    file = open('files/NER_outputs/map_output.txt', 'r').readlines()
    for line in file:
        r, e = line.strip().split("(")
        e1, e2 = e.split(', ')
        e2 = e2.replace(")", '')
        relations.append((e1, r, e2))

    relations = list(set(relations))

    for relation in map_main(relations):
        print(map, ", ")

from nltk import PorterStemmer
from named_entity_recognition import *
from pubmed_parse import get_synonyms, sort_hgnc
from collections import defaultdict
from ontology_stuff import build_onto_objects

stemmer = PorterStemmer()

def example_relations():

    relations_SHANK = [('SHANK proteins', 'crucial for', 'formation of excitatory synapses'),
                 ('SHANK proteins', 'crucial for', 'plasticity of excitatory synapses'),
                 ('mutations in all three SHANK genes', 'associated', 'autism spectrum disorder'),
                 ('SHANK3', 'appears_to_be', 'major ASD gene'),
                 ('frameshift mutations', 'resulting in', 'premature stop'),
                 ('frameshift mutations', 'resulting in', 'truncation of SHANK3 protein'),
                 ('nonsense mutations', 'resulting in', 'premature stop'),
                 ('nonsense mutations', 'resulting in', 'truncation of SHANK3 protein'),
                 ('individuals harboring these mutations', 'had', 'global development delays'),
                 ('individuals harboring these mutations', 'had', 'intellectual disability'),
                 ('c.1527G > A,', 'result in', 'proteins that lack most of the SHANK3 terminus'),
                 ('c.2497delG', 'result in', 'proteins that lack most of the SHANK3 terminus'),
                 ('cells expressing these mutants', 'exhibit', 'converging morphological phenotypes'),
                 ('protein based on c.5008A>T', 'lacks', 'short part of the sterile alpha motif SAM domain'),
                 ('protein based on c.5008A>T', 'not accumulate in', 'nucleus'),
                 ('any heterozygous stop mutation in SHANK3', 'lead to', 'dysequilibrium of SHANK3 isoform expression'),
                 ('any heterozygous stop mutation in SHANK3', 'lead to', 'alterations in stoichiometry of SHANK3 protein complexes'),
                 ('any heterozygous stop mutation in SHANK3', 'resulting in', 'distinct perturbation of neuronal morphology'),
                 ('This', 'could explain', 'why the clinical phenotype in all three individuals included in this study remains')
                 ]

    relations_WAGR = [ ('WAGR syndrome', 'characterized_by', "by Wilm's tumor"),
                ('WAGR syndrome', 'characterized_by', 'andridia'),
                ('WAGR syndrome', 'characterized_by', 'genitourinary abnormalities'),
                ('WAGR syndrome', 'characterized_by', 'intellectual disabilities'),
                ('WAGR', 'caused_by', 'chromosomal deletion'),
                ('chromosomal deletion', 'includes', 'PAX6' ),
                ('chromosomal deletion', 'includes', 'WT1' ),
                ('chromosomal deletion', 'includes', 'PRRG4 genes'),
                ('PRRG4', 'proposed_to', 'contribute to the autistic symptoms'),
                ('the molecular function of PRRG4 genes', 'remains', 'unknown'),
                ('Drosophila commissurelessissureless gene', 'encodes', 'a short transmembrane protein characterized by PY motifs'),
                ('a short transmembrane protein characterized by PY motifs', 'shared_by', 'PRRG4 protein'),
                ('Comm', 'intercepts', 'the Robo axon guidance receptor in the ER/Golgi'),
                ('Comm', 'targets', 'Robo for degradation'),
                ('Expression of human Robo1', 'CNS', 'midline crossing'),
                ('midline crossing','enhanced_by','co-expression of PRRG4'),
                ('midline crossing','not_enhanced_by','CYRR'),
                ('midline crossing','not enhanced_by','Shisa'),
                ('midline crossing','not enhanced_by','yeast Rcr genes'),
                ('PRRG4', 're-localize', 'hRobo1'),
                ('PRRG4', 'homologue' , 'Comm'),
                ('Comm', 'required_for', 'axon guidance and synapse formation in the fly'),
                ('PRRG4', 'contribute_to', 'autistic symptoms of WAGR'),
                ('PRRG4', 'contribute_to', 'disturbing either of these processes'),
    ]

    return relations_WAGR


def load_onto_terms():

    def format_terms(file):

        terms = defaultdict(list)

        for line in file:
            if line.startswith("Class_"):
                classno, name = line.strip().split(": ")
            elif not line == "\n":
                semtypes = []
                if line.startswith('semtypes:'):
                    semtypes = re.findall('\[.*?\]', line)
                    terms[classno].append(semtypes)

                else:
                    stemmed_line = " ".join([stemmer.stem(x) for x in line.strip().split()])
                    terms[classno].append(stemmed_line)
        return terms

    file = open('files/autism_terms/asdpto_terms.txt', 'r').readlines()
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

def sort_onto_mappings(classno_list):

    # eliminates double mappings that are ancestors, returns list of ancestors for each mapping
    copylist = classno_list.copy()

    def get_obj(classno):
        return next((x for x in onto_objects if x.classnum == classno), None)

    def string_ancestors(classno):
        return [str(x).replace('asdpto.', '') for x in get_obj(classno).ancestors[0]]

    if len(classno_list)>1:
        combs = itertools.combinations(classno_list,2)
        for c1, c2 in combs:
            if c1 in string_ancestors(c2):
                copylist.remove(c1) if c1 in copylist else None
            elif c2 in string_ancestors(c1):
                copylist.remove(c1) if c1 in copylist else None

    return copylist



if __name__=="__main__":

    gene_terms, mutation_terms = relevant_terms()
    relations = example_relations()
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
        '': ''
    }

    for subj, rel, effectee in relations:

            subject_mappings = []
            effectee_mappings = []
            subj_onto_mappings = []
            effectee_onto_mappings = []

            stemmed_subj = " ".join([stemmer.stem(x) for x in subj.split()])
            stemmed_eff = " ".join([stemmer.stem(x) for x in effectee.split()])

            # search for mutations
            m1, m2 = mutation_search(subj), mutation_search(effectee)
            if len(m1) > 0: subject_mappings.append('Mutations')
            if len(m2) > 0: effectee_mappings.append('Mutations')
            if any([stemmer.stem(x) for x in subj.split() if stemmer.stem(x) in mutation_terms]): subject_mappings.append('Mutations')
            if any([stemmer.stem(x) for x in effectee.split() if stemmer.stem(x) in mutation_terms]): effectee_mappings.append('Mutations')

            # search for SFARI genes
            if any([x for x in subj.split() if x in SFARI_genes]): subject_mappings.append('SFARI Genes')
            if any([x for x in effectee.split() if x in SFARI_genes]): effectee_mappings.append('SFARI Genes')

            # search for non SFARI genes
            if any([x for x in subj.split() if x in non_SFARI_genes]): subject_mappings.append('Genes')
            if any([x for x in effectee.split() if x in non_SFARI_genes]): effectee_mappings.append('Genes')
            if any([stemmer.stem(x) for x in subj.split() if stemmer.stem(x) in gene_terms and 'SFARI Genes' not in subject_mappings]): subject_mappings.append('Genes')
            if any([stemmer.stem(x) for x in effectee.split() if stemmer.stem(x) in gene_terms and 'SFARI Genes' not in subject_mappings]): effectee_mappings.append('Genes')

            s = annotate(subj)
            e = annotate(effectee)

            # search for matches in onto
            for node, phrases in onto_terms.items():
                for phrase in phrases:
                    if type(phrase) != list and "{} ".format(phrase) in stemmed_subj or phrase==stemmed_subj:
                        subj_onto_mappings.append(node)
                    if type(phrase) != list and "{} ".format(phrase) in stemmed_eff or phrase==stemmed_eff:
                        effectee_onto_mappings.append(node)

            if subj_onto_mappings: subject_mappings.extend(sort_onto_mappings(subj_onto_mappings))
            if effectee_onto_mappings: effectee_mappings.extend(sort_onto_mappings(effectee_onto_mappings))

            # map to onto if semantic type is in related

            # add to dict to format
            node_mappings[(subj, s)] = list(set(subject_mappings))
            node_mappings[(effectee, e)] = list(set(effectee_mappings))

    for e1, rel, e2 in relations:
        new_e1, new_e2 = {}, {}
        for k, v in node_mappings.items():
            if e1==k[0]: new_e1 = k
            if e2 == k[0]: new_e2 = k
            if len(new_e1.keys())>0 and len(new_e2.keys())>0:
                final_relations.append((new_e1, rel, new_e2 ))

    for entity, mappings in node_mappings.items():
        for map in mappings:
            final_relations.append((entity, 'is_a', map))

    print('\n\n\n')

    for t in final_relations:
        print(t)









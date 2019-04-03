from collections import defaultdict, OrderedDict
from indexer import *
from ontology_stuff import build_onto_objects
from relation_mapping import get_synonyms


class ResultsObject:

    def __init__(self, id, sfari, non_sfari, named_ents, asd_terms):
        self.id = id
        self.sfari = sfari
        self.non_sfari = non_sfari
        self.named_ents = named_ents
        self.asd_terms = asd_terms




def format_results(file):
    results = []
    used = []

    for line in file:
        line = line.strip()
        line = line.replace('Stereotyped, Restricted, and Repetitive Behavior',
                            'Stereotyped Restricted and Repetitive Behavior')
        if line.startswith('PMCID:'):
            p, id = line.split(':')
            sfari_genes = defaultdict(int)
            non_sfari_genes = []
            named_ents = defaultdict(list)
            asd_terms = defaultdict(list)
            final_sfari = {}
            final_non_sfari = {}
        elif not line == "\n":
            if line.startswith('SFARI Genes: '):
                line = line.replace('SFARI Genes: ', '')
                genes = line.strip().split(',')
                for gene in genes:
                    if ":" in gene:
                        gene, count = gene.split(':')
                        sfari_genes[gene.upper()] += int(count.strip())

            if line.startswith('Non SFARI Genes:'):
                line = line.replace('Non SFARI Genes:', '').replace('[', '').replace(']', '')
                genes = line.strip().split(',')
                for gene in genes:
                    gene = gene.upper()
                    non_sfari_genes.append(gene)

            if line.startswith('Named Entities:'):
                line = line.replace("Named Entities: ", '').strip()
                terms = line.split('), (')
                for term in terms:
                    if '[]' not in term:
                        try:
                            term=term.replace("(", '').replace(")",'')
                            ent, label = term.split(': [')
                            label=label.replace(']', '')
                            str = ""
                            labels = label.split(',')
                            for label in labels: str += "{} ".format(semtypes.get(label))
                            named_ents[str].append(ent)
                        except ValueError: pass

            if line.startswith('ASD_Terms:'):
                line = line.replace('ASD_Terms:', '').replace('[', '').replace(']', '')
                terms = line.strip().split(')),')
                for term in terms:
                    if term:
                        term = term.replace("(", '').replace(")", '')
                        term, label = term.split(', ')
                        label = label.replace('"', '')
                        term = term.replace("'", "")
                        asd_terms[label.strip()].append(term.strip())

                if id not in used:
                    r = ResultsObject(id, sfari_genes, non_sfari_genes, named_ents, asd_terms)
                    results.append(r)
                    used.append(id)

    results = list(set(results))
    #
    # for result in results:
    #     print(result.id)
    #     print(result.sfari)
    #     print(result.non_sfari)
    #     for item in result.asd_terms.items():
    #         print(item)

    return results


def gene_count(result_list):
    gene_paper_counts = defaultdict(int)
    gene_mention_count = defaultdict(int)
    gene_score = []


    for result in result_list:
        for g, c in result.sfari.items():
            gene_mention_count[g] += (c)
            gene_paper_counts[g] += 1

    return gene_mention_count, gene_paper_counts


def gene_paper_mentions(result_list):
    gene_paper = defaultdict(list)

    for result in result_list:
        for g, c in result.sfari.items():
            if result.id not in gene_paper[g]:
                gene_paper[g].append(result.id)

    return gene_paper


def group_counts(result_list):
    onto_objects = build_onto_objects()

    def get_obj(classno):
        return next((x for x in onto_objects if x.classnum == classno), None)

    def get_descendants(obj):
        return [get_obj(str(x).replace('asdpto.', '')).label for x in obj.descendants()]

    major_groups = {
        'medical_group': get_descendants(get_obj('Class_154')) + ["'Medical History'"],
        'personal_group': get_descendants(get_obj('Class_152')) + ["'Personal Traits"],
        'social_group': get_descendants(get_obj('Class_153')) + ["'Social Competence'"]
    }

    second_level_group = {
        'comorbid_group': get_descendants(get_obj('Class_365')) + ["'Comorbidities'"],
        'complaints_group': get_descendants(get_obj('Class_406')) + ["'Complaints and Indications'"],
        'diagnosis_group': get_descendants(get_obj('Class_97')) + ["'Diagnosis'"],
        'exposures_group': get_descendants(get_obj('Class_148')) + ["'Exposures'"],
        'perinatal_group': get_descendants(get_obj('Class_385')) + ["'Perinatal History'"],
        'cognitive_group': get_descendants(get_obj('Class_158')) + ["'Cognitive Abilities'"],
        'emotional_group': get_descendants(get_obj('Class_160')) + ["'Emotional Traits'"],
        'executive_group': get_descendants(get_obj('Class_155')) + ["'Executive Function'"],
        'language_group': get_descendants(get_obj('Class_156')) + ["'Language Ability'"],
        'stereo_group': get_descendants(get_obj('Class_166')) + ["'Stereotyped, Restricted, and Repetitive Behavior'"],
        'adaptive_life_group': get_descendants(get_obj('Class_538')) + ["'Adaptive Life Skills'"],
        'interpersonal_group': get_descendants(get_obj('Class_283')) + ["'Interpersonal Interactions'"],
        'social_norm_group': get_descendants(get_obj('Class_66')) + ["'Recognition of Social Norms'"],
    }

    group_mentions = defaultdict(int)

    for result in result_list:
        for asd_term in result.asd_terms:
            for group, descendants in second_level_group.items():
                if asd_term in descendants:
                    group_mentions[group] += 1
                    break

    for group, count in group_mentions.items():
        print("{},{}".format(group, count))


def cluster_results(file):

    num_clusters = 3

    sfari_genes = [x.lower() for x in list(set(itertools.chain.from_iterable(get_synonyms().values())))]
    results = []

    for i in range(0, num_clusters):
        terms = []
        genes = []
        asd = []
        papers = []
        for line in file:
            if line.startswith("Cluster {} words:".format(i)):
                line = line.replace("Cluster {} words:".format(i), "")
                terms = line.strip().split(',')
                terms = [term.replace("b'", "").replace("'", "").replace("_", ' ') for term in terms]
                for term in terms:
                    if term in sfari_genes and term != '':
                        genes.append(term)
                    else:
                        asd.append(term)
            if line.startswith("Cluster {} titles:".format(i)):
                line = line.replace("Cluster {} titles:".format(i), "")
                papers = line.strip().split(', ')

            result = (i, genes, asd, papers)
        results.append(result)

    return results


def cluster():

    cluster_file = open('files/stats/clustering/3_annotated.txt', 'r').readlines()
    res = cluster_results(cluster_file)

    gene_file  = open("files/papers/asd_gene_corpus.txt", 'r').readlines()
    pheno_file  = open("files/papers/asd_pheno_corpus.txt", 'r').readlines()

    gene_papers = [str(paper.id) for paper in reload_corpus(gene_file)]
    pheno_papers = [str(paper.id) for paper in reload_corpus(pheno_file)]


    for cluster in res:
        gene_percent = 0
        pheno_percent = 0
        overlap_percent = 0
        papers = (cluster[3])
        for paper in papers:
            if paper in gene_papers and paper in pheno_papers: overlap_percent += 1
            elif paper in gene_papers: gene_percent += 1
            elif paper in pheno_papers: pheno_percent += 1
        print(cluster[0], len(papers), gene_percent/len(papers), pheno_percent/len(papers), overlap_percent/len(papers))

if __name__=="__main__":



    results = format_results()
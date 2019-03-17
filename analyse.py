import re
import pandas
import numpy
from pubmed_parse import get_geneinfo
from collections import defaultdict
from ontology_stuff import build_onto_objects

class ResultsObject:

    def __init__(self, id, sfari, non_sfari, asd_terms):

        self.id = id
        self.sfari = sfari
        self.non_sfari = non_sfari
        self.asd_terms = asd_terms


def format_results(file):

    results = []
    used = []

    for line in file:
        line = line.strip()
        if line.startswith('PMCID:'):
            p, id = line.split(':')
            sfari_genes = defaultdict(list)
            non_sfari_genes = defaultdict(list)
            asd_terms = defaultdict(list)
            final_sfari = {}
            final_non_sfari = {}
        elif not line == "\n":
            if line.startswith('SFARI Genes:'):
                line = line.replace('SFARI Genes:', '').replace('[', '').replace(']', '')
                genes = line.strip().split(',')
                for gene in genes:
                    if gene:
                        gene = re.sub("'", '', gene)
                        g, count = gene.split(": ")
                        g = re.sub("'", '' , g)
                        g = (g.strip()).upper()
                        sfari_genes[g].append(int(count))

                for gene, counts in sfari_genes.items():
                    if len(counts)>1:
                        final_sfari[gene] = sum(counts)
                    else: final_sfari[gene] = counts[0]

            if line.startswith('Non SFARI Genes:'):
                line = line.replace('Non SFARI Genes:', '').replace('[', '').replace(']', '')
                genes = line.strip().split(',')
                for gene in genes:
                    if gene:
                        gene = re.sub("'", '', gene)
                        g, count = gene.split(": ")
                        g = re.sub("'", '' , g)
                        g = (g.strip()).upper()
                        non_sfari_genes[g].append(int(count))

                for gene, counts in non_sfari_genes.items():
                    if len(counts) > 1:
                        final_non_sfari[gene] = sum(counts)
                    else:
                        final_non_sfari[gene] = counts[0]

            if line.startswith('ASD_Terms:'):
                line = line.replace('ASD_Terms:', '').replace('[', '').replace(']', '')
                terms = line.strip().split(')), ')
                for term in terms:
                    if term:
                        term = term.replace("(", '').replace(")", '')
                        term, label = term.split(', "')
                        term = term.replace("'", '')
                        label = label.replace('"', '')
                        asd_terms[label].append(term)

                if id not in used:
                    r = ResultsObject(id, final_sfari, final_non_sfari, asd_terms)
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
    'social_group' : get_descendants(get_obj('Class_153')) + ["'Social Competence'"]
    }

    second_level_group = {
    'comorbid_group': get_descendants(get_obj('Class_365')) + ["'Comorbidities'"],
    'complaints_group' :get_descendants(get_obj('Class_406')) + ["'Complaints and Indications'"],
    'diagnosis_group': get_descendants(get_obj('Class_97'))+ ["'Diagnosis'"],
    'exposures_group': get_descendants(get_obj('Class_148'))+ ["'Exposures'"],
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

    for k, v in second_level_group.items():
        print(k, v)



    # for result in result_list:
    #
    #     counts = defaultdict(list)
    #
    #     for label, terms in result.asd_terms.items():
    #         print(label, terms)
    #         for group, descendants in second_level_group.items():
    #             if label in descendants:
    #                 counts[group].extend(terms)
    #
    #     print(result.id, len(counts.values()))
    #     print(counts)
    #     print('\n')


if __name__=='__main__':

    results_file = open('files/system_output/gene_output.txt', 'r').readlines()

    results = format_results(results_file)
    gene_counts, paper_counts = gene_count(results)
    gene_mentions = gene_paper_mentions(results)
    group_counts(results)

    # sfari_genes = get_geneinfo()
    # for gene in sfari_genes:
    #     if gene.symbol in gene_counts.keys():
    #         c = gene_counts[gene.symbol]
    #         p = paper_counts[gene.symbol]
    #         mentions = gene_mentions[gene.symbol]
    #     else:
    #         c = 0
    #         p = 0
    #         mentions = []
    #
    #     print(gene.symbol, ',', gene.score, ',', gene.syndromic, ',', c, ',', p )


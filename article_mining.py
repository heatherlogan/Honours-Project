from collections import defaultdict, Counter
from indexer import *
import re

def load_relevant_papers():

    relevant_papers = {}

    file = open('files/relevant_papers.txt', 'r').readlines()

    for line in file:
        classnum, list = line.split(': ')
        papers = (list.strip()).split(',')
        relevant_papers[classnum] = papers

    return relevant_papers


def sort_hgnc():

    # {Approved Symbol: [All synonyms]}
    hgnc_genes = defaultdict(list)

    file = open('files/hgnc.csv', 'r').readlines()

    # ignore pseudogenes(?)

    for line in file:
        if 'pseudogene' in line:
            pass
        else:
            line = line.replace('\n', '').replace('"', '')
            line = line.split(',')
            hgnc_genes[line[0]] = list(filter(None, line))
    return hgnc_genes


def write_mentioned_genes():

    hgnc_genes = sort_hgnc()

    # writes all genes mentioned in paper to a txt file.

    f = open('files/genes_counts_per_paper.txt', 'w')

    article_file = open("files/corpus.txt", 'r').readlines()
    articles = reload_corpus(article_file)

    for art in articles:

        gene_count = Counter()

        text = re.sub('PMC_TEXT: ', '', art.text)
        tokenized_text = re.split("[\W]", text)
        tokenized_text = list(filter(None, tokenized_text))
        joined = " ".join([word.lower() for word in tokenized_text])

        if len(tokenized_text) < 20000:

            for gene, synonyms in hgnc_genes.items():
                for name in synonyms:
                    if name.lower().strip() in joined:
                        gene_count[gene] += 1

            temp = []
            for gene, int in gene_count.items():
                temp.append("{}:{}".format(gene, int))

            string_genecount = str(art.id) + "--" + ', '.join(temp) + "\n"

            f.write(string_genecount)
            print(art.id)

    f.close()


def genecounts_from_paper(pmcid):

    article_file = open("files/corpus.txt", 'r').readlines()
    articles = reload_corpus(article_file)

    # for getting the gene counts from a single paper based on id (dont need atm)
    hgnc_genes = sort_hgnc()
    gene_count = Counter()

    art = next((x for x in articles if x.id == int(pmcid)), None)

    text = re.sub('PMC_TEXT: ', '', art.text)
    tokenized_text = re.split("[\W]", text)
    tokenized_text = list(filter(None, tokenized_text))
    joined = " ".join([word.lower() for word in tokenized_text])

    for gene, synonyms in hgnc_genes.items():
        for name in synonyms:
            if name.lower().strip() in joined:
                gene_count[gene] += 1

    print(pmcid, ":", gene_count)
    return gene_count


def load_gene_families():

    # loads list of gene families from txt file as dictionary

    file = open('files/gene_families.txt', 'r').readlines()

    gene_families = {}
    for line in file:
        family, gene = line.split('\t')
        gene_families[gene.strip()] = family

    return gene_families


def load_genes_per_paper():

    print('loading genes per paper')

    # loads mentioned genes from the text file into form {paper { gene: count}}
    file = open('files/genes_in_papers.txt', 'r').readlines()

    genes_per_paper = {}

    for line in file:
        line = line.strip()
        gene_counts = {}
        paper, genecounts = line.split('--')
        genecounts = genecounts.split(',')
        for item in genecounts:
            item = item.strip()
            if len(item)>0:
                gene, count = item.split(':')
                gene_counts[gene.strip()] = int(count)
        genes_per_paper[paper.strip()] = gene_counts
    return genes_per_paper

genes_per_paper = load_genes_per_paper()

def get_getjoinedcounts(paper_list):

    # gets the total counts of all genes mentioned per paper

    joinedcounts = Counter()

    for paper in paper_list:
        counts = genes_per_paper.get(paper)
        if counts != None:
            for gene, count in counts.items():
                joinedcounts[gene] += count

    return joinedcounts


def match_families(joined_counts):

    # matches the list of gene counts to their families and saves with count

    gene_fams = load_gene_families()
    gene_family_counts = Counter()
    no_family = []

    for gene, count in joined_counts.items():

        family = gene_fams.get(gene)
        if family == None:
            no_family.append(gene)
        else:
            gene_family_counts[family] += count

    return gene_family_counts


def match_genes_to_sfari(gene_list):

    sfari_file = open('files/SFARI_file.csv', 'r').readlines()
    sfari_genes = []
    mentioned_genes= []

    for line in sfari_file:
        line = line.split(',')
        sfari_genes.append(line[1])

    for gene in gene_list:
        if gene in sfari_genes:
            mentioned_genes.append(gene)

    return mentioned_genes


if __name__=="__main__":

    pass
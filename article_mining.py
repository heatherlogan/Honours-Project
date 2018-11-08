from collections import defaultdict, Counter
from indexer import *
import re


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

    # writes all genes mentioned in paper to a txt file.

    f = open('files/genes_per_paper2.txt', 'w')

    article_file = open("files/corpus.txt", 'r').readlines()
    articles = reload_corpus(article_file)
    genes = sort_hgnc()

    count = 107

    for art in articles[107:]:
        text = re.sub('PMC_TEXT: ', '', art.text)
        tokenized_text = re.split("[\W]", text)
        tokenized_text = list(filter(None, tokenized_text))

        print(art.id)

        if len(tokenized_text) < 20000:

            gene_count = Counter()

            for gene, synonyms in genes.items():
                for name in synonyms:
                    if (name.lower().strip()) in tokenized_text:
                        gene_count[gene] += 1

            genelist = list((dict(gene_count)).keys())
            genelist = ', '.join(genelist)
            string = "{}: {}\n".format(art.id, genelist)
            print("\t", count, string)
            f.write(string)
            count += 1

    f.close()


def get_genes_from_papers():

    # reloads txt file and finds genes mentioned in multiple papers.

    f = open('files/genes_per_paper.txt', 'r').readlines()

    mentioned_genes = {}

    for line in f:
        line = line.strip().split(': ')
        paper = line[0]
        genes = line[1].split(', ')
        mentioned_genes[paper] = genes

    all_genes = []
    genes_vs_papers = {}

    for paper, genes in mentioned_genes.items():
        all_genes.extend(genes)

    for gene in all_genes:
        papers = []
        for paper, genes in mentioned_genes.items():
            if gene in genes:
                if paper not in papers:
                    papers.append(paper)
                genes_vs_papers[gene] = papers

    return genes_vs_papers


def match_genes_to_sfari():

    sfari_file = open('files/SFARI_file.csv', 'r').readlines()
    sfari_genes = []
    genes_paper = get_genes_from_papers()

    for line in sfari_file:
        line = line.split(',')
        sfari_genes.append(line[1])

    for gene, papers in genes_paper.items():
        if gene in sfari_genes:
            print(gene, list(set(papers)))


def group_genes_to_families():

    # Sort gene families to {family: [genes]}
    # create new dict for {gene_family: [papers]}
    # special treatment for pseudogenes?
    # leave genes with no family alone
    pass

if __name__=='__main__':

    write_mentioned_genes()
import itertools
import re
from collections import defaultdict


def sort_gene_families():

    file = open('files/gene_families.txt', 'r').readlines()

    gene_families = {}

    for line in file:
        line = line.split('\t')
        family, gene = line[0], line[1]
        gene_families[family] = gene

    return gene_families



if __name__=='__main__':

    sort_gene_families()
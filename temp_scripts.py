# from collections import defaultdict, Counter
# from NER import *
# from nltk.stem.porter import PorterStemmer
# from nltk.stem import WordNetLemmatizer
# from nltk import bigrams, ngrams
# from ontology_stuff import extract_autism_entities
import itertools
from pubmed_parse import *
from main import main_main
from indexer import reload_corpus
import nltk


if __name__=="__main__":

    syns =get_synonyms()
    sfari_genes = [x.upper() for x in list(itertools.chain.from_iterable((syns.values())))]

    file = open("files/re_output.txt", 'r').readlines()

    gene_mentions = defaultdict(list)


    for line in file:
        line2 = line.strip().replace(')', '').replace('(', '').replace("'", '')
        arg1, rel, arg2 = line2.split(', ')
        arg_list = arg1.split() + arg2.split()
        for gene, synonyms in syns.items():
            for arg in arg_list:
                if arg.upper() in synonyms:
                    gene_mentions[gene].append(line.strip())


    for gene, mentions in gene_mentions.items():
        print("\n", gene)
        for t in mentions:
            print('\t', t)
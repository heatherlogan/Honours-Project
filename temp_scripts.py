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

    file = open('files/NER_outputs/output_latest_2.txt', 'r').readlines()
    writefile = open('files/NER_outputs/output_latest.txt', 'w')


    remove = ["[drdd]", "[medd]", "[resd]", "[geoa]", "[enty]", "[food]", "[mnob]", "[phob]",
                   "[bmod]", "[ocac]", "[ocdi]", "[prog]", "[clas]", "[cnce]",
                   "[ftcn]", "[idcn]", "[ipro]", "[qlco]", "[gora]", "[rnlw]", "[spco]", "[tmco]",
                   "[qnco]", "[inpr]","[popg]"]

    for line in file:
        for type in remove:
            if type in line:
                line = ""
                break
        if line != "": writefile.write(line)
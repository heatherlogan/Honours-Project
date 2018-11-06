import numpy as np
import sys
from itertools import chain
from string import digits
from indexer import *
from stemming.porter2 import stem
from Bio import Entrez
from make_corpus import find_name

indexed_file = open('files/corpus_index.txt', 'r').readlines()

docnumbers = []


def format_txt_file():

    # Loads indexed file back into a list of dictionary items [{term: {document:[positions]}}...]

    index_list = []
    term_list = []
    for line in indexed_file:
        position = {}
        index = {}
        if line.endswith(':\n'):
            term = line.replace(':', '').strip()
            term_list.append(term)
        if line.startswith('\t'):
            split_position = (line.replace('\t', '').replace('\n','').replace(' ', '')).split(':')
            docno, position_list2 = split_position[0], split_position[1]
            idxs = list(map(int, position_list2.split(',')))
            position[int(docno)] = idxs
            docnumbers.append(docno)

        if len(position)>0:
            index[term] = position
            index_list.append(index)
    return index_list


# load index
inverted_index = format_txt_file()


def preprocess_term(term):
    return re.sub(r'\W+', '', stem(term.lower()))


def getpositions(term):

    # For a term, retrieves a list of all positions from the inverted index.
    position_list = []
    for index in inverted_index:
        if term in index.keys():
            position_list.append(index.get(term))

    return position_list


def getnot(lst):

    # takes list of documents and returns the all documents in collection except those in list.
    all_docs = sorted(list(set(docnumbers)))
    return [n for n in ([int(x) for x in all_docs]) if n not in lst]


def get_docs(position_list):

    # extracts the documents from a list of {doc:[position]} dictionaries
    docs = []
    for position in position_list:
        for key in position.keys():
            docs.append(key)
    return docs


def rankedir_search(query):

    # gets list of positions for each term in the query and calculates tfidf score for each document

    query = query.split(' ')
    N = len(list(set(docnumbers)))
    tfidfs = {} # Dictionary to store {docnumber: tfidf score}

    def tfidf(tf, df):
        return (1 + np.log10(tf)) * (np.log10(N/df))

    for term in query:
        term = preprocess_term(term)
        positions = getpositions(term)
        docfreq = len(positions)

        for position in positions:
            for doc in position:
                termfreq = len(position[doc])
                t = tfidf(termfreq, docfreq)

                if doc not in tfidfs.keys():
                    tfidfs[doc] = t
                else:
                    newval = tfidfs[doc] + t
                    tfidfs[doc] = newval
    return tfidfs


# Query in list format, preprocesses

def parsequery(queryno, query):

    results = rankedir_search(query)
    results_c = results.copy()
    for doc, score in results_c.items():
        if score == 0.0:
            results.pop(doc)
    results = (sorted(results.items(), key=lambda kv: kv[1], reverse=True))

    return results[:5]


def query_idx(query_file):

    f = open('files/ontology_results.txt', 'w')

    for query in query_file:
        queryno = int(query.split()[0])
        query = query.lstrip(digits).strip()
        headline, description = (query.split('\n'))
        results = parsequery(queryno, query)

        str1 = '{}\nLABEL: {}\nDESCRIPTION: {}\nTOP 5 RELEVANT PAPERS:'.format(queryno, "".join(headline.strip()), (description.strip()))

        print(str1)
        f.write(str1 + "\n")

        for (id, score) in results:

            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={}&tool=my_tool&email=heather_logan@live.co.uk".format(id)
            headline = find_name(id)
            str2 = '\tPMC ID: {}\n\tHEADLINE: {}\n\tLINK: {}\n\tTFIDF SCORE: {}\n\t*********'.format(id, headline, url, round(score, 3))

            print(str2)
            f.write(str2 + "\n")

    f.close()


if __name__=='__main__':

    query_file = open(sys.argv[1], 'r').readlines()
    query_idx(query_file)
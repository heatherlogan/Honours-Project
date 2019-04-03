import numpy as np
from stemming.porter2 import stem
import re
from graph import *

def format_txt_file():

    print('formatting index file')

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

    print('index loaded')
    return index_list


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

    def idf(df):
        return np.log10(N / df)

    for term in query:
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

def frequencies(term):
    # gets list of positions for each term in the query and calculates tfidf score for each document
    N = len(list(set(docnumbers)))

    term = preprocess_term(term)
    positions = getpositions(term)
    docfreq = len(positions)

    termfreqsum = 0
    for position in positions:
        for doc in position:
            print(doc)
            termfreqsum += len(position[doc])

    return docfreq, termfreqsum


def parsequery(query):

    results = rankedir_search(query)
    results_c = results.copy()
    for doc, score in results_c.items():
        if score == 0.0:
            results.pop(doc)

    results = sorted(results.items(), key=lambda kv: kv[1], reverse=True)

    cutoff = 0.5

    if len(results)>0:
        max = results[0][1]
        results_filtered = [(x,y) for (x,y) in results if y>max*cutoff]

    return results, results_filtered


if __name__=='__main__':

    indexed_file = open('files/indexer/annotated_index.txt', 'r').readlines()
    docnumbers = []

    inverted_index = format_txt_file()


    querys = list(set([list(x.keys())[0] for x in inverted_index]))

    counts_full = []
    total = 0
    counts_filtered = []
    for query in querys:
        res, res_filter = parsequery(query)
        total += len(res)
        print(query, len(res))

    print(total)
    #
    #
    # for tag, count1, count2 in counts_full:
    #     tag2 = " ".join(x.capitalize() for x in tag.split("_"))
    #     print("{},{},{},{}".format(tag2, get_group(tag), count1, count2))
    #





    # count_dict = {}

    # write_file = open('files/stats/sfaricounts_gene_papers.csv', 'w')
    # write_file.write("gene, score, syndromic, docs_appeared, number_mentions \n")
    #
    # for gene in sfari_genes:
    #     syns = list(set(synonyms.get(gene.symbol)))
    #     total_docs = 0
    #     total_freq = 0
    #     for syn in syns:
    #         docfreq, termfreq = frequencies(syn)
    #         total_docs += docfreq
    #         total_freq += termfreq
    #     write_file.write("{}, {}, {}, {}, {}\n".format(gene.symbol, gene.score, gene.syndromic, total_docs, total_freq))
    #     print(gene.symbol, gene.score, gene.syndromic, total_docs, total_freq, list(set(synonyms.get(gene.symbol))))
    #
    # write_file.close()




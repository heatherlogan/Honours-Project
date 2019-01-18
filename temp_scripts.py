import itertools
import random
import re
from collections import defaultdict
from indexer import reload_corpus
from named_entity_recognition import *

def sort_gene_families():

    file = open('files/gene_families.txt', 'r').readlines()

    gene_families = {}

    for line in file:
        line = line.split('\t')
        family, gene = line[0], line[1]
        gene_families[family] = gene

    return gene_families



def sort_hgnc():

    file = open('files/hgnc.txt', 'r')
    w_file = open('files/hgnc_sorted.txt', 'w')

    sorted = defaultdict(list)

    for line in file:
        line = line.strip().split('\t')
        line = list(filter(None, line))
        sorted[line[0]].extend(line)

    for k, v in sorted.items():
        print(k, list(set(v)))
        w_file.write("{}: {}\n".format(k, ', '.join(list(set(v)))))
    w_file.close()


def sort_diseases():

    file = open('files/disease_db.txt', 'r')

    r_file = open('files/diseases.txt', 'w')

    diseases = []
    for line in file:
        line = line.strip().split('\t')
        line = list(filter(None, line))
        diseases.append(line[3])

    diseases = sorted(list(set(diseases)))
    for disease in diseases:
        r_file.write(disease + "\n")


def write_abstracts():

    file = open('files/corpus_cleaned.txt', 'r').readlines()
    articles = reload_corpus(file)

    abstracts = []

    for article in articles:

        if article.abstract != "" and len(article.abstract) > 1000 and len(article.abstract) < 1500:

            abstracts.append(article)

    random.shuffle(abstracts)

    return abstracts[:30]


def clean_ent(entity):

    cleaned = re.sub(r'[^a-zA-Z0-9\-._/\s]', '',entity)
    return cleaned.strip().lower()


def corpus_entities():

    hgnc_genes = load_hgnc()

    softTFIDF = sm.SoftTfIdf()

    file = open('files/corpus_cleaned.txt', 'r').readlines()
    articles = reload_corpus(file)

    all_ents = []

    for i, article in enumerate(articles):

            text = article.abstract.strip() + article.text.strip()
            entities = entity_extract(text, 'default')
            entities2 = [clean_ent(entity) for entity in entities if not all(x.isalpha() for x in entity)]
            print(entities2)
            print('\t', i,  len(entities), len(entities2))
            all_ents.append(entities2)

    all_ents = list(nltk.chain.from_iterable(all_ents))
    common_ents = list(set(all_ents))

    print(len(all_ents), len(common_ents))

    file2 = open("files/corpus_entities.txt", 'w')

    common_ents = sorted(common_ents)

    for ent in common_ents:
        file2.write("{}\n".format(ent))



def clean_corpus_entities():

    file = open('files/corpus_entities.txt', 'r')
    file2 = open("files/corpus_entities.txt", 'w')
    entities = []
    for line in file:
        entities.append(line.strip())
    cleaned_ents = []
    for entity in entities:

        if any([x in entity for x in ['www.', '.nih', '.gov', '.ca', '.net', '.co.uk', '.com', '.edu', '.org', '.ac.uk']]):
            pass
        else:
            if any([entity.startswith(x) for x in ['-', '/', '//', '-', '.']]):
                entity = entity[1:]
            cleaned_ents.append(entity.strip())
    print(cleaned_ents)
    print(len(list(set(cleaned_ents))))

    for c in sorted(cleaned_ents):

        file2.write("{}\n".format(c))

if __name__=="__main__":

    clean_corpus_entities()



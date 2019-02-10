from collections import defaultdict, Counter
from named_entity_recognition import *
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import bigrams, ngrams
from ontology_stuff import extract_autism_entities

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


def write_entities():

    file = open('files/corpus_cleaned.txt', 'r').readlines()

    write_file = open('files/abstract_common_entities.txt', 'w')

    articles = reload_corpus(file)

    abstracts = [a.abstract for a in articles if a.abstract]

    all_entites = []

    for i, abs in enumerate(abstracts):

        print(i)
        all_entites.append([k.lower() for k, v in entity_extract(abs, 'default').items()])

    counter = Counter()
    all_entites = list(itertools.chain.from_iterable(all_entites))

    for ent in all_entites:
        counter[ent] += 1

    lst = [c[0] for c in counter.most_common(500)]

    print(sorted(lst))

    for l in sorted(lst):
        write_file.write("{}\n".format(l))

    # 60675 all entities
    # 32187 corpus entities

    write_file.close()


def condense_entities():

    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    entities = []
    stemmed = []
    lemmatized = []

    file = open('files/abstract_common_entities.txt', 'r')

    for line in file:
        ent = line.strip()
        entities.append(ent)
        stemmed.append(stemmer.stem(ent))
        lemmatized.append(lemmatizer.lemmatize(ent))

    stemmed_file = open('files/entities_stemmed.txt', 'w')
    lemmatized_file = open('files/entities_lemmatized.txt', 'w' )

    for ent in sorted(list(set(stemmed))):
        print(ent)
        stemmed_file.write("{}\n".format(ent))

    print(" ")

    for ent in sorted(list(set(lemmatized))):
        print(ent)
        lemmatized_file.write("{}\n".format(ent))


    stemmed_file.close()
    lemmatized_file.close()


def autism_terms():

    onto_labels = extract_autism_entities()
    terms = []

    for o in onto_labels:
        o = o.lower()
        fltr = [word for word in o.split() if word not in stopwords]
        bi = list(bigrams(fltr))
        terms.append(o)
        for o1 in fltr:
            terms.append(o1)
        for b in bi:
            terms.append(' '.join(b))

    return sorted(list(set(terms)))


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


if __name__=="__main__":

    lemmatiz = WordNetLemmatizer()
    stemmer = PorterStemmer()

    asd_terms = autism_terms()

    stemmed_terms = []

    file = open("files/asd_terms.txt", 'w')

    for term in asd_terms:
        stemmed = ""
        for word in term.split():
            stem = lemmatiz.lemmatize(word)
            stemmed += stem + " "
        stemmed_terms.append(stemmed)

    stemmed_terms = sorted(list(set(stemmed_terms)))

    for stem in stemmed_terms:
        print(stem)
        file.write("{}\n".format(stem))
    file.close()

    #
    # test_terms = ["ASD", "poor social skills", "conceptual empathy", "socially awkward", "fragile-X syndrome", "social ability", "aggressiveness"]
    #
    #
    # for term in test_terms:
    #     stemmed = ""
    #     for word in term.split():
    #         stem = stemmer.stem(word)
    #         stemmed += stem + " "
    #
    #     print(term, "\t", stemmed)
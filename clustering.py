import operator
import re
from analyse import format_results
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import ward, dendrogram
from collections import defaultdict
from indexer import reload_corpus, stopwords
from pubmed_parse import get_synonyms
import nltk


class ClusterFormat:
    def __init__(self, id, contents):
        self.id = id
        self.contents = contents


def titles_years():

    year_file = open('files/paper_info/all_dates.txt', 'r').readlines()
    title_file = open('files/paper_info/pheno_titles.txt', 'r').readlines()

    years = {}
    for year in year_file:
        paper, year = year.strip().split('\t')
        years[paper.replace("PMC", '').strip()] = year.strip()

    titles = {}
    for title in title_file:
        paper, title = title.strip().split('\t')
        titles[paper] = title

    return years, titles


def format_for_clustering(results):

    cluster_format = []
    years, titles = titles_years()

    for r in results:
        contents = ""
        year = years.get(str(r.id))
        title = titles.get(str(r.id))

        for gene, count in r.sfari.items():
            if gene not in ['an', 'met', 'kit', 'cage', 'trio','mark']:
                contents += "{}, ".format(gene)

        for label, terms in r.asd_terms.items():
            label = label.replace(" ", "_").replace("'", "").replace(",", '').lower()
            contents += "{}, ".format(label)

        newc = ClusterFormat(r.id, contents)
        cluster_format.append(newc)

    return cluster_format


def preprocess(article_list):

    def prep(text):

        preprocessed = []
        text = nltk.word_tokenize(text.lower())

        for word in text:
            if word not in stopwords:
                preprocessed.append(word)

        return preprocessed

    formatted = []

    for article in article_list:
        text = prep(article.abstract + article.text)
        newc = ClusterFormat(article.id, text)
        formatted.append(newc)

    return formatted


def tfidf_vector(results):

    pmcids = [c.id for c in results]
    contents = [c.contents for c in results]

    def tokenize(text):
        tokenized = []
        text = text.split(',')
        for t in text:
            if t != '' and t != ' ':
                tokenized.append(t.strip().lower())
        return tokenized

    def tokenize_only(text):
        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        return filtered_tokens


    total_vocab = []

    for content in contents:
        total_vocab.extend(tokenize(content))

    total_vocab = list(set(total_vocab))

    vocab_frame = pd.DataFrame({'words': total_vocab}, index=total_vocab)
    print('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')

    print('building matrix')
    tfidf_vectorizer = TfidfVectorizer(use_idf=True, tokenizer=tokenize,
                                       min_df=0.05,  max_df=0.8)
    print('building matrix')
    tfidf_matrix = tfidf_vectorizer.fit_transform(contents) #fit the vectorizer to synopses
    print('building matrix')

    features = tfidf_vectorizer.get_feature_names()
    dist = 1 - cosine_similarity(tfidf_matrix)

    return tfidf_matrix, features, dist, vocab_frame


def Kmeans(results, tfidf_matrix, features, dist, vocab_frame ):

    pmcids = [c.id for c in results]
    contents = [c.contents for c in results]

    # kmeans

    num_clusters = 3
    print('starting kmeans')
    kmeans = KMeans(n_clusters=num_clusters)
    print('fitting kmeans')
    kmeans.fit(tfidf_matrix)

    clusters = kmeans.labels_

    papers = {'id': pmcids, 'contents': contents, 'cluster': clusters}
    frame = pd.DataFrame(papers, index=[clusters], columns = ['id', 'cluster'])
    print(frame['cluster'].value_counts())

    # terms per cluster
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

    for i in range(num_clusters):
        print("\nCluster %d words:" % i, end='')

        for ind in order_centroids[i, :30]:
            print('{}'.format(vocab_frame.ix[features[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore')),
                  end=',')
        print()

        print("Cluster %d titles:" % i, end='')
        for title in frame.ix[i]['id'].values.tolist():
            print(' %s,' % title, end='')
        print()  # add whitespace
        print()  # add whitespace

    # visualise
    print('plotting')
    MDS()
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=1)
    pos = mds.fit_transform(dist)
    xs, ys = pos[:, 0], pos[:, 1]

    cluster_colors = {0: '#16A085', 1: '#EC7063', 2:'#7C1AA6', 3: '#62b3c4',
                      4: '#BB8FCE', 5: '#103642',
                      6: '#005860'}

    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=["" for x in pmcids]))

    groups = df.groupby('label')

    fig, ax = plt.subplots(figsize=(17, 9))  # set size
    ax.margins(0.05)

    for name, group in groups:
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=12, label=name,
                mec='none', color=cluster_colors[name])
        ax.set_aspect('auto')

    ax.legend(numpoints=1)  # show legend with only 1 point
    #
    # for i in range(len(df)):
    #     ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'], size=8)

    # plt.savefig('files/stats/clustering/rawtext_3_clusters.png', dpi=200)  # save figure as ward_clusters

    plt.show()

    plt.close()


def heirarchical_clustering(formatted, tfidf_matrix, features, dist, vocab_frame):

    c = ['#16A085', 'EC7063' ]

    print('beginning hierarchical')
    linkage_matrix = ward(dist)

    fig, ax = plt.subplots(figsize=(15, 20))  # set size
    ax = dendrogram(linkage_matrix,
                    orientation="right",
                    no_labels=True,
                    link_color_func=lambda k: '#686868')

    plt.tick_params( \
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')

    plt.tight_layout()  # show plot with tight layout

    plt.show()

    plt.savefig('files/stats/full_corpus_histo.png', dpi=200)  # save figure as ward_clusters


def word_co_occurrence(results):

    # https://marcobonzanini.com/2015/03/23/mining-twitter-data-with-python-part-4-rugby-and-term-co-occurrences/

    com = defaultdict(lambda: defaultdict(int))
    for result in results:
        terms_only = list(set(result.contents.split(', ')))
        terms_only = [x.strip() for x in terms_only if x != '' and x != ' ']
        for i in range(len(terms_only) - 1):
            for j in range(i + 1, len(terms_only)):
                w1, w2 = sorted([terms_only[i], terms_only[j]])
                if w1 != w2:
                    com[w1][w2] += 1

    com_max = []
    # For each term, look for the most common co-occurrent terms
    for t1 in com:
        t1_max_terms = sorted(com[t1].items(), key=operator.itemgetter(1), reverse=True)[:5]
        for t2, t2_count in t1_max_terms:
            com_max.append(((t1, t2), t2_count))
    # Get the most frequent co-occurrences
    terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)

    common = ['learning_disorders', 'reciprocal_social_interaction', 'stereotyped_restricted_and_repetitive_behavior',
              'cognitive_ability', 'diagnosis']

    write = open('files/stats/counts/co_occurrence.csv', 'w')
    write.write('term, term, count\n')
    for (t1, t2), count in terms_max:
        if t1 in sfari_genes and t2 not in sfari_genes and count >1:
            write.write('{}, {}, {}\n'.format(t1, t2, count))



def analyse_gene_pheno():

    file = open('files/stats/counts/co_occurrence.csv', 'r').readlines()
    pheno_inf = defaultdict(list)
    for line in file[1:]:
        gene, pheno, count = line.strip().split(', ')
        pheno_inf[pheno].append((gene, count))

    for pheno, details in pheno_inf.items():
        if len(details)>10:
            print(pheno, [x for x,y in details][:10])
        else:
            print(pheno, details)



if __name__=="__main__":

    analyse_gene_pheno()

    sfari_genes = list(get_synonyms().keys())

    results_file = open('files/system_output/full_corpus_output.txt', 'r').readlines()
    corpus_file = open('files/papers/full_corpus.txt', 'r').readlines()

    # corpus = reload_corpus(corpus_file)
    # joined_corpus = [ClusterFormat(r.id, r.abstract) for r in corpus]

    annotations = format_for_clustering(format_results(results_file))
    # all_annotations = []
    #
    # for i in annotations: all_annotations.append(i.contents)
    #
    # dictionary = corpora.Dictionary(all_annotations)
    # corpus = [dictionary.doc2bow(annotation) for annotation in all_annotations ]

    tfidf_matrix, features, dist, vocab_frame = tfidf_vector(annotations)
    print(tfidf_matrix.shape, dist.shape)
    # print(features)

    Kmeans(annotations, tfidf_matrix, features, dist, vocab_frame)
    heirarchical_clustering(annotations, tfidf_matrix, features, dist, vocab_frame)
    plt.close()

import inline as inline
import matplotlib as matplotlib
from analyse import format_results
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd
import os  # for os.path.basename
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import ward, dendrogram

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
            contents += "{}, ".format(gene) * count
        for label, terms in r.asd_terms.items():
            label = label.replace(" ", "_").replace("'", "").replace(",", '').lower()
            contents += "{}, ".format(label) * len(terms)

        newc = ClusterFormat(r.id, contents)
        cluster_format.append(newc)

    return cluster_format


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

    total_vocab = []
    for content in contents:
        total_vocab.extend(tokenize(content))

    vocab_frame = pd.DataFrame({'words': total_vocab}, index=total_vocab)

    tfidf_vectorizer = TfidfVectorizer(use_idf=True, tokenizer=tokenize, min_df=0.05,  max_df=0.7)
    tfidf_matrix = tfidf_vectorizer.fit_transform(contents) #fit the vectorizer to synopses
    features = tfidf_vectorizer.get_feature_names()
    dist = 1 - cosine_similarity(tfidf_matrix)

    return tfidf_matrix, features, dist, vocab_frame


def Kmeans(results, tfidf_matrix, features, dist, vocab_frame ):

    pmcids = [c.id for c in results]
    contents = [c.contents for c in results]

    # kmeans

    num_clusters = 9
    kmeans = KMeans(n_clusters=num_clusters)
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

    MDS()
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=1)
    pos = mds.fit_transform(dist)
    xs, ys = pos[:, 0], pos[:, 1]

    cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e', 5: '#483d8b'}

    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=["" for x in pmcids]))

    groups = df.groupby('label')

    fig, ax = plt.subplots(figsize=(17, 9))  # set size
    ax.margins(0.05)


    for name, group in groups:
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
                mec='none')
        ax.set_aspect('auto')


    ax.legend(numpoints=1)  # show legend with only 1 point

    for i in range(len(df)):
        ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'], size=8)

    # plt.savefig('files/stats/gene_clusters.png', dpi=200)  # save figure as ward_clusters


    plt.show()

    plt.close()



def heirarchical_clustering(formatted, tfidf_matrix, features, dist, vocab_frame):

    linkage_matrix = ward(dist)

    fig, ax = plt.subplots(figsize=(15, 20))  # set size
    ax = dendrogram(linkage_matrix, orientation="right");

    plt.tick_params( \
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')

    plt.tight_layout()  # show plot with tight layout

    plt.show()

    plt.savefig('files/stats/gene_clusters_histo.png', dpi=200)  # save figure as ward_clusters




if __name__=="__main__":


    results_file = open('files/system_output/gene_output.txt', 'r').readlines()

    results = format_results(results_file)

    formatted = list(set(format_for_clustering(results)))

    tfidf_matrix, features, dist, vocab_frame = tfidf_vector(formatted)

    Kmeans(formatted, tfidf_matrix, features, dist, vocab_frame)

    # heirarchical_clustering(formatted, tfidf_matrix, features, dist, vocab_frame)

    plt.close()



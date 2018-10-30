import re
import itertools
from nltk.corpus import stopwords
from stemming.porter2 import stem

stopwords = list(set(stopwords.words('english')))

class Article:

    def __init__(self, id, headline, text):
        self.id = id
        self.headline = headline
        self.text = text


def reload_corpus():

    print("\nloading corpus..")
    file = open('files/corpus.txt', 'r').readlines()

    id_indexes = [i for i, x in enumerate(file) if re.match("PMC_ID: ", x)]
    end_indexes = [i for i, x in enumerate(file) if re.match(":PMC_ENDTEXT", x)]
    start_end = list(zip(id_indexes, end_indexes))
    articles = []
    article_list = []
    count = 0

    for i in start_end:
        article = []
        a,b = i
        for line in file[a:b]:
            article.append(line)
        article_list.append(article)

    for article in article_list:
        id = ""
        headline = ""
        text = []
        for line in article:
            if re.match('PMC_ID: ', line):
                id = re.sub('PMC_ID: ', '', line)
                id = id.strip()
            if re.match('PMC_HEADLINE: ', line):
                headline = re.sub('PMC_HEADLINE: ', '', line)
            if re.match('PMC_TEXT: ', line):
                idx1 = article.index(line)

        for line in article[idx1:]:
            text.append(line)

        text = (list(itertools.chain(text)))
        new_article = Article(int(id), headline, " ".join(text))
        articles.append(new_article)
        count += 1

    print("corpus loaded")
    return articles


def build_index(article_objects):

    print("\nbuilding index..\n")

    inv_index = []
    ignored_articles = []
    count = 0

    for article in article_objects:

        pattern = "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})"

        text = re.sub(r'\[.*?\]', '', article.text)
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'{}'.format(pattern), '', text)

        tokenized_text = re.split("[\W]", text)
        tokenized_text = filter(None, tokenized_text)

        processed_text = []

        for word in tokenized_text:
            word = word.lower()
            if word not in stopwords and not word.isdigit():
                processed_text.append(stem(word))

        index_per_article = []
        word_count = 0

        # Remove docs > 20000 long as they were taking to long to index

        if len(processed_text) < 20000:

            for word in processed_text:
                word_occurrences = {}
                term_obj = {}
                positions = [i + 1 for i, x in enumerate(processed_text) if x == word]
                word_occurrences[article.id] = positions
                term_obj[word] = word_occurrences
                if term_obj not in index_per_article:
                    index_per_article.append(term_obj)
                word_count += 1
                print("\t", count, article.id, ": ", word_count * 100 / len(processed_text), "%")
            count += 1
            print(count, article.id)

        else:
            ignored_articles.append(article)

        inv_index.append(index_per_article)

    print("sorting index..")
    inv_index = list(itertools.chain.from_iterable(inv_index))
    inv_index.sort(key=lambda d: sorted(d.keys()))
    inv_index = itertools.groupby(inv_index, key=lambda x: sorted(x.keys()))

    # Format and save to index file

    f = open('files/corpus_index.txt', 'w')

    for word, positions in inv_index:
        string_word = "{}:\n".format(''.join(word))
        f.write(string_word)
        list_positions = []
        for x in list(positions):
            for key, v in x.items():
                list_positions.append(v)
        for item in list_positions:
            for doc, pos in item.items():
                f.write("\t{}: {}\n".format(doc, (','.join(map(str, pos)))))
        f.write('\n')

    print("indexing complete\n")
    f.close()

    f2 = open('files/ignored_articles.txt', 'w')

    for article in ignored_articles:
        f2.write("{}: {}" .format(article.id, article.headline))
    f2.close()


if __name__=="__main__":

    articles = reload_corpus()
    build_index(articles)
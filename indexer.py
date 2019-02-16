import re
import itertools
from nltk.corpus import stopwords

stopwords = list(set(stopwords.words('english')))

class Article:

    def __init__(self, id, headline, abstract, text):
        self.id = id
        self.headline = headline
        self.abstract = abstract
        self.text = text


def reload_corpus(file):

    print("\nloading corpus..")

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
        abstract = []
        text = []
        idx_a = 0

        for line in article:

            if re.match('PMC_ID: ', line):
                id = re.sub('PMC_ID: ', '', line)
                id = id.strip()
            if re.match('PMC_HEADLINE: ', line):
                headline = re.sub('PMC_HEADLINE: ', '', line)
            if re.match('PMC_ABSTRACT: ', line):
                idx_a = article.index(line)
            if re.match('PMC_TEXT: ', line):
                idx1 = article.index(line)
        if idx_a != 0:
            for line in article[idx_a:idx1]:
                abstract.append(line)
        else:
            abstract = ""

        for line in article[idx1:]:
            text.append(line)

        if abstract:
            abstract = " ".join(abstract)
            abstract = re.sub("Background\n", "", abstract)
            abstract = re.sub("Aim\n", "", abstract)
            abstract = re.sub("Method\n", "", abstract)
            abstract = re.sub("Results\n", "", abstract)
            abstract = re.sub("Case Presentation\n", "", abstract)
            abstract = re.sub("Limitations\n", "", abstract)
            abstract = re.sub("Conclusions\n", "", abstract)
            abstract = re.sub("PMC_ABSTRACT: ", "", abstract)

        if len(text) == 0:
            count += 1
        else:
            text = (list(itertools.chain(text)))
            text = " ".join(text)
            text = re.sub("PMC_TEXT: ", "", text)
            text = re.sub("\n", '', text)

            if len(text) == 1:
                count += 1
            else:
                new_article = Article(int(id), headline, abstract, text.strip())
                articles.append(new_article)

    print("corpus loaded")

    #returns article objects

    return articles


def build_index(article_objects):

    print("\nbuilding index..\n")

    inv_index = []
    ignored_articles = []
    count = 0

    for article in article_objects:

        pattern = "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})"

        text = re.sub(r'\[.*?\]', '', article.text)
        text = re.sub(r'{}'.format(pattern), '', text)

        tokenized_text = re.split("[\W]", text)
        tokenized_text = filter(None, tokenized_text)

        processed_text = []

        for word in tokenized_text:
            word = word.lower()
            if word not in stopwords and not word.isdigit():
                processed_text.append((word))

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

    f = open('files/index.txt', 'w')

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


def clean_corpus(): #removes failed articles with no text

    file = open('files/corpus.txt', 'r').readlines()
    cleaned = open('files/corpus_cleaned.txt', 'w')
    failed_ids = open('files/failed_ids.txt', 'w')
    articles = reload_corpus(file)
    # build_index(articles)

    count = 0
    for article in articles:
        if article.text == "" or article.text == "\n" or article.text == None:
            str = "{}\t{}\n".format(article.id, article.text)
            failed_ids.write(str)
        else:
            id = "PMC_ID: {}\n".format(article.id)
            head = "PMC_HEADLINE: {}\n".format(article.headline)
            if article.abstract:
                abstract = "PMC_ABSTRACT: {}:\n".format(article.abstract)

            body = "PMC_TEXT: {} \n:PMC_ENDTEXT\n\n".format(article.text)

            cleaned.write(id)
            cleaned.write(head)
            if article.abstract:
                cleaned.write(abstract)
            cleaned.write(body)
            count += 1

    print(count)


if __name__=="__main__":

    file = open('files/papers/include_papers.txt', 'r').readlines()
    articles = reload_corpus(file)

    for article in articles:
        print(article.headline)


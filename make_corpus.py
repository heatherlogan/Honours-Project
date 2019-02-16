from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup


class Article:

    def __init__(self, pmcid, title, abstract, text):
        self.pmcid = pmcid
        self.title = title
        self.abstract = abstract
        self.text = text


def format_article(url):
    article_title = ""

    # grab page
    q = Request(url)
    uclient = urlopen(q)
    page_html = uclient.read()
    uclient.close()
    try:
    # html parsing
        page_soup = soup(page_html, "html.parser")
        pmcid = page_soup.find("article-id", {"pub-id-type":"pmc"})
        pmcid = pmcid.text
        title = page_soup.find_all("title-group")

        for t in title:
            t2 = t.find_all("article-title")
            all = []
            for t3 in t2:
                all.append(t3.text)
            article_title = all[0]

        abstract = page_soup.find("abstract").text
        body = page_soup.find("body")
        sections = body.find_all("sec")

        article_text = []

        for section in sections:
            # Prevents duplicates for nested sections
            if section.find('sec') is not None:
                para = section.find('p') # only finds first p (fix later)
                article_text.append(para.text)
            else:
                paragraphs = section.find_all("p")
                for para in paragraphs:
                    # [s.extract() for s in para.find_all('sup')]
                    # [s.decompose() for s in para('xref')] # removing references
                    article_text.append(para.text)

    except AttributeError:

        abstract = ""
        article_text = ""

    return Article(pmcid, article_title, abstract, ' '.join(article_text))


def build_corpus(url_file):

    urls = url_file.split('\n')
    corp = open('files/papers/include_papers.txt', 'w')
    count = 0

    for url in urls:

        obj = format_article(url)

        id = "PMC_ID: {}\n".format(obj.pmcid)
        head = "PMC_HEADLINE: {}\n".format(obj.title)
        if obj.abstract:
            abstract = "PMC_ABSTRACT: {}:\n".format(obj.abstract)
        body = "PMC_TEXT: {} \n:PMC_ENDTEXT\n\n".format(obj.text)

        corp.write(id)
        corp.write(head)
        if obj.abstract:
            corp.write(abstract)
        corp.write(body)

        count += 1
        print(count, obj.pmcid)

    corp.close()


def find_name(id):

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={}&tool=my_tool&email=heather_logan@live.co.uk".format(id)
    article_title= ""

    # grab page
    q = Request(url)
    uclient = urlopen(q)
    page_html = uclient.read()
    uclient.close()

    # html parsing
    page_soup = soup(page_html, "html.parser")
    pmcid = page_soup.find("article-id", {"pub-id-type":"pmc"})
    title = page_soup.find_all("title-group")

    for t in title:
        t2 = t.find_all("article-title")
        all = []
        for t3 in t2:
            all.append(t3.text)
        article_title = all[0]

    return article_title





if __name__=="__main__":

    url_file = open('files/papers/include_urls.txt', 'r').read()
    build_corpus(url_file)





from pubmed_parse import *
from itertools import chain
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup
import re
from xml.dom import minidom
import os
import sys

class Article:

    def __init__(self, pmcid, title, text):
        self.pmcid = pmcid
        self.title = title
        self.text = text


def format_article(url):
    obj = []
    article_title=""

    # grab page
    q = Request(url)
    uclient = urlopen(q)
    page_html = uclient.read()
    uclient.close()

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

    sections = page_soup.find_all("sec")
    article_text = []
    for section in sections:
        paragraphs = section.find_all("p")
        para_text = []
        for para in paragraphs:
            para_text.append((para.text))
            p = para.text
        article_text.append(' '.join(para_text))

    return Article(pmcid, article_title, ' '.join(article_text))


def build_corpus():

    url_file = open('files/url_list.txt', 'r').read()
    urls = url_file.split('\n')
    corp = open('files/corpus.txt', 'w')

    count = 0

    for url in urls:
        obj = format_article(url)

        id = "PMC_ID: {}\n".format(obj.pmcid)
        head = "PMC_HEADLINE: {}\n".format(obj.title)
        body = "PMC_TEXT: {} \n:PMC_ENDTEXT\n\n".format(obj.text)

        corp.write(id)
        corp.write(head)
        corp.write(body)

        count += 1
        print(count, obj.pmcid)

    corp.close()


def find_name(id):

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={}&tool=my_tool&email=heather_logan@live.co.uk".format(id)

    obj = []
    article_title= ""

    # grab page
    q = Request(url)
    uclient = urlopen(q)
    page_html = uclient.read()
    uclient.close()

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

    return article_title


if __name__=="__main__":

    build_corpus()

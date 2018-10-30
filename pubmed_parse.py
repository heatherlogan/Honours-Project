from Bio import Entrez
import json
import csv

emailstring = 'heather_logan@live.co.uk'
file = open("files/SFARI_file.csv", 'r').readlines()

def search_pub(query):
    Entrez.email = emailstring

    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax='20',
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results


def search_pmc(query):
    Entrez.email= emailstring

    handle = Entrez.esearch(db='pmc', term=query)

    results = Entrez.read(handle)
    return results


def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = emailstring
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results


def query_pubmed(symbol, name, querytype):
    gene_papers = "{}[tiab] AND open access[filter]" .format(symbol)  # SFARI gene papers
    autism_papers = "{}[tiab] AND (Autism Spectrum Disorders OR ASD) AND open access[filter]".format(symbol) #Gene overlap with autism

    if querytype == "g":
        return gene_papers
    else:
        return autism_papers


def get_keywords(paper):
    keywords = []
    keyword_list = (paper['MedlineCitation']['KeywordList'])
    for obj in keyword_list:
        for keyword in obj:
            keywords.append(str(keyword))
    return keywords


def get_meshterms(paper):
    meshterms = []
    mesh_list = paper['MedlineCitation']['MeshHeadingList']
    for term in mesh_list:
        t = term.get('DescriptorName')
        meshterms.append(str(t))
    return meshterms


def full_xml(id_list):

    url_list = []
    for id in id_list:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={}&tool=my_tool&email={}".format(id, emailstring)
        url_list.append(url)

    return url_list


class Gene:

    def __init__(self, symbol, name, score, syndromic, gene_papers, autism_papers):
        self.symbol = symbol
        self.name = name
        self.score = score  # fix
        self.syndromic = syndromic
        self.gene_papers = gene_papers  # fix
        self.autism_papers = autism_papers


def get_geneinfo():

    genes = []

    for line in file:
        line = line.strip().split(',')
        genes.append(Gene(line[1], line[2], line[4], line[5], '', ''))

    return genes


def get_reports():

    genes = get_geneinfo()

    # saves gene details and a txt file of pmcids.

    with open("files/sfari_counts.csv", 'w', newline='') as f:

        writer = csv.writer(f)

        pmcid_list = []

        f2 = open("files/sfari_pmcids.txt", 'w')

        # writer.writerow(["Symbol", "Name", "Gene Score", "Syndromic", "#Papers", "#Autism Papers"])

        for g in genes[1:]:
            results_sfari = search_pmc(query_pubmed(g.symbol, g.name, 'g'))
            results_autism = search_pmc(query_pubmed(g.symbol, g.name, 'a_g'))
            g.sfari_papers = results_sfari['Count']
            g.autism_papers = results_autism['Count']
            pmcid = results_autism['IdList']

            details = [g.symbol, g.name, g.score, g.syndromic, g.sfari_papers, g.autism_papers]
            writer.writerow(details)

            pmcid_list.extend(pmcid)
            f2.write(', '.join(pmcid))
            f2.write(',\n')
            print(g.symbol)

    print('finished')


def write_urls():

    url_list = []

    f = open('files/sfari_pmcids.txt', 'r').read()
    f = f.replace('\n', '')
    f = f.replace(' ', '')
    id_list = list(filter(None, f.split(',')))

    f2 = open('files/url_list.txt', 'w')

    for id in id_list:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={}&tool=my_tool&email={}".format(id, emailstring)
        if url not in url_list:
            url_list.append(url)
            f2.write(url + "\n")
    f2.close()
    print(len(url_list))


if __name__=='__main__':
    write_urls()
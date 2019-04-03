from collections import defaultdict
from Bio import Entrez

emailstring = 'heather_logan@live.co.uk'


def search_pub(query):
    Entrez.email = emailstring

    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax='3000',
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)

    return results


def search_pmc(query):
    Entrez.email= emailstring
    handle = Entrez.esearch(db='pmc', term=query,  retmax='120000',)

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

    file = open("files/genes_etc/SFARI_file.csv", 'r').readlines()

    genes = []

    for line in file:
        line = line.strip().split(',')
        genes.append(Gene(line[1], line[2], line[4], line[5], '', ''))

    return genes


def write_urls():

    url_list = []

    f = open('files/sfari_pmcids.txt', 'r').read()
    f = f.replace('\n', '')
    f = f.replace(' ', '')
    id_list = list(filter(None, f.split(',')))

    for id in id_list:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={}&tool=my_tool&email={}".format(id, emailstring)
        if url not in url_list:
            url_list.append(url)
    return url_list

def sort_hgnc():

    # {Approved Symbol: [All synonyms]}
    hgnc_genes ={}

    file = open('files/genes_etc/hgnc_sorted.txt', 'r').readlines()

    # ignore pseudogenes(?)

    for line in file:
        if 'pseudogene' in line:
            pass
        else:
            key, vals = line.strip().split(": ")
            vals = vals.split(', ')
            hgnc_genes[key] = [key] + vals

    return hgnc_genes


def get_synonyms():
    sfari= open('files/genes_etc/SFARI_file.csv', 'r')
    hgnc = sort_hgnc()

    sfari_symbols = {}

    for line in sfari:
        line = line.split(',')
        sfari_symbols[line[1]] = line[2]

    all_synonyms = {}

    count = 0
    for symbol, name in sfari_symbols.items():
        if symbol in hgnc.keys():
            all_synonyms[symbol] = hgnc.get(symbol)
        else:
            all_synonyms[symbol] = [symbol, name]
        count += 1
    return all_synonyms


def stuff():
    writer = open("files/sfari_q_results.txt", 'w')
    writer.write("Gene, Gene + ASD, Gene Synonyms + ASD, Gene + ASD Majr, Gene Synonyms + ASD Majr")

    non_majr_results = open('files/autism_non_majr_papers1.txt', 'w')
    majr_results = open("files/autism_majr_papers1.txt", 'w')

    sfari_syns = get_synonyms()

    for gene in list(sfari_syns.keys())[291:]:

        syns = sfari_syns.get(gene)

        query1 = "{} AND (Autism Spectrum Disorder) AND open access[filter]".format(gene)
        syn_str = "{}".format(gene)
        for syn in syns[1:]:
            syn_str += " OR ({})".format(syn)
        query2 = syn_str + " AND Autism Spectrum Disorder AND open access[filter]"
        query3 = "{} AND (Autism Spectrum Disorder[MAJR]) AND open access[filter]".format(gene)
        query4 = syn_str + " AND (Autism Spectrum Disorder[MAJR]) AND open access[filter]"

        # q1_r = search_pmc(query1)['Count']
        q2_r = search_pmc(query2)
        # q3_r = search_pmc(query3)['Count']
        q4_r = search_pmc(query4)


        print(gene)
        # print("\t", query1, q1_r)
        print("\t", query2, q2_r['Count'])
        # print("\t", query3, q3_r)
        print("\t", query4, q4_r['Count'])

        writer.write("{},{},{},{},{}\n".format(gene, "", q2_r['Count'], "", q4_r['Count']))
        non_majr_results.write(gene + ":" + ','.join(q2_r['IdList']) + "\n")
        majr_results.write(gene + ":" + ','.join(q4_r['IdList']) + "\n")

    writer.close()
    non_majr_results.close()
    majr_results.close()


def get_PMC_from_pubmed(query):

    results = search_pub(query)
    pubmed_ids = []

    if results['IdList']:
        pmc_ids = results['IdList']
        r = fetch_details(pmc_ids)['PubmedArticle']

        for paper in r:
            p = paper['PubmedData']['ArticleIdList']
            for p2 in p:
                year = 0
                if p2.startswith("PMC"):
                    pubmed_ids.append(str(p2))
                    for date in paper['PubmedData']['History']:
                        if date.attributes['PubStatus'] == 'entrez':
                            year = date['Year']
                    print(str(p2), '\t', year)

    return pubmed_ids



def makeurls(ids):

    # ids = get_PMC_from_pubmed(query)
    urls = open('files/papers/asd_gene_urls_2.txt', 'w')

    for id in ids:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={}&tool=my_tool&email={}".format(id, emailstring)
        urls.write(url + "\n")
    urls.close()


def check_papers():
    genefile = open('files/gene_pmcids_2.txt', 'r')

    gene_papers = []

    for line in genefile:
        gene, papers = line.strip().split(':')
        papers = papers.split(', ')
        gene_papers.extend(papers)

    gene_papers = list(set(gene_papers))

    autismfile = open('files/autism_pmcids.txt', 'r')
    autism_papers = []

    for line in autismfile:
        papers = line.strip().split(', ')
        autism_papers.extend(papers)

    autism_papers =list(set(autism_papers))

    in_both = 0
    gene_only = 0
    autism_only = 0

    for paper in autism_papers:
        if paper in gene_papers:
            in_both += 1
        else:
            autism_only += 1

    gene_only = len(gene_papers) - in_both
    print(in_both, autism_only, gene_only)

    file = open('files/large_pmcids.txt', 'w')

    gene_papers.extend(autism_papers)
    all_papers = list(set(gene_papers))
    file.write(','.join(all_papers))


if __name__=="__main__":

    query = '"Autistic Disorder/genetics"[Mesh] AND "loattrfree full text"[sb]'
    query3 = '"autism spectrum disorder"[MeSH Terms] AND (social[text word] OR behaviour[text word] OR phenotype[text word]) AND "loattrfree full text"[sb]'
    query5 = '("autism spectrum disorder"[MeSH Terms] OR ("autism"[All Fields] AND "spectrum"[All Fields] AND "disorder"[All Fields]) OR "autism spectrum disorder"[All Fields]) AND "open access"[filter]'
    query6 = '"autism spectrum disorder"[MeSH Terms] AND (("genetics"[Subheading] OR "genetics"[All Fields] OR "genetics"[MeSH Terms]) OR ("genes"[MeSH Terms] OR "genes"[All Fields])) AND "open access"[filter]'



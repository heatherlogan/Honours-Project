from itertools import chain
from ontology_stuff import *
from collections import Counter

onto_objects = build_onto_objects()
leaf_nodes = get_leaf_nodes()

# search ontology node

# shows each child
# gets relevant paper ids.

# shows list of genes mentioned (sorted by family?) with count

# shows sfari genes mentioned, in order of confidence

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def load_relevant_papers():

    relevant_papers = {}

    file = open('files/relevant_papers.txt', 'r').readlines()

    for line in file:
        classnum, list = line.split(': ')
        papers = (list.strip()).split(',')
        relevant_papers[classnum] = papers

    return relevant_papers


def load_mentioned_genes():
    file = open('files/genes_per_paper.txt', 'r').readlines()

    genes_in_paper = {}

    for line in file:
        paper, list = line.split(":")
        if len(list) > 0:
            genes = (list.strip()).split(", ")
        else:
            genes = []
        genes_in_paper[paper]= genes

    return genes_in_paper


def load_gene_families():

    file = open('files/gene_families.txt', 'r').readlines()

    gene_families = {}
    for line in file:
        family, gene = line.split('\t')
        gene_families[gene.strip()] = family

    return gene_families


relevant_papers = load_relevant_papers()
genes_in_paper = load_mentioned_genes()
gene_families = load_gene_families()


def compare_genes_papers(list_of_papers):
    all_genes = []

    for paper in list_of_papers:
        genes = genes_in_paper.get(paper)
        if genes != None:
            all_genes.append(genes)

    genes = sorted(list(chain.from_iterable(all_genes)))
    return genes


def group_by_families(list_of_genes):

    gene_fams_found = []
    not_found = []

    for gene in list_of_genes:
        family = gene_families.get(gene)
        if family == None:
            not_found.append(gene)
        else:
            gene_fams_found.append(family)
    return gene_fams_found, not_found




def build_ancestry_main(major):

    print("\n", '\033[1m'+ (major.label).upper())

    def build_ancestry(node, count):

        def get_node(n):
            return next((x for x in onto_objects if x.classnum == n), None)

        def get_children(node):
            children = []

            for i in node.descendants():
                parent = ((re.sub('([^\s\w]|)+', '', str(i.is_a).replace('asdpto.', ''))))
                if parent == node.classnum:
                    children.append(i)
            return children

        children = get_children(node)

        if len(children) > 0:
            count += 1
            for child in children:
                string = '\t\t' * count
                child = get_node(re.sub('asdpto.', '', str(child)))

                print(string + color.BLUE + child.label.upper() + color.END)
                papers = relevant_papers.get(child.classnum)

                if papers != None:
                    all_genes = compare_genes_papers(papers)
                    print(string + "\t\tMost Relevant Papers: ", papers)
                    top_genes = Counter(all_genes).most_common(10)
                    print(string + "\t\tMost Mentioned Genes: ", [a for a,b in top_genes])
                    found_fams, not_found = group_by_families(all_genes)
                    top_families = Counter(found_fams).most_common(4)
                    print(string + "\t\tMost Mentioned Families:", [a for a,b in top_families])


                build_ancestry(child, count)

    count = 0
    build_ancestry(node, count)


if __name__=='__main__':

    name = "Motor Skills"
    node = next((x for x in onto_objects if x.label == name), None)

    if node == None:
        print('Invalid Node')
    else:
        build_ancestry_main(node)

from itertools import chain
from ontology_stuff import *
from article_mining import *

onto_objects = build_onto_objects()
leaf_nodes = get_leaf_nodes()
relevant_papers = load_relevant_papers()
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

                print(string + color.BOLD + color.BLUE + child.label.upper() + color.END)
                papers = relevant_papers.get(child.classnum)

                if papers != None:

                    print(string + "\t\tMost Relevant Papers: ", papers)

                    all_genes = get_getjoinedcounts(papers)
                    top_genes = all_genes.most_common(20)
                    found_fams = match_families(all_genes)
                    top_families = found_fams.most_common(10)

                    print(string + "\t\tMost Mentioned Genes: ", [a for a, b in top_genes])
                    print(string + "\t\tMost Mentioned Families:", [a for a, b in top_families])

                build_ancestry(child, count)

    count = 0
    build_ancestry(node, count)


if __name__=='__main__':

    name = "Motor Skills"
    node = next((x for x in onto_objects if x.label == name or x.classnum == name), None)

    if node == None:
        print('Invalid Node')
    else:
        build_ancestry_main(node)

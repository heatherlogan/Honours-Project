from ontology_stuff import *

onto_objects = build_onto_objects()
leaf_nodes = get_leaf_nodes()


# search ontology node

# shows each child

# gets relevant paper ids.

# shows list of genes mentioned (sorted by family?) with count

# shows sfari genes mentioned, in order of confidence

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
                string = '\t' * count
                child = get_node(re.sub('asdpto.', '', str(child)))
                print(string, '\033[1m * ' + child.label.upper())

                # get info

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
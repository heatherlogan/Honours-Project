

# reads gold standard file to tuples of ('phrase'; 'concept')


# reads NER output to same tuples

def load_output():
    file = open('files/output_NER.txt', 'r').readlines()

    output_NER = []
    doc = 0

    for line in file:
        if "*" in line:
            doc += 1;
        else:
            phrase, semtype = line.strip().split(':')
            output_NER.append((doc, phrase.strip(), semtype.strip()))

    return output_NER


# True positives; entity and correct classification


# False positives; entity and wrong classification


# True negatives;



if __name__=="__main__":

    output = load_output()



    for o in output:
        if o[0] == 1:
            print(o)


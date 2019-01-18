

# reads gold standard file to tuples of ('phrase'; 'concept')


# reads NER output to same tuples
import itertools
from difflib import SequenceMatcher


def load_gold():

    file = open("files/manually_annotated.txt", 'r').readlines()

    gold_annotations = []

    for line in file:
        if "***END" not in line:
            phrase, semtype = line.strip().split(':')
            gold_annotations.append((phrase.strip(), semtype.strip()))
        else:
            break

    return gold_annotations


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

#
#
# # Correct = correct string and correct label
# incorrect = similar/correct string and incorrect label
# partial = similar string and correct label
# missing = golden annotation is missed
# spirius = system returns annotation not in golden

# type = type matches the system tagged entity and golden annotation
# partial = partial boundary match regardless of type
# relaxed = exact string match regardless of type
# strict = exact string and exCT type


def is_similar(gold, system):

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    if similar(gold, system)>0.8:
        return True
    else:
        return False

def identify_matches(gold, system):
    correct = 0
    partial = 0
    incorrect = 0

    cor = []
    par = []
    incor = []



    for (gold_phrase, gold_type) in gold:
        for (system_phrase, system_type) in system:
            if gold_phrase == system_phrase:
                if gold_type == system_type:
                    correct += 1
                    cor.append(((gold_phrase, gold_type), (system_phrase, system_type)))
                else:
                    incorrect += 1
                    incor.append(((gold_phrase, gold_type), (system_phrase, system_type)))

            else:
                if is_similar(gold_phrase, system_phrase):
                    if gold_type == system_type:
                        par.append(((gold_phrase, gold_type), (system_phrase, system_type)))
                        partial += 1
                    else:
                        incor.append(((gold_phrase, gold_type), (system_phrase, system_type)))
                        incorrect += 1

    print(correct, partial, incorrect)
    #
    #
    # not_eval_gold = [x for x in gold if x not in evaluated]
    #
    # not_eval_system = [x for x in system if x not in evaluated]
    #
    # for n in not_eval_gold:
    #     print(n)
    # print('\n')
    #
    # for n in not_eval_system:
    #     print(n)

    for i in incor:
        print(i)

if __name__=="__main__":

    gold_annotations = load_gold()
    output = load_output()

    output.sort(key=lambda x: x[1])
    gold_annotations.sort()

    temp_output = [(p,t) for (i, p, t) in output if i==1]

    identify_matches(gold_annotations, temp_output)




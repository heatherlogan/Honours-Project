import itertools
from difflib import SequenceMatcher


def load_gold():

    file = open("files/manually_annotated.txt", 'r').readlines()

    gold_annotations = []

    for line in file:
        line = line.strip()
        if "***STOP" not in line:
            if "**END" not in line:
                if "*PMC" in line:
                    id = line.replace('*', '').strip()
                elif line != "":
                    phrase, semtype = line.split(':')
                    gold_annotations.append((id, phrase.strip(), semtype.strip()))
        else:
            break
    return gold_annotations


def load_output():


    file = open("files/output_latest2.txt", 'r').readlines()

    system_annotations = []

    for line in file:
        print(line)
        line = line.strip()

        if "***STOP" not in line:
            if "**END" not in line:
                if "*PMC" in line:
                    id = line.replace('*', '').strip()
                elif line != "":
                    phrase, semtype = line.split(':')
                    system_annotations.append((id, phrase.strip().lower(), semtype.strip()))
        else:
            break

    return system_annotations



# Correct = correct string and correct label
# Incorrect = similar/correct string and incorrect label
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

    if similar(gold, system) > 0.8: return True
    else:
        return False


def identify_matches(gold, system):

    correct = 0
    partial = 0
    incorrect = 0
    evaluated = []

    for (gold_phrase, gold_type) in gold:
        for (system_phrase, system_type) in system:
            if gold_phrase == system_phrase:
                if gold_type == system_type:
                    correct += 1
                    evaluated.append((gold_phrase, gold_type))
                else:
                    incorrect += 1
                    evaluated.append((gold_phrase, gold_type))
                    evaluated.append((system_phrase, system_type))
            else:
                if is_similar(gold_phrase, system_phrase):
                    if gold_type == system_type:
                        partial += 1
                        evaluated.append((gold_phrase, gold_type))
                        evaluated.append((system_phrase, system_type))
                    else:
                        incorrect += 1
                        evaluated.append((gold_phrase, gold_type))
                        evaluated.append((system_phrase, system_type))

    missing = len([x for x in gold if x not in sorted(list(set(evaluated)))])
    spirius = len([x for x in system if x not in sorted(list(set(evaluated)))])

    # print(correct, partial, incorrect, missing, spirius)

    return correct, partial, incorrect, missing, spirius


def calculate_metrics(correct, partial, incorrect, missing, spirius):

    TP = correct + incorrect
    FP = partial + spirius
    FN = partial + missing
    possible = TP + FN
    actual = TP + FP

    precision_exact = (correct/actual)
    recall_exact = (correct/possible)

    precision_partial = (correct + (0.5 * partial))/actual
    recall_partial = (correct + (0.5 * partial))/possible

    return precision_exact, recall_exact, precision_partial, recall_partial



if __name__=="__main__":

    gold_annotations = load_gold()

    system_out = load_output()

    system_out.sort(key=lambda x: x[1])
    gold_annotations.sort()

    pmcds = list(set([x for x, y, z in (gold_annotations)]))

    string_list = []
    strn = "Paper ID\tExact Precision\tExact Recall\tExact F1\tPartial Precision\tPartial Recall\tPatrial F1"
    print(strn)

    avg_ex_p = 0
    avg_ex_r = 0
    avg_ex_f1 = 0
    avg_par_p = 0
    avg_par_r = 0
    avg_par_f1 = 0

    for i, p in enumerate(pmcds):

        golds = [(g[1], g[2]) for g in gold_annotations if g[0] == p]
        output = [(o[1], o[2]) for o in system_out if o[0] == p]

        cor, par, incor, mis, spir = identify_matches(golds, output)
        pre_ex, rec_ex, pre_par, rec_par = calculate_metrics(cor, par, incor, mis, spir)
        f1_ex = 2 * ((pre_ex * rec_ex)/(pre_ex + rec_ex))
        f1_par =2 * ((pre_par * rec_par)/(pre_par + rec_par))
        print("{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t".format(p, pre_ex, rec_ex, pre_par, f1_ex, rec_par, f1_par))

        avg_ex_p += pre_ex
        avg_ex_r += pre_ex
        avg_ex_f1 += f1_ex
        avg_par_p += pre_par
        avg_par_r += rec_par
        avg_par_f1 += f1_par

    i = len(pmcds)

    print("Average:\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t"
          .format(avg_ex_p/i, avg_ex_r/i, avg_ex_f1/i,
                  avg_par_p/i, avg_par_r/i, avg_par_f1/i))

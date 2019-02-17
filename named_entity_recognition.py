import itertools
import re
from difflib import SequenceMatcher
import nltk
from pymetamap import MetaMap
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from indexer import reload_corpus

mm = MetaMap.get_instance('/Users/heatherlogan/Desktop/public_mm/bin/metamap16')
stopwords = list(set(stopwords.words('english')))
lem = WordNetLemmatizer()


def acronym_search(text):

    # returns an acronym : term dictionary detected in text assuming acronyms are stated as Full Word (acronym)
    # looks at first letter of every word in preceeding areas or if a word begins with a portion of the acronym

    acronyms = {}

    lst = re.findall('\(.*?\)', text)
    text = re.sub('[.,?!]','',text)
    text = text.split()
    for ac in lst:
        try:
            i = text.index(ac)
            chars = [a.lower() for a in list(ac) if a.isalpha()]
            start = i+2 - len(ac)
            j = [start if start >= 0 else 0][0]
            preceeding_words = text[j:i]
            ac = re.sub('[]()[]', '', ac)
            for word in preceeding_words:
                if word.lower().startswith(ac.lower()):
                    acronyms[ac] = " ".join(preceeding_words[preceeding_words.index(word):])
            output = []
            for i in preceeding_words:
                output.append(i[0].lower())
            intersection = ([value for value in chars if value in output])
            if len(intersection) >= len(chars)/2:
                try:
                    first = [preceeding_words.index(i) for i in preceeding_words if i.lower().startswith(intersection[0])][0]
                    ac = re.sub('[]()[]', '', ac)
                    acronyms[ac] = " ".join(preceeding_words[first:])
                except IndexError:
                    pass
        except ValueError:
            pass

    acronyms['ASD'] = 'Autism Spectrum Disorder'

    return acronyms


def load_hgnc():

    file = open('files/genes_etc/hgnc_sorted.txt', 'r').readlines()
    genes = {}

    for line in file:
        approved, alises = line.strip().split(': ')
        alises = alises.split(', ')
        genes[approved] = alises

    return genes


def load_amino_acids():

    file = open('files/genes_etc/amino_acids.csv', 'r').readlines()
    amino_acids = []

    for line in file[1:]:
        name, abbrev, sym = line.strip().split(',')
        amino_acids.append((name, abbrev, sym))

    return amino_acids


def entity_extract(text, pattern):

    if pattern=='default':
        pattern = r""" Ents: {[0-9]*<JJ|VBN>*(<NN>|<NNS>|<NNP>)+}"""

    named_ents = {}

    for sentence in nltk.sent_tokenize(text):
        # r = re.split('; |\. |\.\s|\s|\n', sentence)

        pos_s = nltk.pos_tag(sentence.split())
        chunkParser = nltk.RegexpParser(pattern)
        chunked = chunkParser.parse(pos_s)

        for chunk in chunked:
            string = []
            if type(chunk) != tuple:
                [string.append(term.lower()) for term, tag in chunk]
            if string:
                if string[-1].endswith(",") or string[-1].endswith("."):
                    string[-1] = string[-1][:-1]

                ascii_string = []
                for term in string:
                    term = "".join([t for t in term if ord(t) < 128])

                    ascii_string.append(term)

                string = " ".join(ascii_string)
                named_ents[string.strip()] = []

    named_ents = {k: v for k, v in named_ents.items() if k is not ''}

    # splitting on comma, refactor later

    fixed_named_ents = {}

    for k, v in named_ents.items():
        if ',' in k:
            new_k = k.split(',')
            for k2 in new_k:
                fixed_named_ents[k2] = []
        else:
            fixed_named_ents[k] = v

    return fixed_named_ents


def meta_map_chunked(entities):
    concepts, error = mm.extract_concepts(entities, [1])
    return concepts


# returns possible semantic types for an entity
def meta_ner(entity):

    cs, error = mm.extract_concepts([entity],[1])
    semtypes_lst = []
    for c in cs:
        semtypes_lst.append(c.semtypes)
    return semtypes_lst


def is_gene(term):
    # used for unidentified terms that could be misspelled genes

    flat_vals = list(itertools.chain.from_iterable(hgnc.values()))
    is_similar = False

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    for hg in flat_vals:
        hg = hg.upper()
        term = term.upper()
        if similar(hg, term) > 0.85:
            is_similar = True
            break

    return is_similar

def get_genes(text):

    text = nltk.word_tokenize(text)

    detected_genes = {}

    for t in text:
        if t.upper() in [x.upper() for x in itertools.chain.from_iterable(hgnc.values())] and t not in stopwords:
            detected_genes[t] = ['[gngm]']

    return detected_genes


def mutation_search(text):

    # split on whitespaces then sentence level
    mutations = {}
    amino_acids = list(sum(load_amino_acids(), ()))
    variant_types = ['c', 'g', 'm', 'n', 'r', 'p']
    string_ors = ""
    for acid in amino_acids[:len(amino_acids)-2]:
        string_ors += ("{}|".format(acid))
    string_ors += "{}".format((amino_acids[len(amino_acids)-1]))

    patterns = ["(\s)({})[0-9]+({})".format(string_ors, string_ors), # E45V
                "({})\.[0-9]+(\s)*({})(\s)*>(\s)*({})".format(variant_types, string_ors, string_ors), #c.65A>V
                "({})\.({})(\s)*[0-9]+(\s)*>(\s)*({})".format(variant_types, string_ors, string_ors), #c.A65>V
                "({})\.({})[0-9]+({})".format(variant_types, string_ors, string_ors), #c.A43V
                "({})\.[0-9]+_[0-9]+(\s)*ins(\s)*({})".format(variant_types, string_ors), # c.75_77insG insertion
                "({})\.[0-9]+(\s)*del(\s)*({})".format(variant_types, string_ors), # c.75delA deletion
                "({})\.({})(\s)*[0-9]+(\s)fs".format(variant_types, string_ors), # frameshift
                "({})\.[0-9]+(\s)*dup(\s)*({})".format(variant_types, string_ors) ] # duplication

    for pattern in patterns:
        f = re.finditer(pattern, text)

        for match in f:
            mut = match.group()
            mut = mut.encode('ascii', 'ignore').decode('ascii')
            mutations[mut] = ['[comd]']

    return mutations


def process_text(text):
    # search and replace acronyms, remove remaining bracket items

    acs = acronym_search(text)
    muts = mutation_search(text)
    print(acs)

    for acronym, fullword in acs.items():
        text = re.sub(acronym, fullword, text)

    brackets = re.findall('\[.*?\]', text) + re.findall('\(.*?\)', text)

    for b in brackets:
        term = re.sub('[\[\]\(\)]', '', b)
        if term in acs.values():
            text = text.replace(b, '')
        else:
            terms = term.split()
            for t in terms:
                t = t.strip()
                if t not in muts:
                    text = text.replace(t, '')

    text = text.replace('  ', ' ').replace(" ( )", '')
    print(text)
    return text


def load_gold_annotations():

    file=open('files/gold_most_common_entities.txt', 'r').readlines()
    gold_annotations = {}

    for line in file:
        term, label = line.split(': ')
        gold_annotations[term.strip()] = label.strip()

    return gold_annotations


def similar_gold(term):

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    label = ""
    max = 0

    # checks if a  gold annotations for
    for k, v in gold_annotations.items():
        sim = similar(term, k)
        if sim > 0.85 and sim > max:
            max = sim
            label = v

    if label:
        return label
    else:
        return ""

def annotate(text):

    found_genes = [g.lower() for g in get_genes(text)]
    mutations = mutation_search(text)
    entities = entity_extract(process_text(text), 'default')
    entities = {**entities, **mutations}
    id_entity = {}

    for k, v in entities.items():
        if k not in stopwords:
            if k in mutations.keys():
                id_entity[k] = '[comd]'
            elif k in gold_annotations.keys():
                print(k, "in golden")
                id_entity[k] = gold_annotations.get(k)
            elif lem.lemmatize(k) in gold_annotations.keys():
                print(k, "in golder")
                id_entity[k] = gold_annotations.get(lem.lemmatize(k))
            elif k in found_genes:
                id_entity[k] = '[gngm]'
            else:
                semtypes = meta_ner(k)
                if len(semtypes) > 0:
                    id_entity[k] = semtypes[0]
                elif is_gene(k):
                    id_entity[k] = '[gngm]'
                elif similar_gold(k) != "":
                    id_entity[k] = similar_gold(k)

    for k, v in id_entity.items():
        print("{}: {}".format(k.strip(), v))
    return id_entity

def annotate_abstracts(filename):

    abstract_file = open('files/papers/{}'.format(filename), 'r').readlines()
    abstracts = reload_corpus(abstract_file)

    for i, ab in enumerate(abstracts):
        print("*PMC{}*".format(ab.id))
        text = ab.abstract
        annotate(text)


if __name__=="__main__":

    hgnc = load_hgnc()
    gold_annotations = load_gold_annotations()

    text = "Individuals with ASD showed reduced interpersonal interactions."

    text10=" Chromatin immunoprecipitation assay using Retinoid Acid Receptor B as the " \
           "immunoprecipitation target suggests RA regulation of Aldh1a3 and Foxn1 in mice."

    annotate(text10)
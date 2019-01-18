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

    return acronyms


def load_hgnc():

    file = open('files/hgnc_sorted.txt', 'r').readlines()
    genes = {}

    for line in file:
        approved, alises = line.strip().split(': ')
        alises = alises.split(', ')
        genes[approved] = alises

    return genes


def load_amino_acids():

    file = open('files/amino_acids.csv', 'r').readlines()
    amino_acids = []

    for line in file[1:]:
        name, abbrev, sym = line.strip().split(',')
        amino_acids.append((name, abbrev, sym))

    return amino_acids


def entity_extract(text, pattern):

    if pattern=='default':
        pattern = r""" Ents: {[0-9]*<JJ>*(<NN>|<NNS>|<NNP>)+}"""

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
                ascii_string = []
                for term in string:
                    term = "".join([t for t in term if ord(t)<128])
                    ascii_string.append(term)
                string = " ".join(ascii_string)

                if string.endswith(".") or string.endswith(','):
                    string = string[:-1]

                if string.lower() not in stopwords:
                    for x in [';', ',', ':', ]:
                        if x in string:
                            strs = string.split(x)
                            for s in strs:
                                s = re.sub('[,.;:]', '', s)
                                named_ents[s.strip()] = []
                            break
                        else:
                            string = re.sub('[,.;:]', '', string)
                            named_ents[string.strip()] = []

    return named_ents


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
    remove = []
    keep = []

    brackets = re.findall('\[.*?\]', text) + re.findall('\(.*?\)', text)

    for b in brackets:
        term = re.sub('[\[\]\(\)]', '', b)

        if term in acs.keys():
            keep.append(term)

        # if only number then remove
        elif all(x.isdigit() for x in term):
            remove.append(b)
        else:
            remove.append(b)


    for k in keep:
        text = re.sub(k, acs.get(k), text)

    for r in remove:
        text = text.replace(r, '')

    text = text.replace('(', ', ').replace(')', ',')

    return text

if __name__=="__main__":


    test_sentences = "Very recently, homozygous variations within ALDH1A3 have been associated with autosomal recessive microphthalmia with or without cysts or coloboma." \
                     "Two missense novel SNVs were found in the same child: ALDH1A3 (RefSeq NM_000693: c.1514T>C (p.I505T)) and FOXN1 (RefSeq NM_003593: c.146C>T (p.S49L)). " \
                     "A bimodal age of onset was established and the best-fitting cut-off score between early and late age of onset was 20 years (early age of onset ≤19 years)." \
                     "Participants with AS showed difficulties in identifying the awkward elements of everyday social scenarios, and they were also impaired in generating problem solutions but not in judging alternative solutions on the social problem fluency and resolution tasks." \
                     "The present study examined whether adults with high functioning autism (HFA) showed greater difficulties in (1) their self-reported ability to empathise with others and/or (2) their ability to read mental states in others’ eyes than adults with Asperger syndrome (AS)."



    hgnc = load_hgnc()


    abstract_file = open('files/abstracts.txt', 'r').readlines()
    writefile = open('files/output_NER.txt', 'w')

    abstracts = reload_corpus(abstract_file)

    for ab in abstracts:

        text = ab.abstract

        found_genes = get_genes(text)
        mutations = mutation_search(text)
        entities = entity_extract(process_text(text), 'default')
        new = {**entities, **found_genes, **mutations}
        #
        id_entity = {}

        unknown = []

        for k, v in new.items():
            if k not in stopwords:
                if k not in mutations.keys():
                    lst = meta_ner(k)
                else:
                    lst = ['[comd]']
                id_entity[k] = lst

        for k2, v2 in id_entity.items():
            if len(v2)>0:
                txt = "{}: {}\n".format(k2, v2[0])
                print(k2, v2[0])
                writefile.write(txt)
            else:
                if k2 in mutations.keys():
                    txt = "{}: [comd]\n".format(k2)
                    writefile.write(txt)
                    print(k2, '[comd]')
                elif is_gene(k2):
                    txt = "{}: [gngm]\n".format(k2)
                    writefile.write(txt)
                    print(k2, '[gngm]')
                else:
                    # search more dictionaries
                    unknown.append(k2)
        writefile.write("\n")
        print(unknown)
    writefile.close()




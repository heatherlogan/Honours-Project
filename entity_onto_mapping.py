from ontology_stuff import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
import spacy
import numpy as np

stemmer = PorterStemmer()
nlp = spacy.load('en')

def load_asd_terms (file):

    terms = defaultdict(list)

    for line in file:
        if line.startswith("Class_"):
            classno = line.strip()
        elif not line == "\n":
            terms[classno].append(stemmer.stem(line.strip()))
    return terms


def load_entities(filename):

    file = open('files/NER_outputs/{}'.format(filename), 'r').readlines()

    ents = defaultdict(list)

    for line in file:
        if line.startswith("*PMC"):
            pmcid = line.strip().replace("*", "*")
        elif ("**") not in line and line != "\n":
            ents[pmcid].append(line.strip())
    return ents

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()



def get_semtype_groups():

    semtype_file = open('files/semantics/semantic_types.txt', 'r').readlines()
    semgroup_file = open('files/semantics/semantic_groups.txt', 'r').readlines()

    semgroup = defaultdict(list)

    for line in semgroup_file:
        acronym, group, id, type = line.strip().split("|")
        semgroup[acronym].append(type)

    semtypes = {}

    for line in semtype_file:
        abbrev, id, name = line.strip().split('|')
        semtypes[name] = abbrev

    semgroup_acronyms = defaultdict(list)

    for group, types in semgroup.items():
        for type in types:
            abbrev_type = semtypes.get(type)
            semgroup_acronyms[group].append(abbrev_type)

    return semgroup_acronyms




# change to general terms

def map_asd_onto(entities):

    file_string = "files/autism_terms/medical_phrases.txt"
    file = open(file_string, 'r').readlines()

    terms = defaultdict(list)

    for line in file:
        if line.startswith("Class_"):
            classno = line.strip()
        elif not line == "\n":
            terms[classno].append(line.strip())



    ent_keys = list(entities.keys())
    all_terms = ent_keys

    mappings = {}

    for entity in ent_keys:
        max_ent = 0
        for node, term_list in terms.items():
            for term in term_list:
                sim = similar(entity, term)
                if sim > max_ent and sim >0.5:
                    max_ent = sim
                    mappings[entity] = node


    class_terms = defaultdict(list)

    for e, v in mappings.items():
        class_terms[v].append(e)

    for c, t in class_terms.items():
        print(c)
        print(t)






def sort_asd_terms(ents):

    medfile = open('files/autism_terms/medical_keywords.txt', 'r').readlines()
    personalfile = open('files/autism_terms/personal_keywords.txt', 'r').readlines()
    socialfile = open('files/autism_terms/social_keywords.txt', 'r').readlines()
    med_terms = load_asd_terms(medfile)
    personal_terms = load_asd_terms(personalfile)
    social_terms = load_asd_terms(socialfile)

    semgroups = get_semtype_groups()

    chem_semtypes = ['antb','orch','phsu','hops','vita', 'clnd', 'horm']
    personal_semtypes = ['orga', 'inbe', 'socb', 'patf', 'bhvr']
    medical_semtypes = (semgroups.get('ANAT') + semgroups.get('DISO') + chem_semtypes)
    medical_semtypes.remove('cell')
    medical_semtypes.remove('fndg')
    social_semtypes = semgroups.get('ACTI')

    medical_ents = {}
    personal_ents = {}
    social_ents = {}

    med_terms = sorted(list(itertools.chain.from_iterable([v for k, v in med_terms.items()])))
    personal_terms = sorted(list(itertools.chain.from_iterable([v for k, v in personal_terms.items()])))
    social_terms = sorted(list(itertools.chain.from_iterable([v for k, v in social_terms.items()])))

    generic_terms = ["autism", 'autism spectrum disorder', 'asd', 'autism disorder', ] # remove?

    for ent, v in ents.items():
        for v2 in v:
            term, label = v2.split(':')
            stemmed = [stemmer.stem(e) for e in term.split()]
            label = (label.replace('[', '').replace(']', ''))
            label = label.split(', ')
            for word in stemmed:
                if word in med_terms:
                    medical_ents[term] = label[0].strip()
                if word in personal_terms:
                    personal_ents[term] = label[0].strip()
                if word in social_terms:
                    social_ents[term] = label[0].strip()

            for l in label:
                l = l.strip()
                if l in medical_semtypes:
                    medical_ents[term] = label[0].strip()
                if l in personal_semtypes:
                    personal_ents[term] = label[0].strip()
                if l in social_semtypes:
                    social_ents[term] = label[0].strip()


    medical_ents = OrderedDict(sorted(medical_ents.items(), key=lambda t: t[0]))
    personal_ents = OrderedDict(sorted(personal_ents.items(), key=lambda t: t[0]))
    social_ents = OrderedDict(sorted(social_ents.items(), key=lambda t: t[0]))


    return medical_ents, personal_ents, social_ents

if __name__=="__main__":

    # change to some paper

    file = "ner_include_list.txt"

    ents = load_entities(file)

    medical_ents, personal_ents, social_ents = sort_asd_terms(ents)

    for k, v in medical_ents.items():
        print(k, v)

    print('\n\n')
    for k, v in personal_ents.items():
        print(k, v)
    print('\n\n')
    for k, v in social_ents.items():
        print(k, v)
    print('\n\n')




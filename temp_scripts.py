# from collections import defaultdict, Counter
# from NER import *
# from nltk.stem.porter import PorterStemmer
# from nltk.stem import WordNetLemmatizer
# from nltk import bigrams, ngrams
# from ontology_stuff import extract_autism_entities
from pubmed_parse import *
import nltk

def sort_gene_families():

    file = open('files/gene_families.txt', 'r').readlines()

    gene_families = {}

    for line in file:
        line = line.split('\t')
        family, gene = line[0], line[1]
        gene_families[family] = gene

    return gene_families


def sort_hgnc():

    file = open('files/hgnc.txt', 'r')
    w_file = open('files/hgnc_sorted.txt', 'w')

    sorted = defaultdict(list)

    for line in file:
        line = line.strip().split('\t')
        line = list(filter(None, line))
        sorted[line[0]].extend(line)

    for k, v in sorted.items():
        print(k, list(set(v)))
        w_file.write("{}: {}\n".format(k, ', '.join(list(set(v)))))
    w_file.close()


def sort_diseases():

    file = open('files/disease_db.txt', 'r')

    r_file = open('files/diseases.txt', 'w')

    diseases = []
    for line in file:
        line = line.strip().split('\t')
        line = list(filter(None, line))
        diseases.append(line[3])

    diseases = sorted(list(set(diseases)))
    for disease in diseases:
        r_file.write(disease + "\n")


def write_entities():

    file = open('files/corpus_cleaned.txt', 'r').readlines()

    write_file = open('files/abstract_common_entities.txt', 'w')

    articles = reload_corpus(file)

    abstracts = [a.abstract for a in articles if a.abstract]

    all_entites = []

    for i, abs in enumerate(abstracts):

        print(i)
        all_entites.append([k.lower() for k, v in entity_extract(abs, 'default').items()])

    counter = Counter()
    all_entites = list(itertools.chain.from_iterable(all_entites))

    for ent in all_entites:
        counter[ent] += 1

    lst = [c[0] for c in counter.most_common(500)]

    print(sorted(lst))

    for l in sorted(lst):
        write_file.write("{}\n".format(l))

    # 60675 all entities
    # 32187 corpus entities

    write_file.close()


def condense_entities():

    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    entities = []
    stemmed = []
    lemmatized = []

    file = open('files/abstract_common_entities.txt', 'r')

    for line in file:
        ent = line.strip()
        entities.append(ent)
        stemmed.append(stemmer.stem(ent))
        lemmatized.append(lemmatizer.lemmatize(ent))

    stemmed_file = open('files/entities_stemmed.txt', 'w')
    lemmatized_file = open('files/entities_lemmatized.txt', 'w' )

    for ent in sorted(list(set(stemmed))):
        print(ent)
        stemmed_file.write("{}\n".format(ent))

    print(" ")

    for ent in sorted(list(set(lemmatized))):
        print(ent)
        lemmatized_file.write("{}\n".format(ent))


    stemmed_file.close()
    lemmatized_file.close()


def autism_terms():

    onto_labels = extract_autism_entities()
    terms = []

    for o in onto_labels:
        o = o.lower()
        fltr = [word for word in o.split() if word not in stopwords]
        bi = list(bigrams(fltr))
        terms.append(o)
        for o1 in fltr:
            terms.append(o1)
        for b in bi:
            terms.append(' '.join(b))

    return sorted(list(set(terms)))


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def is_anaphor():

    examples = ["this", "that", "he", 'she', "they",
                "Children with autism may have difficulties with visual disengagement that is, inhibiting current fixations and orienting to new stimuli in the periphery."]

    for example in examples:
        postag = nltk.pos_tag(example.split())
        print(postag)


def get_pubmmeds():

    pmcids = ['5321753', '5389513', '1382247', '5660893', '4635597', '3730181', '5442155', '4427554', '5508252', '3884762', '5351180', '4642926', '3988108', '5324567', '3745408', '5915454', '3295800', '6110470', '3310790', '5351204', '4647182', '4870371', '3325173', '59656', '3494744', '4411356', '6169859', '3399634', '4859958', '5416665', '4861960', '5067329', '5070061', '1513515', '6092396', '4413835', '3767287', '5974415', '6051604', '6258166', '5472790', '4693501', '4644211', '5881179', '3245106', '4011843', '3776732', '4926390', '3784762', '6299922', '6004695', '4747159', '2805335', '5451068', '4047885', '3996537', '5822461', '3041792', '3961203', '2848579', '4031262', '4059929', '4312830', '3179967', '2815936', '2645381', '4396692', '3043074', '3225379', '4320286', '2838793', '5790834', '2866544', '2847695', '5907836', '3490915', '5537637', '3040743', '4423768', '5474730', '3001695', '4323380', '4091790', '3006638', '3006426', '4445743', '5482876', '5833085', '3090611', '3235126', '2839489', '3474800', '3309488', '3524021', '2643049', '4372342', '3738022', '4824422', '1851007', '3720840', '3798378', '4433014', '1865561', '5886277', '2869041', '4424375', '3001124', '2248565', '4846490', '1525191', '2932694', '3723491', '2934739', '1888683', '3581547', '2265260', '3547942', '2222245', '4056431', '3815575', '3590998', '2373955', '1513329', '2935882', '4690969', '3350576', '4573762', '4707541', '3619456', '5068589', '4712554', '4701386', '5518181', '5541734', '3613847', '3338262', '3371866', '3811986', '3386011', '5539915', '2730532', '4739328', '2731203', '5472997', '3566384', '64493', '4903018', '194752', '3844687', '3170664', '3818007', '4740767', '4723262', '2752466', '4731780', '3819162', '3610904', '3637561', '3827143', '3874034', '4740114', '3840590', '3506511', '3548427', '4909589', '5879542', '5638204', '4820035', '5621737', '5374041', '5360848', '4449286', '3428055', '4631108', '4929695', '4556482', '5675000', '3042898', '3941568', '4568303', '3006666', '3965395', '4801420', '4793536', '4458007', '4926223', '4307305', '4263785', '4943479', '4574168', '4306541', '4849199', '5805137', '5382808', '4833406', '4468215', '4471293', '4315323', '4914424', '4504226', '3003876', '4821887', '3083416', '5684358', '3130692', '3368908', '3338748', '4341013', '3513680', '3094531', '6019410', '3885205', '3113723', '6026208', '2492880', '3533944', '3513683', '3383751', '3150391', '3907307', '3427326', '2772655', '2603481', '3899449', '2774338', '3965040', '2946294', '2892398', '5352796', '2670970', '3213131', '411038', '5389537', '4023913', '3400671', '3197027', '2705502', '3228874', '3130139', '329128', '5364052', '4316932', '3607626', '4530629', '3440365', '3915307', '3626795', '3162001', '3517299', '4383723', '3159129', '2797846', '3116738', '420465', '5701309', '3111012', '3636468', '3501969', '3919719', '3198479', '2921070', '2761880', '3961190', '2644762', '5789211', '2889141', '5842695', '3215885', '2921284', '546213', '509312', '3309504', '4319152', '5899373', '3513682', '3040206', '2947401', '3823459', '4119222', '4485698', '548305', '4198124', '5045145', '4140467', '1084355', '5022064', '4067505', '5578492', '4233346', '3681934', '5575292', '4134484', '5607556', '5431663', '5862414', '3688962', '4614053', '3694043', '4811712', '3631200', '5085743', '3628102', '4237351', '5360850', '1310613', '5543534', '3690969', '4419151', '4137411', '5454981', '4554745', '5454987', '3690523', '4249945', '4607423', '5622473', '4878876', '5075143', '4244134', '4259993', '6345368', '2683930', '5418740', '2685981', '6047246', '5354807', '4099083', '5794881', '6197704', '3252613', '5025785', '3057962', '3448848', '2965350', '5545734', '3464360', '5468514', '4949425', '4175587', '5667738', '3270696', '5167061', '4350522', '4177294', '5545711', '3181906', '5409128', '2671988', '2678711', '3565204', '4153713', '3544904', '5822466', '2721832', '5181638', '5299396', '4988886', '4350523', '3513679', '5339506', '4774994', '2638799', '4977510', '4990618', '3577685', '2680219', '4977499', '3269681', '5098909', '2695001', '3652084', '3710970', '2686502', '3309518', '5192959', '3547868']
    new_ids = []

    r = fetch_details(pmcids)['PubmedArticle']

    for paper in r:
        p = paper['PubmedData']['ArticleIdList']
        for p2 in p:
            if p2.startswith("PMC"):
                new_ids.append(str(p2).replace('PMC', ''))


    print(new_ids)
    print(len(pmcids), len(new_ids))

if __name__=="__main__":

    get_pubmmeds()
from collections import defaultdict, Counter
from NER import *
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import bigrams, ngrams
from ontology_stuff import extract_autism_entities
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


def filter_relations(relations):

    relations_copy = relations.copy()

    for e1, r, e2 in relations_copy:

        e1_pos_tag = nltk.pos_tag(e1.split())
        e2_pos_tag = nltk.pos_tag(e2.split())









    return relations_copy








if __name__=="__main__":

    s = "Recent evidences suggested that SNAP-25 is involved in different neuropsychiatric and neurological disorders.1 SNAP-25 participates in the regulation of synaptic vesicle exocytosis through the formation of a soluble N-ethylmaleimide-sensitive fusion protein-attachment protein receptor complex2 and interacts with different types of voltage-gated calcium channels,3 inhibiting their function and thus reducing neuronal calcium responsiveness to depolarization.4, 5, 6 Interestingly, polymorphisms in the SNAP-25 gene as well as altered expression of the protein have been associated with abnormal behavioural phenotype in both animal models7, 8, 9 and humans. Polymorphisms in the SNAP-25 gene have been found in patients affected by attention-deficit/hyperactivity disorder ,10, 11, 12, 13 schizophrenia14, 15, 16 and autism spectrum disorders .17 In a group of Sardinian children who developed primary Autism Spectrum Disorder, SNAP-25 polymorphisms were associated with a more compromised clinical outcome,17 and a significant correlation was observed between SNAP-25 single-nucleotide polymorphisms rs363043 and the Childhood Autism Rating Scale . Notably, these correlations were predominantly with hyperactivity and one or more aspects of the executive functions. SNAP-25 was also shown to be involved in the differential cognitive ability of healthy subjects. In particular, four SNAP-25 SNAP-25 single-nucleotide polymorphisms were associated with an increment of performance, but not of verbal intelligence quotient.18 Reduction of SNAP-25 expression has been described in brains of patients affected by either schizophrenia14 or ADHD.19 Reduction of protein expression was associated with the occurrence of frequent electroencephalographic spikes, suggesting a diffuse network hyperexcitability as shown in coloboma mouse20 and SNAP-25 heterozygous mice.21 Interestingly, epilepsy is associated with several neurodevelopmental disorders including ADHD, Autism Spectrum Disorder and intellectual disability.22 Such co-occurrence may share a genetic basis.23 Children and adolescents with epilepsy, in particular, tend to show an increased risk of ADHD,24, 25 suggesting a strong interrelationship between the Autism Spectrum Disorder and ADHD phenotype and childhood epilepsy. Notably, the epileptiform activity, characterized by the occurrence of frequent electroencephalogram spikes in 3-month-old SNAP-25+/− mice, was accompanied by cognitive deficits that were reverted by antiepileptic drugs.21 In an attempt to understand more in depth the role of SNAP-25 in human diseases characterized by an abnormal cognitive profile, we first analysed five SNAP-25 gene polymorphisms in a clinically characterized cohort of children affected by Autism Spectrum Disorder; in particular, we evaluated possible associations between such SNAP-25 single-nucleotide polymorphisms and the clinical outcome of Autism Spectrum Disorder. As we found a correlation between rs363050 SNP and cognitive deficits, the functional effects of this polymorphism on the gene expression was evaluated by means of the luciferaseiferase reporter gene confirming its involvement in gene transcriptional modulation. Moreover, given that SNAP-25 expression can be altered in childhood neuropsychiatric diseases and our previous work demonstrated behavioural and electroencephalogram deficits in adult SNAP-25+/− mice, we decided to verify whether similar deficits were present also during adolescence , in order to highlight possible autistic or ADHD symptoms. Finally, to verify a possible therapeutic application of valproate , which was previously shown to rescue some behavioural and electroencephalogram deficits when acutely administered, we evaluated the effect of this antiepileptic drug after chronic exposure. Forty-four Italian Autism Spectrum Disorder patients were enroled in the study. All subjects were born in peninsular Italy from families without Sardinian ancestry and were of Italian descent. All children underwent an in-depth examination that included clinical and neurological evaluations, mental status examination , neuropsychological evaluation and other diagnostic tools, such as the Modified Checklist for Autism in Toddlers, Childhood Autism Rating Scale, the Australian Scale for Asperger's syndrome, karyotype and DNA analysis for fragile X and MeC-P2, screens for inborn errors of metabolism , amino and organic acidopathies, electroencephalogram, brain-stem acoustic evoked potentials, visual evoked responses and computerized tomography or magnetic resonance imaging; some parents gave their consent only for computerized tomography rather than for magnetic resonance imaging. In-depth genetic analyses were performed as well in these children. The rs363050 gene polymorphism correlates with decreasing cognitive scores in autistic children. The rs363050 gene polymorphism correlates with decreasing cognitive scores in autistic children. The genotype distribution of the five analysed SNAP-25 SNAP-25 single-nucleotide polymorphisms , rs363039 rs363043, rs3746544 and rs1051312) was in the Hardy–Weinberg equilibrium. SNAP-25 genotypes were then examined in relationship with the Childhood Autism Rating Scale score34 in toto , as well as in relationship with the specific scores assigned to hyperactivity and autistic core-behaviour . The latter are specific items of the Childhood Autism Rating Scale, meant to separately define hyperactivity level and autistic core-behaviour on a seven-step scale . Moreover, based on the hypothesis that brain dysfunctions could be inferred from a lower cognitive functioning and/or from cortical electrical abnormalities, patients were subsequently classified according to their cognitive levels using the DSM IV-TR criteria.28 Categorical variables were evaluated by contingency table and χ2-evaluation. Significant associations of the rs363050 polymorphism with altered cognitive scores was observed by the comparison of categorical cognitive score variables ) : in particular, rs363050 genotype was more frequently observed in subjects with lower cognitive scores than in subjects with higher cognitive scores . Cognitive score association with SNAP-25 polymorphism was further analysed by numerical degrees scores association with SNAP-25 single-nucleotide polymorphisms by analysis of variance. Also, in this case results showed a statistical association between rs363050 polymorphism distribution and cognitive scores, index of mental retardation, whereas no associations were observed between these SNAP-25 single-nucleotide polymorphisms and any of the other neuropsychiatric parameters analysed. Finally, the analysis of possible correlations between cortical electrical dysfunction and presence of seizures and SNAP-25 SNAP-25 single-nucleotide polymorphisms as categorical variables, by contingency table and χ2-evaluation , did not reveal the presence of any further association. SNP rs363050 encompasses a regulatory element leading to SNAP-25 expression decrease. The results obtained in humans studies reported a strong association between SNAP-25 SNP rs363050 polymorphism and cognitive functions. rs363050 SNP is localized in intron 1 of the gene coding for SNAP-25; as regulatory elements are often present in introns of genes,35, 36, 37, 38 we conducted, by means of the luciferaseiferase reporter gene assay, an analysis of rs363050 SNP functional effect on transcriptional activity with the aim to define whether it could have a key role in the SNAP-25 gene expression. A series of plasmids, in which the region encompassing the rs363050 SNP and carrying either the parental or the minor allele was inserted in single or four concatenated copies upstream and/or downstream the thymidine kinase promoter in pGL4 basic vector, were originated . Their activity was tested by means of transient transfection of the human neuroblastoma SH-SY5Y cell line and compared with that of the plasmid without the cassette . The A allele did not affect transcription regulation of the reference plasmid when present in single copy, but had a slight, although statistical significant increase when in four copies . The presence of the susceptible G allele resulted in a statistical significant decrease in luciferaseiferase activity of 30% and 42% , respectively. When the same cassettes were inserted downstream the luciferase reporter gene, both constructs showed a marked decrease in the capability of driving the expression of the reporter gene of 60% with respect to the thymidine kinase promoter . However, the reduced transcription capability of the minor allele with respect to the parental allele was again observed . As a control, three concatenated copies of the sequence, surrounding the rs363043 polymorphic site, were tested . No effect on transcription was measured in the presence of both the parental allele and minor allele . Adolescent SNAP-25+/− mice are impaired in motor activity, memory, social interaction and show reduced SNAP-25 expression: therapeutic effect of VLP. Adolescent SNAP-25+/− mice are impaired in motor activity, memory, social interaction and show reduced SNAP-25 expression: therapeutic effect of VLP. Given the SNP rs363050 was strongly associated with cognitive scores in Autism Spectrum Disorder children and since the rs363050 minor allele displayed a reduced transcription capability, we evaluated the behavioural profile of 6-week-old SNAP-25+/− mice in order to define whether reductions of the protein levels could affect the cognitive profile in young individuals. Furthermore, as acute treatment with VLP has been previously demonstrated to abolish associative memory defects in adult SNAP-25+/− mice,21 animals were exposed to plain water or VLP, for 21 days, 24 h per day. The mean daily intake was not different between VLP- and water-exposed mice. The VLP amount corresponded to 250–270 mg kg−1 per day . Analysis of motor activity was carried out in mice of both genotypes in basal conditions and after chronic VLP treatment. The time course of horizontal activity, recorded every 10 min for 4 h and after D-amphetamine injection for 3 h after water or VLP pre-exposure, is reported in Supplementary Figure 2. Analysis of the time course , evaluated as blocks of 1-h each, showed that SNAP-25+/− mice were hyperactive. Amphetamine treatment significantly increased the number of horizontal movements in SNAP-25+/+ water-exposed mice, but it was ineffective in SNAP-25+/− mice. Any difference among the groups on the mean horizontal activity counts after VLP was shown, confirming that the drug normalized motor activity in the SNAP-25+/− mice. When tested for conditioned taste aversion with saccharin , SNAP-25+/− mice exhibited a significantly attenuated conditioned taste aversion, as they avoided the saccharin solution to a lesser degree compared with SNAP-25+/+ mice during choice tests. Repeated treatment with VLP induced a significant decrease in saccharin intake in the SNAP-25+/− mice compared with the water-exposed controls without affecting the intake of sweet solution in wild-type animals, suggesting a recovery in conditioned taste aversion. Mutant and control mice drank comparable amounts of fluid during the conditioning sessions , excluding a general alteration of fluid consumption or taste. When tested for sociability, SNAP-25+/+ water-exposed mice appeared normal, spending longer time to explore the compartment with the stranger mouse than the empty cage. Conversely, SNAP-25+/− mice, pre-exposed to water, spent more time in the empty compartment . When tested for social recognition , SNAP-25+/− mice remained close to the familiar stranger for the same time, suggesting an impaired social recognition. Both genotypes spent equal time in the central compartment. Pre-treatment with chronic VLP significantly rescued both sociability and social novelty deficits. SNAP-25+/− adolescent mice were impaired in episodic memory, as indicated by the altered discrimination index in the novel object recognition test . SNAP-25+/− mice exposed to water exhibited a reduced discrimination index compared with their littermates. VLP exposure slightly, but not significantly, decreased SNAP-25+/+ performance, whereas it was able to significantly recover SNAP-25+/− mice deficit. Western blotting analysis of SNAP-25 expression in the hippocampi and prefrontal cortex of 6–7-week-old mice, water exposed, revealed a reduction of about 30 and 20% expression in SNAP-25+/− tissue relative to wild type, respectively , in line with previously reported findings evaluated in the cortex.21 Chronic treatment with VLP completely rescued, only in the hippocampi, expression in SNAP-25+/−. These findings open the possibility that the behavioural rescue observed in SNAP-25+/− mice upon VLP treatment might be at least partially associated with increased protein levels. Basal electroencephalogram activity is characterized by spike activity in adolescent SNAP-25+/− mice: VLP normalizes at least for 1 week the electroencephalogram recording. In basal conditions, adolescent SNAP-25+/− mice displayed electroencephalogram abnormalities in terms of spike activity during 24-h recording , as previously shown also in the adult heterozygous mice.21 Two representative traces of one SNAP-25+/+ and one SNAP-25+/− mouse are reported. In basal conditions SNAP-25+/+ tracing appeared normal, whereas that of SNAP-25+/− mouse was characterized by an abnormal and recurrent increase of amplitude. Twenty-four hours after chronic 21-day VLP exposure, heterozygous tracing was normalized. VLP pre-exposure had no effects on the wild-type electroencephalogram profile. The quantitative analysis of the mean number of spikes, evaluated for 2 h and in the following 3 weeks after VLP withdrawal in both genotypes , revealed a reduction of spikes in SNAP-25+/− mice during the first week, which progressively returned to basal value within the third week. Accordingly, a 15% decrease of SNAP-25 expression in heterozygous hippocampi was shown after VLP withdrawal. The goal of the present study was to obtain supportive evidence for association between SNAP-25 gene and Autism Spectrum Disorder-specific scores, using multiple strategies. First, we found that among five SNAP-25 single-nucleotide polymorphisms in the SNAP-25 gene, the SNAP-25 single-nucleotide polymorphisms rs363050 showed significant relation with altered cognitive scores in Autism Spectrum Disorder children. Our findings agree with others,39 where an association between rs363050 putative risk allele with intellectual disability traits was suggested. Different SNAP-25 gene polymorphisms have been suggested to associate with related traits of autism17 and ADHD,40 working memory ability41 including short-/long-term memory and visual attention.16 We cannot exclude a linkage disequilibrium effect or an ethnic effect, which may explain the involvement of different SNAP-25 single-nucleotide polymorphisms in the same SNAP-25 genetic locus. For this reason replication studies using larger case studies are warranted. In this study, we performed a more in depth analysis of the possible functional role of rs363050 SNP to better understand its involvement in SNAP-25 expression. The analysis of transcriptional activity revealed that SNP rs363050 spans a region containing a regulatory element whose function is dependent on its position; furthermore, the presence of the minor allele rs363050 influences the transcription of the SNAP-25 gene. This could be due to the impairment of binding of factors involved in the modulation of the SNAP-25 gene expression level or in the binding of other factors, different from the ones that recognize the sequence of the parental allele, acting as a repressor. Due to the importance that the presence of the minor allele can have on SNAP-25 expression levels, experiments aimed to identify and characterize this factor will be further exploited. SNAP-25 has a central role in synaptic transmission and plasticity.4, 40, 42, 43 The protein forms a complex with syntaxin and the synaptic vesicle proteins , which is required for the Ca++-mediated exocytosis of the neurotransmitter into the synaptic cleft. The protein is also involved in the processes of axon growth44 and dendritic spine morphogenesis.45 Changes in the levels of expression of the SNAP-25 protein may influence the functioning of synaptic circuits associated with cognitive functions. Our findings on adolescent SNAP-25+/− mice strongly corroborate the association between SNAP-25 and cognitive function. A significant impairment in different forms of memory was found when SNAP-25 protein expression was reduced. Memory deficits were observed in three different forms of memory: episodic, aversive and social. About the latter, social recognition disability was accompanied by a decrease of social interaction, suggesting an autistic-like trait. Autism Spectrum Disorder are often accompanied by co-morbidity including hyperactivity and seizures , which are clinical features shared with ADHD.46 A significant correlation between SNAP-25 gene polymorphism and hyperactivity in a cohort of children with a diagnosis of Autism Spectrum Disorder has been previously found.17 Interestingly, the behavioural profile of adolescent SNAP-25+/− mice confirmed hyperactivity, as previously shown in mice of the same age,21 and we believe revealed for the first time abnormal electroencephalogram characterized by frequent spikes of high amplitude, already in very young mice. Notably, comparing the behavioural deficit previously observed in adults,21 adolescent SNAP-25+/− mice showed a similar cognitive deficit but a greater impairment of social behaviour and social recognition. In contrast, electroencephalogram abnormality was less pronounced in adolescent SNAP-25+/− mice. These findings are in line with what happens in autistic patients. Findings on intellectual functioning outcome in autistic adulthood revealed that intelligence quotient scores tend to remain stable overtime in the majority of studies.47 More difficult is the comparison between mice and patients about social behaviour: large individual differences were found, although autism-related symptoms and behaviour generally improve with age.47 Epilepsy increases with age48, 49 and the cumulative risk of epilepsy in adults with autism is estimated at 20–35%.50 The abnormal electroencephalogram activity could be a factor contributing to learning and is indeed well established that epileptiform electroencephalogram discharges unaccompanied by overt clinical change may be associated with transitory cognitive impairment detectable by appropriate psychological testing;51 also, a decline in intelligence quotient score in patients affected by epilepsy has been reported.52 Repeated exposure to VLP, largely normalized, as expected, the altered electroencephalogram profile but, surprisingly, it exerted positive effects on all behavioural deficits, including hyperactivity. VLP is known to have a broad spectrum of actions: it reduces neuronal excitability regulating the glutamate/GABA neurotransmitters system and modulating the synaptic/inhibitory balance. This modulation has been recently linked to its indirect action through astrocytes.53 In addition, VLP is an histone deacetylase inhibitor and also induces brain-derived neurotrophic factor and glial cell-line-derived neurotrophic factor NF transcription/expression in astrocytes to provide a consequent neuroprotective effect in vitro.54 We observed detrimental effects induced by prolonged exposure to VLP in SNAP-25+/+ mice on object recognition and slightly on conditioned taste aversion. VLP can interfere with learning and memory processes both in experimental models55, 56 and patients. Indeed, it has been reported to alter spatial learning in immature rats via the activation of protein kinase Cγ in hippocampal neurons.54 Altered dendritic morphology and impaired social transmission of food preference in epileptic mutant mice,56 after 3 months of exposure to oral VLP , have also been found. On the other hand, VLP reduced seizures, mortality and rescued a normal hippocampal long term potentiation in the same mice, in which severe seizures occurred in the early period of their life.56 Interestingly, in our experiments, VLP was able to rescue the decreased SNAP-25 expression into the hippocampus, suggesting the possibility of a direct effect on the protein expression levels. The mechanism by which VLP acts on SNAP-25 expression remains unclear. Hippocampus is an area strongly involved in different forms of memory. Future studies will be needed to evaluate the SNAP-25 level expression in other areas involved in motor function and sociability, such as striatum and amygdala. In conclusion, our current data, together with a previous study carried out in adult SNAP-25+/− mice,21 suggest that reduced levels of SNAP-25 protein expression are responsible for behavioural and electroencephalogram alterations in adolescent mice. Given rs363050, which associates with altered cognitive scores in Autism Spectrum Disorder children, leads to reduced protein expression, one could support our previous hypothesis that the reduction of SNAP-25 expression could be involved in the cognitive and neuropsychological deficits in children affected by Autism Spectrum Disorder.59 Notably, beside the autistic symptoms, SNAP-25+/− mice show a broad spectrum of deficits that mimic the well-known neuropsychiatric or neurologic disorders, such as ADHD, schizophrenia and epilepsy. In this context, VLP appears to gain significant attention for its potential therapeutic use. The potential mechanism through which alterations in SNAP-25 may have a direct role in the aetiology as well as contribute to the pathology of these disorders requires future studies."

    print(process_text(s))
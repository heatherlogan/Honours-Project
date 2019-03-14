from py2neo import Graph, Node, Relationship, NodeMatcher


def graph_relations(relations):

    relations = [
        (('Genes', '[heading]'), 'is_a', ('PMCID', '[paper]')),
        (('SFARI Genes', '[heading]'), 'is_a', ('PMCID', '[paper]')),
        (('ASD Phenotype', '[heading]'), 'is_a', ('PMCID', '[paper]')),
        (('Mutations', '[heading]'), 'is_a', ('PMCID', '[paper]')) ] + relations

    graph = Graph()
    matcher = NodeMatcher(graph)

    all_terms = []
    for t1, relation, t2 in relations:
        all_terms.append(t1)
        all_terms.append(t2)

    all_terms = list(set(all_terms))
    print((all_terms))

    for i, term in enumerate(all_terms):
        label, type = term[0], term[1]

        print(label, type)

        graph.create(Node(type, name=label))

    for t1, relation, t2 in relations:
        t1_label, t1_type = t1[0], t1[1]
        t2_label, t2_type = t2[0], t2[1]

        node1 = matcher.match(t1_type, name=t1_label).first()
        node2 = matcher.match(t2_type, name=t2_label).first()
        rel = Relationship(node1, relation, node2)
        print(i, rel)
        graph.create(rel)

if __name__ == "__main__":

    relations_ex = [
        ((('Genes', '[heading]')), 'is_a', ('PMCID', '[paper]')),
        (('SFARI Genes', '[heading]'), 'is_a', ('PMCID', '[paper]')),
        (('ASD Phenotype', '[heading]'), 'is_a', ('PMCID', '[paper]')),
        (('Mutations', '[heading]'), 'is_a', ('PMCID', '[paper]')),
        (('that', '[gngm]'), 'plays', ('a role in cellular proliferation', '[celf]')),
        (('development of the axonal tract', '[celf]'), 'have been associated', ('with a non-progressive neurological disease', '[fndg]')),
        (('several other genes', '[gngm]'), 'is_a', ('Genes', '[heading]')),
        (("'Autism Phenotype'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('that', '[gngm]'), 'plays', ('differentiation', '[celf]')),
        (('Chd2', '[gngm]'), 'leads', ('impaired memory', '[mobd]')),
        (('they', '[?]'), 'demonstrate', ('impaired perception of biological motion with motor control', '[menp]')),
        (('SCN1A mutations', '[genf]'), 'is_a', ('SFARI Genes', '[heading]')),
        (('UBE3A including GABRB3 GABRA5 GABRG3', '[ftcn]'), 'is_a', ('Genes', '[heading]')),
        (('social behavior phenotype NKX2-1 mutations', '[genf]'), 'have been associated',
         ('with a non-progressive neurological disease', '[fndg]')),
        (('The IQSEC2 variant phenotype', '[orga]'), 'includes', ('developmental delay', '[mobd]')),
        (('affected by attention-deficit/hyperactivity disorder', '[mobd]'), 'are associated',
         ('with deletion involving 11p14 .1', '[genf]')),
        (('adolescents', '[aggp]'), 'tend', ('childhood epilepsy', '[dsyn]')),
        (('adolescents', '[aggp]'), 'tend', ('to show an increased risk of attention-deficit/hyperactivity disorder')),
        (('which', '[gngm]'), 'encompasses', ('UBE3A including GABRB3 GABRA5 GABRG3', '[ftcn]')),
        (('which', '[gngm]'), 'is_a', ('Genes', '[heading]')),
        (('which', '[gngm]'), 'encompasses', ('several other genes', '[gngm]')),
        (('Cardiofaciocutaneous syndrome', '[cgab]'), 'are caused', ('by heterozygous germline mutations', '[genf]')),
        (('Angelman syndrome', '[dsyn]'), 'caused', ('by either disruptions of the gene UBE3A of chromosome 15', '[celc]')),
        (('IQSEC2 as a neurodevelopmental disability gene', '[gngm]'), 'is_a', ("'Learning Disorders'", '[pheno]')),
        (('IQSEC2 as a neurodevelopmental disability gene', '[gngm]'), 'is_a', ('SFARI Genes', '[heading]')),
        (('intellectual disability epilepsy hypotonia autism developmental regression', '[mobd]'), 'is_a',
         ("'Learning Disorders'", '[pheno]')),
        (("'Epilepsy'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('social behavior phenotype NKX2-1 mutations', '[genf]'), 'is_a', ('Mutations', '[heading]')),
        (('with deletion involving 11p14 .1', '[genf]'), 'is_a', ('Mutations', '[heading]')),
        (('Chd2', '[gngm]'), 'is_a', ('Genes', '[heading]')),
        (('to aberrant cortical network function', '[bpoc]'), 'is_a', ("'Tics and Mannerisms'", '[pheno]')),
        (('Costello syndrome', '[dsyn]'), 'are caused', ('by heterozygous germline mutations', '[genf]')),
        (('CDK5R1 gene', '[gngm]'), 'has been associated', ('with intellectual disability in humans', '[humn]')),
        (('RASopathies including Noonan syndrome', '[cgab,dsyn]'), 'are caused', ('in genes', '[gngm]')),
        (('The IQSEC2 variant phenotype', '[orga]'), 'includes', ('stereotypies', '[mobd]')),
        (('by either disruptions of the gene UBE3A of chromosome 15', '[celc]'), 'is_a', ('SFARI Genes', '[heading]')),
        (('Whole exome sequencing', '[mbrt]'), 'has established',
         ('IQSEC2 as a neurodevelopmental disability gene', '[gngm]')),
        (("'Affect'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('social behavior phenotype NKX2-1 mutations', '[genf]'), 'is_a', ('Genes', '[heading]')),
        (('Angelman syndrome', '[dsyn]'), 'caused', ('deletion', '[genf]')),
        (('intellectual disability epilepsy hypotonia autism developmental regression', '[mobd]'), 'is_a',
         ("'Epilepsy'", '[pheno]')),
        (('that', '[gngm]'), 'plays', ('survival', '[acty]')),
        (('developmental delay', '[mobd]'), 'are associated', ('with deletion involving 11p14 .1', '[genf]')),
        (('deletion', '[genf]'), 'is_a', ('Mutations', '[heading]')),
        (('in genes', '[gngm]'), 'is_a', ('Genes', '[heading]')),
        (("'Neurologic Indications'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('Children with epilepsy', '[podg]'), 'tend',
         ('affected by attention-deficit/hyperactivity disorder phenotype', '[mobd]')),
        (('UBE3A including GABRB3 GABRA5 GABRG3', '[ftcn]'), 'is_a', ('SFARI Genes', '[heading]')),
        (('cranial neural crest migration', '[bpoc]'), 'have been associated',
         ('with a non-progressive neurological disease', '[fndg]')),
        (('with intellectual disability in humans', '[humn]'), 'is_a', ("'Learning Disorders'", '[pheno]')),
        (('that', '[gngm]'), 'is_a', ('Genes', '[heading]')),
        (('CDK5R1 gene', '[gngm]'), 'is_a', ('Genes', '[heading]')),
        (('with a non-progressive neurological disease', '[fndg]'), 'is_a', ("'Neurologic Indications'", '[pheno]')),
        (('social behavior phenotype NKX2-1 mutations', '[genf]'), 'is_a', ("'Autism Phenotype'", '[pheno]')),
        (('to aberrant cortical network function', '[bpoc]'), 'is_a', ("'Tourette Syndrome'", '[pheno]')),
        (('they', '[?]'), 'demonstrate', ('problems', '[idcn]')),
        (("'Tourette Syndrome'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('The IQSEC2 variant phenotype', '[orga]'), 'is_a', ('SFARI Genes', '[heading]')),
        (('SCN1A mutations', '[genf]'), 'is_a', ('Mutations', '[heading]')),
        (('RASopathies including Noonan syndrome', '[cgab,dsyn]'), 'are caused',
         ('by heterozygous germline mutations', '[genf]')),
        (('IQSEC2 as a neurodevelopmental disability gene', '[gngm]'), 'is_a', ('Genes', '[heading]')),
        (('The IQSEC2 variant phenotype', '[orga]'), 'includes', ('microcephaly', '[cgab,dsyn]')),
        (('Costello syndrome', '[dsyn]'), 'are caused', ('in genes', '[gngm]')),
        (('The IQSEC2 variant phenotype', '[orga]'), 'includes',
         ('intellectual disability epilepsy hypotonia autism developmental regression', '[mobd]')),
        (('adolescents', '[aggp]'), 'tend', ('affected by attention-deficit/hyperactivity disorder phenotype', '[mobd]')),
        (('Chd2', '[gngm]'), 'leads', ('to aberrant cortical network function', '[bpoc]')),
        (('affected by attention-deficit/hyperactivity disorder phenotype', '[mobd]'), 'is_a', ("'Affect'", '[pheno]')),
        (('to show an increased risk of affected by attention-deficit/hyperactivity disorder','[idcn]'), 'is_a', ("'Affect'", '[pheno]')),
        (('The IQSEC2 variant phenotype', '[orga]'), 'is_a', ('Mutations', '[heading]')),
        (("'Attention Deficit Disorder with Hyperactivity'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('developmental delay', '[mobd]'), 'is_a', ("'Learning Disorders'", '[pheno]')),
        (('affected by attention-deficit/hyperactivity disorder', '[mobd]'), 'is_a', ("'Affect'", '[pheno]')),
        (('Cardiofaciocutaneous syndrome', '[cgab]'), 'are caused', ('in genes', '[gngm]')),
        (("'Learning Disorders'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('by heterozygous germline mutations', '[genf]'), 'is_a', ('Mutations', '[heading]')),
        (('autism', '[mobd]'), 'are associated', ('with deletion involving 11p14 .1', '[genf]')),
        (('obesity', '[dsyn]'), 'are associated', ('with deletion involving 11p14 .1', '[genf]')),
        (('Whole exome sequencing', '[mbrt]'), 'is_a', ('Genes', '[heading]')),
        (('affected by attention-deficit/hyperactivity disorder', '[mobd]'), 'is_a',
         ("'Attention Deficit Disorder with Hyperactivity'", '[pheno]')),
        (('SCN1A mutations', '[genf]'), 'cause', ('Dravet syndrome', '[dsyn]')),
        (("'Cognitive Ability'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('SCN1A mutations', '[genf]'), 'cause', ('GEFS +', '[dsyn]')),
        (('Children with epilepsy', '[podg]'), 'tend', ('to show an increased risk of affected by attention-deficit/hyperactivity disorder', '[idcn]')),
        (('impaired perception of biological motion with motor control', '[menp]'), 'is_a',
         ("'Cognitive Ability'", '[pheno]')),
        (("'Tics and Mannerisms'", '[pheno]'), 'is_a', ('ASD Phenotype', '[heading]')),
        (('Children with epilepsy', '[podg]'), 'tend', ('childhood epilepsy', '[dsyn]')),
        (('by either disruptions of the gene UBE3A of chromosome 15', '[celc]'), 'is_a', ('Genes', '[heading]')),
        (('Angelman syndrome', '[dsyn]'), 'caused', ('15q11-q13', '[celc]')),
    ]

    graph_relations(relations_ex)

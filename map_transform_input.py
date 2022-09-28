import pandas as pd
from configs import assistments as conf

MODEL = conf.config['GE_MODEL']['MODEL']
CONFIG = conf.config['GE_MODEL']['CONFIG']

INPUT_TRIPLES = conf.config['graphs']['possible_triples']
OUTPUT_FILE = conf.root_embs + f"{MODEL}/config{CONFIG}"+"/{}.list"
MAPPING_ENTITIES = conf.root_embs + f'{MODEL}/config{CONFIG}/entities.tsv'
MAPPING_RELATIONS = conf.root_embs + f'{MODEL}/config{CONFIG}/relations.tsv'

triples = pd.read_csv(INPUT_TRIPLES, names=['h', 'r', 't'])
id_entities = pd.read_csv(MAPPING_ENTITIES, names=['id', 'iri'])
id_relations = pd.read_csv(MAPPING_RELATIONS, names=['id', 'iri'])

triples = pd.merge(triples, id_entities, how='left', left_on='h', right_on='iri')
triples.drop(columns=['iri'], inplace=True)
triples.rename(columns={'id': 'head'}, inplace=True)
triples = pd.merge(triples, id_entities, how='left', left_on='t', right_on='iri')
triples.drop(columns=['iri'], inplace=True)
triples.rename(columns={'id': 'tail'}, inplace=True)
triples = pd.merge(triples, id_relations, how='left', left_on='r', right_on='iri')
triples.drop(columns=['iri'], inplace=True)
triples.rename(columns={'id': 'rel'}, inplace=True)

triples['head'].to_csv(OUTPUT_FILE.format('heads'), index=False, header=False)
triples['rel'].to_csv(OUTPUT_FILE.format('rels'), index=False, header=False)
triples['tail'].to_csv(OUTPUT_FILE.format('tails'), index=False, header=False)

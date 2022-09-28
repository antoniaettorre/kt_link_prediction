import pandas as pd
import logging
import numpy as np
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix, accuracy_score, recall_score, roc_curve, auc, \
    precision_score, balanced_accuracy_score
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
from configs import assistments as conf

SCORE_TH = -50
LIMIT = 1
LIMIT_MODE = 'head'
TEST = conf.TEST
DATASET = conf.config['DS']
MODEL = conf.config['GE_MODEL']['MODEL']
CONFIG = conf.config['GE_MODEL']['CONFIG']
APPROX_KT = True
OPTIMIZE = False

MODE = 'triplet_wise'
# File containing the triples that have been predicted
RESULT_FILE = conf.root_embs + f"{MODEL}/config{CONFIG}/result.tsv"
# File containing the real triples (that we want to predict)
TRUTH_FILE = conf.config["graphs"]["real_triples"]
# File containing all the possible triples that could be there given the set of answers we want to predict
DATASET_FILE = conf.config["graphs"]["possible_triples"]
# Files to map the elements id in results with their IRI
MAPPING_ENTITIES = conf.root_embs + f'{MODEL}/config{CONFIG}/entities.tsv'
MAPPING_RELATIONS = conf.root_embs + f'{MODEL}/config{CONFIG}/relations.tsv'

logging.basicConfig(filename=f'results/{DATASET}/result_test{TEST}_{MODEL}_{CONFIG}.log', filemode='w', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')


def map_id_to_uri(results, id_entities, id_relations):
    triples = pd.merge(results, id_entities, how='left', left_on='head', right_on='id')
    triples.drop(columns=['id', 'head'], inplace=True)
    triples.rename(columns={'iri': 'h'}, inplace=True)
    triples = pd.merge(triples, id_entities, how='left', left_on='tail', right_on='id')
    triples.drop(columns=['id', 'tail'], inplace=True)
    triples.rename(columns={'iri': 't'}, inplace=True)
    triples = pd.merge(triples, id_relations, how='left', left_on='rel', right_on='id')
    triples.drop(columns=['id', 'rel'], inplace=True)
    triples.rename(columns={'iri': 'r'}, inplace=True)
    return triples


def remove_low_score_triples(triples, dataset, truth):
    attr = 'h'
    triples = triples.loc[triples['score'] > SCORE_TH]
    triples.reset_index(inplace=True, drop=True)
    entities = list(triples[attr].unique())
    dataset = dataset.loc[dataset[attr].isin(entities)]
    dataset.reset_index(inplace=True, drop=True)
    truth = truth.loc[truth[attr].isin(entities)]
    truth.reset_index(inplace=True, drop=True)
    return triples, dataset, truth


def remove_extra_triples(triples, l, mode='all'):
    if mode == "all":
        triples.sort_values(by=['score'], inplace=True, ascending=False)
        triples.reset_index(inplace=True, drop=True)
        return triples[0:l]
    attr = 'h'
    if mode == 'rel':
        attr = "r"
    elif mode == 'tail':
        attr = 't'
    triples.sort_values(by=[attr, 'score'], inplace=True, ascending=False)
    triples.reset_index(inplace=True, drop=True)
    indices = triples.drop_duplicates(subset=[attr])[[attr]]
    indices['ind'] = list(indices.index)
    df = pd.merge(triples, indices, how='left', on=attr)
    df['dist'] = list(df.index) - df['ind']
    df = df.loc[df['dist'] < l]
    df.drop(columns=['ind', 'dist'], inplace=True)
    return df


def normalize_score_for_auc(triples):
    a = triples.groupby('h')['score'].apply(sum).reset_index(name='tot_score')
    triples = pd.merge(triples, a, how='right', on='h')
    triples['temp_score'] = triples['score']/triples['tot_score']
    norm_score1 = 1 - triples.loc[triples['t'].str.contains('_1')]['temp_score']
    norm_score0 = triples.loc[~triples['t'].str.contains('_1')]['temp_score']
    triples['norm_score'] = norm_score1.append(norm_score0)
    triples.drop(columns=['tot_score', 'temp_score'], inplace=True)
    return triples

def compute_custom_metrics(triples, truth, approx):
    logging.info('Performance on final prediction task')
    res, y_test, y_pred = conf.get_KT_results(triples, truth, approx)
    fpr, tpr, thresholds = roc_curve(y_test, y_pred)
    bacc = tpr - fpr
    i_max = np.where(bacc == np.amax(bacc))[0][0]
    best_t = thresholds[i_max]
    roc_auc = auc(fpr, tpr)
    display = RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc)
    display.plot()
    plt.show()
    if OPTIMIZE:
        logging.info(
            '> Best test TH: {}'.format(best_t)
        )
        res = y_pred >= best_t
    if approx:
        logging.info(
            '> AUC with norm-score: {}'.format(roc_auc_score(y_test, y_pred))
        )
        logging.info(
            '> F1-scores: {}'.format(
                f1_score(y_test, res, average=None)
            )
        )
        logging.info(
            '> ACC: {}'.format(accuracy_score(y_test, res))
        )
        logging.info(
            '> RECALL: {}'.format(recall_score(y_test, res))
        )
        logging.info(
            '> PRECISION: {}'.format(precision_score(y_test, res))
        )
        logging.info(
            '> BALANCED ACCURACY: {}'.format(balanced_accuracy_score(y_test, res))
        )
    else:
        logging.info('> F1-score micro:' + str(f1_score(y_test, res, average='micro')))
        logging.info('> F1-score macro:' + str(f1_score(y_test, res, average='macro')))
        logging.info('> F1-score weighted:' + str(f1_score(y_test, res, average='weighted')))
        cm = confusion_matrix(y_test, res)
        tn, fp, fn, tp = cm.ravel()
        logging.info(f"TN: {tn}, FP: {fp}, FN: {fn}, TP: {tp}")
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp = disp.plot()
        plt.show()


logging.info(f'Analyzing results in {RESULT_FILE}')
logging.info(f'Test: test{TEST}')
logging.info(f'GE Model: {MODEL}')
logging.info(f'GE config for model: {CONFIG}')
logging.info(f"Settings: LIMIT={LIMIT}, LIMIT_MODE={LIMIT_MODE}")

results = pd.read_csv(RESULT_FILE, sep="\t")
id_entities = pd.read_csv(MAPPING_ENTITIES, names=['id', 'iri'])
id_relations = pd.read_csv(MAPPING_RELATIONS, names=['id', 'iri'])
truth = pd.read_csv(TRUTH_FILE, names=['h', 'r', 't'])
dataset = pd.read_csv(DATASET_FILE, names=['h', 'r', 't'])


triples = map_id_to_uri(results, id_entities, id_relations)
triples = normalize_score_for_auc(triples)
triples, dataset, truth = remove_low_score_triples(triples, dataset, truth)

triples['triple'] = triples['h'] + triples['r'] + triples['t']
dataset['triple'] = dataset['h'] + dataset['r'] + dataset['t']
truth['triple'] = truth['h'] + truth['r'] + truth['t']


triples = remove_extra_triples(triples, LIMIT, LIMIT_MODE)
triples.drop(columns=['score'], inplace=True)

dataset['predict'] = dataset['triple'].isin(triples['triple'])
dataset['target'] = dataset['triple'].isin(truth['triple'])

compute_custom_metrics(triples, truth, APPROX_KT)
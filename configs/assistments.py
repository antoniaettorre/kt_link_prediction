
root = 'data/datasets/assistments/'
root_graph = 'data/graphs/assistments/'
root_embs = 'data/gembs/assistments/'
TEST = '0'

config = {
    'DS': 'assistments',
    'datasets': {
        'train_answers': root + 'train_answers.csv',
        'test_answers': root + 'test_answers.csv',
    },
    'graphs': {
        'complete': root_graph + 'graph.ttl',
        'csv_graph': root_graph + 'graph.txt',
        'possible_triples': root_graph + 'triples_possible.txt',
        'real_triples': root_graph + 'triples_real.txt',
    },
    'GE_MODEL': {
        'MODEL': 'TransE_l2',
        'CONFIG': '0'
    },
    'NAMESPACES': {
        'ass': 'http://www.assistment-test.org/',
        'owl': 'http://www.w3.org/2002/07/owl#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'schema': 'https://schema.org/'
    }
}


def prepare_data_for_triples(data):
    data.drop_duplicates(subset=['order_id'], inplace=True)
    data['answer'] = "ass_answer" + data['order_id'].astype(str)
    data['selection'] = 'ass_' + data['problem'].astype(str) + '_' + data['correct'].astype(str)
    return data


def get_subjects(data):
    return data['answer']


def get_possible_rel_for_subj(s, data):
    return ["ass_has_correctly_selected", "ass_has_incorrectly_selected"]


def get_real_rel_for_subj(s, data):
    res = data.loc[data['answer'] == s]['correct'].to_list()[0]
    if res == 1:
        return ["ass_has_correctly_selected"]
    return ["ass_has_incorrectly_selected"]

def get_possible_obj_for_subj_rel(s, r, data):
    question = data.loc[data['answer'] == s]['problem'].to_list()[0]
    if r == "ass_has_correctly_selected":
        return ['ass_' + question + '_1']
    return ['ass_' + question + '_0']


def get_real_obj_for_subj_rel(s, r, data):
    res = data.loc[data['answer'] == s]['selection'].to_list()
    return res


def get_KT_results(predicted, target, approx):
    predicted.sort_values(by=['h'], inplace=True)
    target.sort_values(by=['h'], inplace=True)
    predicted['approx'] = predicted['t'].str.contains('_1')
    target['approx'] = target['t'].str.contains('_1')
    return predicted['approx'].values, target['approx'].values, predicted['norm_score'].values
import pandas as pd
import logging

def format_IRI(IRI, NAMESPACE_LIST):
    name = str(IRI)
    for p in NAMESPACE_LIST:
        name = name.replace(NAMESPACE_LIST[p], p+'_')
    return name


NAMESPACE_LIST = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'schema': 'https://schema.org/',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'xml': 'http://www.w3.org/2001/XMLSchema#',
    'xsd': 'http://www.w3.org/XML/1998/namespace'
}


class GenerateTriples:

    def __init__(self, conf, real=False):
        self.INPUT_FILE = conf.config['datasets']['test_answers']
        self.OUTPUT_FILE = conf.config['graphs']['real_triples' if real else 'possible_triples']

        self.prepare_data = conf.prepare_data_for_triples
        self.get_subjects = conf.get_subjects
        self.get_rel_for_subj = conf.get_real_rel_for_subj if real else conf.get_possible_rel_for_subj
        self.get_obj_for_subj_rel = conf.get_real_obj_for_subj_rel if real else conf.get_possible_obj_for_subj_rel

        NAMESPACE_LIST.update(conf.config['NAMESPACES'])

    def __call__(self, *args, **kwargs):
        data = pd.read_csv(self.INPUT_FILE)
        data = self.prepare_data(data)
        triples = {
            "subjs": [],
            "rels": [],
            "objs": []
        }
        for s in self.get_subjects(data):
            logging.debug(f'Treating subject: {s}')
            for r in self.get_rel_for_subj(s, data):
                for o in self.get_obj_for_subj_rel(s, r, data):
                    triples["subjs"].append(format_IRI(s, NAMESPACE_LIST))
                    triples["rels"].append(format_IRI(r, NAMESPACE_LIST))
                    triples["objs"].append(format_IRI(o, NAMESPACE_LIST))

        pd.DataFrame(triples).to_csv(self.OUTPUT_FILE, index=False, header=False)

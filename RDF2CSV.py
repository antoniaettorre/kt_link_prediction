from rdflib import Graph, Literal
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


class RDF2CSV:
    def __init__(self, conf):
        self.GRAPH_FILE = conf.config["graphs"]["complete"]
        self.OUTPUT_FILE = conf.config["graphs"]["csv_graph"]
        NAMESPACE_LIST.update(conf.config['NAMESPACES'])

    def __call__(self, *args, **kwargs):
        logging.info(f"Opening TURTLE file for graph {self.GRAPH_FILE}...")
        rdf_graph = Graph()
        rdf_graph.parse(self.GRAPH_FILE, format="turtle")
        logging.info(f"Number of triples in the original graph: {len(rdf_graph)}")
        edge_sources = []
        edge_targets = []
        edge_types = []
        i = 0
        for s, p, o in rdf_graph.triples((None, None, None)):
            subj = format_IRI(s, NAMESPACE_LIST)
            obj = format_IRI(o, NAMESPACE_LIST)
            edge_sources.append(subj)
            edge_targets.append(obj)
            edge_types.append(format_IRI(p, NAMESPACE_LIST))
            i = i + 1
            if i % 10000 == 0:
                logging.debug(f"Processed {i} triples...")

        df = pd.DataFrame(
            {
                "h": edge_sources,
                "p": edge_types,
                "t": edge_targets
            }
        )
        logging.info("Saving CSV...")
        df.to_csv(self.OUTPUT_FILE, index=False, header=False)


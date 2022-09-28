import logging
import os
from RDF2CSV import RDF2CSV
from generate_triples import GenerateTriples
from configs import assistments as conf


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')

logging.info("Starting preprocessing pipeline...")

if not os.path.exists(conf.config['graphs']['csv_graph']):
    logging.info('Converting graph to list of triples...')
    rdf2csv = RDF2CSV(conf)
    rdf2csv()
else:
    logging.info('CSV file exists already, skipping conversion...')

if not os.path.exists(conf.config['graphs']['possible_triples']):
    logging.info("Creating possible triples' list...")
    gt = GenerateTriples(conf, False)
    gt()
else:
    logging.info('List of possible triples exists already, skipping...')
if not os.path.exists(conf.config['graphs']['real_triples']):
    logging.info("Creating real triples' list...")
    gt = GenerateTriples(conf, True)
    gt()
else:
    logging.info('List of real triples exists already, skipping...')

embs_dir = conf.root_embs
model_dir = os.path.join(embs_dir, conf.config['GE_MODEL']['MODEL'])
if not os.path.exists(model_dir):
    os.mkdir(model_dir)
config_dir = os.path.join(model_dir, 'config' + conf.config['GE_MODEL']['CONFIG'])
if not os.path.exists(config_dir):
    os.mkdir(config_dir)

logging.info("Preprocessing done!")

exit(0)







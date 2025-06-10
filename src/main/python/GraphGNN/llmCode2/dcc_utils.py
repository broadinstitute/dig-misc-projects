
# imports
import logging
import sys 
import json

# settings
# logging.basicConfig(level=logging.INFO, format=f'[%(asctime)s] - %(levelname)s - %(name)s %(threadName)s : %(message)s')
# handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO, 
    format=f'[%(asctime)s] - %(levelname)s - %(name)s %(threadName)s : %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


# constants
KEY_NODE_FILES = "node_files"
KEY_INFERENCE = "inference"
KEY_DATA_MAPPING = "dataset_mapping"
KEY_NODE_EMBEDDINGS = "node_embeddings"
KEY_MODEL_PATH = "model_path"

# methods
def get_logger(name): 
    # get the logger
    logger = logging.getLogger(name)
    # logger.addHandler(handler)

    # return
    return logger 


def load_config(config_path='config.json'):
    config = None
    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


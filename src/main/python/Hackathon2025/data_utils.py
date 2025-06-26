
# imports
import csv 
import logging
import sys


# constants
DEBUG = False
DIR_DATA = '/Users/mduby/Data/Broad/Hackathon25/Data'
FILE_GENES = '{}/orphanet_genes.txt'.format(DIR_DATA)
FILE_PHENOTYPES = '{}/orphanet_all_frequency_hpo.txt'.format(DIR_DATA)

logging.basicConfig(
    level=logging.INFO, 
    format=f'[%(asctime)s] - %(levelname)s - %(name)s %(threadName)s : %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


# methods
def get_logger(name): 
    # get the logger
    logger = logging.getLogger(name)
    # logger.addHandler(handler)

    # return
    return logger 

logger = get_logger(__name__)


def load_gene_disease_mapping(file_path):
    gene_dict = {}
    map_sorted_gene = {}

    with open(file_path, 'r') as f:
        next(f)
        for line in f:
            line = line.strip()
            if not line:
                continue

            # log
            if DEBUG:
                print("for line: {}".format(line))

            # split into disease_id and (optional) gene:weight list
            parts = line.split(maxsplit=1)
            disease_id = parts[0]
            if len(parts) == 1 or not parts[1].strip():
                # no genes on this line
                continue
            # parse each gene:weight (they’re semicolon-separated)
            for pair in parts[1].split(';'):
                gene, weight_str = pair.split(':')
                try:
                    weight = float(weight_str)
                except ValueError:
                    # skip malformed weights
                    continue
                gene_dict.setdefault(gene, []).append({disease_id: weight})

    # sort
    for key, value in gene_dict.items():
        map_sorted_gene[key] = sort_list(list_of_dicts=value)

    # return
    # return gene_dict
    return map_sorted_gene


def load_pheno_disease_mapping(file_path):
    # initialize
    pheno_dict = {}
    map_sorted_pheno = {}

    # load the file
    with open(file_path, newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        # extract phenotype codes (all fieldnames except the first)
        pheno_codes = reader.fieldnames[1:]
        # initialize list for each phenotype
        for ph in pheno_codes:
            pheno_dict[ph] = []

        for row in reader:
            disease_id = row[reader.fieldnames[0]]
            for ph in pheno_codes:
                val = row[ph].strip()
                if not val:
                    # skip empty cells
                    continue
                try:
                    weight = float(val)
                except ValueError:
                    # skip non-numeric entries
                    continue
                if weight > 0:
                    pheno_dict[ph].append({disease_id: weight})

    # sort
    for key, value in pheno_dict.items():
        map_sorted_pheno[key] = sort_list(list_of_dicts=value)

    # return
    # return pheno_dict
    return map_sorted_pheno


def sort_list(list_of_dicts):
    return sorted(list_of_dicts, key=lambda x: list(x.values())[0], reverse=True)

if __name__ == "__main__":
    # instantiate
    map_genes = {}
    map_pheno = {}
    # file_genes = "/Users/mduby/Data/Broad/Hackathon25/Data/orphanet_genes.txt"
    # file_pheno = "/Users/mduby/Data/Broad/Hackathon25/Data/phen_small.txt"
    file_genes = FILE_GENES
    file_pheno = FILE_PHENOTYPES

    # load the file
    map_genes = load_gene_disease_mapping(file_path=file_genes)

    # test
    list_gene = ['NFIA', 'BMP2', 'L2HGDH', 'PPARG']
    for gene in list_gene:
        list_disease = map_genes.get(gene, {})
        print("got {} for gene: {}".format(list_disease, gene))

    # load the pheno file
    map_pheno = load_pheno_disease_mapping(file_path=file_pheno)

    # test
    list_pheno = ['HP.0000175', 'HP.0000995', 'HP.0001269']
    for pheno in list_pheno:
        list_disease = map_pheno.get(pheno, {})
        print("got {} for gene: {}".format(list_disease, pheno))



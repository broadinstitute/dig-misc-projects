
# imports
import csv 
import logging
import sys


# constants
DEBUG = False
DIR_DATA = '/Users/mduby/Data/Broad/Hackathon25/Data'

FILE_HPO = "{}/hpo_id.csv".format(DIR_DATA)
FILE_ORPHANET = "{}/Orpha_id.tsv".format(DIR_DATA)
FILE_GENES = '{}/orphanet_genes.txt'.format(DIR_DATA)
# FILE_PHENOTYPES = '{}/orphanet_all_frequency_hpo.txt'.format(DIR_DATA)
FILE_PHENOTYPES = '{}/phen_small.txt'.format(DIR_DATA)

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


def load_orpha_terms(filename=FILE_ORPHANET):
    """
    Read Orpha terms file into a dictionary.
    
    Args:
        filename (str): Path to the file (tab or space separated)
        
    Returns:
        dict: Dictionary with OrphaID as keys and Name as values
    """
    orpha_dict = {}
    
    with open(filename, 'r', encoding='utf-8') as file:
        # Skip header line
        next(file)
        
        for line in file:
            line = line.strip()
            if line:  # Skip empty lines
                # Split on whitespace (handles both tabs and spaces)
                parts = line.split(None, 1)  # Split on first whitespace only
                if len(parts) == 2:
                    orpha_id, name = parts
                    orpha_dict[orpha_id] = name
    
    return orpha_dict


def load_hpo_terms(filename=FILE_HPO):
    """
    Read HPO terms CSV file into a dictionary.
    
    Args:
        filename (str): Path to the CSV file
        
    Returns:
        dict: Dictionary with HPO_terms as keys and Description as values
    """
    hpo_dict = {}
    
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hpo_dict[row['HPO_terms'].replace(':', '.')] = row['Description']
    
    return hpo_dict


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
                gene_dict.setdefault(gene, []).append({'Orpha:{}'.format(disease_id): weight})

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

# constants
MAP_GENES = load_gene_disease_mapping(file_path=FILE_GENES)
print("loaded gene map of size: {}".format(len(MAP_GENES)))
MAP_PHENOTYPES = load_pheno_disease_mapping(file_path=FILE_PHENOTYPES)
print("loaded phenotype map of size: {}".format(len(MAP_PHENOTYPES)))
MAP_ORPHANET = load_orpha_terms()
print("loaded orpahnet map of size: {}".format(len(MAP_ORPHANET)))

def get_map_disease_for_gene_list(list_genes):
    '''
    return a map of disease with concatenated scores
    '''
    # initialize
    map_result = {}
    map_sorted = {}

    # get the gene data
    for gene in list_genes:
        list_disease = MAP_GENES.get(gene, [])
        for item in list_disease:
            for key, value in item.items():
                map_result[key] = map_result.get(key, 0.0) + value

    # sort

    # return
    return map_result


def get_map_disease_for_pheno_list(list_phenotypes):
    '''
    return a map of disease with concatenated scores
    '''
    # initialize
    map_result = {}

    # get the gene data
    for pheno in list_phenotypes:
        list_disease = MAP_PHENOTYPES.get(pheno, [])
        for item in list_disease:
            for key, value in item.items():
                map_result[key] = map_result.get(key, 0.0) + value

    # sort

    # return
    return map_result


def translate_map_to_sorted_list(map_disease):
    # initialize
    list_disease = []

    # loop
    for key, value in map_disease.items():
        name = MAP_ORPHANET.get(key.replace('Orpha:', ''), key)
        list_disease.append({'disease': {'id': key, 'name': name}, 'score': value})

    # sort
    sorted_list_desc = sorted(list_disease, key=lambda x: x['score'], reverse=True)

    # return
    return sorted_list_desc


def get_list_disease_for_entity_list(list_input, max_value=1000, for_genes=True):
    if for_genes:
        # get the map of disease
        map_disease = get_map_disease_for_gene_list(list_genes=list_input)

        # get the sorted list
        list_disease = translate_map_to_sorted_list(map_disease=map_disease)

    else:
        # first replace the : by . for all entries
        list_updated = [s.replace(':', '.') for s in list_input]
        print("for input: {}, got: {}".format(list_input, list_updated))

        # get the map of disease
        map_disease = get_map_disease_for_pheno_list(list_phenotypes=list_updated)

        # get the sorted list
        list_disease = translate_map_to_sorted_list(map_disease=map_disease)

    # return number wanted
    return list_disease[:max_value]


# main
if __name__ == "__main__":
    # instantiate
    map_genes = {}
    map_pheno = {}
    # file_genes = "/Users/mduby/Data/Broad/Hackathon25/Data/orphanet_genes.txt"
    # file_pheno = "/Users/mduby/Data/Broad/Hackathon25/Data/phen_small.txt"
    file_genes = FILE_GENES
    file_pheno = FILE_PHENOTYPES

    # load the file
    # map_genes = load_gene_disease_mapping(file_path=file_genes)
    map_genes = MAP_GENES

    # test
    list_gene = ['NFIA', 'BMP2', 'L2HGDH', 'PPARG']
    for gene in list_gene:
        list_disease = map_genes.get(gene, {})
        print("got {} for gene: {}".format(list_disease, gene))

    # test the gene list
    list_disease = get_map_disease_for_gene_list(list_genes=list_gene)
    print("\nfor list of genes: {}, got map of diseases: {}".format(list_gene, list_disease))
    print("\nfor list of genes: {}, got formatted  list of diseases: {}".format(list_gene, translate_map_to_sorted_list(map_disease=list_disease)))

    # rest call test
    list_disease = get_list_disease_for_entity_list(list_input=list_gene)
    print("\nfor list of genes: {}, got REST list of diseases: {}".format(list_gene, list_disease))

    # load the pheno file
    # map_pheno = load_pheno_disease_mapping(file_path=file_pheno)
    map_pheno = MAP_PHENOTYPES

    # test
    list_pheno = ['HP.0000175', 'HP.0000995', 'HP.0001269']
    for pheno in list_pheno:
        list_disease = map_pheno.get(pheno, {})
        print("\ngot {} for gene: {}".format(list_disease, pheno))

    # read hpo map
    map_hpo = load_hpo_terms()
    list_pheno = ['HP.0000175', 'HP.0000995', 'HP.0001269']
    for pheno in list_pheno:
        print("for hpo: {}, got name: {}".format(pheno, map_hpo.get(pheno)))

    # read hpo map
    map_orpha = load_orpha_terms()
    list_orpha = ['166024', '371', '166282','45']
    for orpha in list_orpha:
        print("for orpha: {}, got name: {}".format(orpha, map_orpha.get(orpha)))

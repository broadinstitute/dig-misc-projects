
# imports

# constants
DEBUG = False

# methods
def load_gene_disease_mapping(file_path):
    gene_dict = {}
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
    return gene_dict

if __name__ == "__main__":
    # instantiate
    map_genes = {}
    file_genes = "/Users/mduby/Data/Broad/Hackathon25/Data/orphanet_genes.txt"

    # load the file
    map_genes = load_gene_disease_mapping(file_path=file_genes)

    # test
    list_gene = ['NFIA', 'BMP2', 'L2HGDH', 'PPARG']
    for gene in list_gene:
        list_disease = map_genes.get(gene, {})
        print("got {} for gene: {}".format(list_disease, gene))





# imports
import json
import pandas as pd
import torch
from torch_geometric.data import HeteroData
import dcc_utils as dutils


# constants
logger = dutils.get_logger(__name__)
DEBUG=True

# classes
class HeteroNetworkDataset:
    """
    Loads a heterogeneous graph from CSV files, according to a JSON config.

    Now assumes each node CSV has exactly one column:
      - 'id' (string or integer), no additional feature columns.

    Edge CSVs must be in the format:
        source_id,target_id,{'weight': <float>}
    """

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.node_files = self.config.get('node_files', {})
        self.edge_files = self.config.get('edge_files', {})

        self.data = HeteroData()
        # id_mapping[node_type] = { original_id: integer_index, ... }
        self.id_mapping = {}

    def load_data(self) -> HeteroData:
        # 1) Load all node types (only 'id' column)
        for ntype, filepath in self.node_files.items():
            # log
            logger.info("reading node file: {}".format(filepath))

            df = pd.read_csv(filepath, dtype={'id': str})
            if 'id' not in df.columns:
                raise ValueError(f"Node file for '{ntype}' must contain an 'id' column.")
            df = df[['id']]  # drop any extras

            ids = df['id'].tolist()
            num_nodes = len(ids)

            # debug
            if DEBUG:
                print("id list: {}".format(ids))

            self.id_mapping[ntype] = {orig_id: idx for idx, orig_id in enumerate(ids)}
            self.data[ntype].num_nodes = num_nodes

        # 2) Load all edge types (extract only 'weight')
        for rel, info in self.edge_files.items():
            src_type = info['src']
            dst_type = info['dst']
            path     = info['path']

            # log
            logger.info("reading edge file: {}".format(path))

            if src_type not in self.node_files or dst_type not in self.node_files:
                raise ValueError(f"Edge '{rel}' references unknown node types '{src_type}' or '{dst_type}'.")

            # Read CSV with no header; columns: source, target, props
            df = pd.read_csv(
                path,
                header=None,
                names=['source', 'target', 'props'],
                dtype={'source': str, 'target': str}
            )

            # Map string-IDs to integer indices
            src_mapped = df['source'].map(self.id_mapping[src_type])
            dst_mapped = df['target'].map(self.id_mapping[dst_type])

            # --- filter out edges with missing source or target mapping ---
            mask = src_mapped.notnull() & dst_mapped.notnull()
            df         = df[mask]
            src_mapped = src_mapped[mask]
            dst_mapped = dst_mapped[mask]
            # ----------------------------------------------------------------

            src_indices = src_mapped.astype(int).tolist()
            dst_indices = dst_mapped.astype(int).tolist()
            edge_index = torch.tensor([src_indices, dst_indices], dtype=torch.long)
            self.data[(src_type, rel, dst_type)].edge_index = edge_index

            # Parse 'props' to extract only the 'weight' value
            weight_list = []
            for s in df['props']:
                pdict = eval(s)  # or ast.literal_eval(s)
                weight_list.append(float(pdict.get('weight', 0.0)))

            edge_weight_tensor = torch.tensor(weight_list, dtype=torch.float).unsqueeze(1)
            self.data[(src_type, rel, dst_type)].edge_attr = edge_weight_tensor

        return self.data

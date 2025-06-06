import json
import pandas as pd
import torch
import ast
from torch_geometric.data import HeteroData

class HeteroNetworkDataset:
    """
    Loads a heterogeneous graph from CSV files, according to a JSON config.

    Edge CSVs in this format must have three comma-separated fields:
      - source (string ID)
      - target (string ID)
      - a Python-dict literal containing at least {'weight': <float>}

    Example edge CSV rows:
      828167,608085,{'weight': 0.04437}
      860492,606920,{'weight': 0.0287}
      819321,607168,{'weight': 0.2938}
    """

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.node_files = self.config.get('node_files', {})
        self.edge_files = self.config.get('edge_files', {})

        self.data = HeteroData()
        self.id_mapping = {}

    def load_data(self) -> HeteroData:
        # 1) Load node types
        for ntype, filepath in self.node_files.items():
            df = pd.read_csv(filepath)
            if 'id' not in df.columns:
                raise ValueError(f"Node file for '{ntype}' must contain an 'id' column.")
            ids = df['id'].tolist()
            num_nodes = len(ids)

            self.id_mapping[ntype] = {orig_id: idx for idx, orig_id in enumerate(ids)}
            self.data[ntype].num_nodes = num_nodes

            feature_cols = [c for c in df.columns if c != 'id']
            if feature_cols:
                feats = torch.tensor(df[feature_cols].values, dtype=torch.float)
                if feats.shape[0] != num_nodes:
                    raise ValueError(f"Mismatch in number of rows vs. num_nodes for '{ntype}'.")
                self.data[ntype].x = feats

        # 2) Load edge types (only extracting 'weight' from the dict)
        for rel, info in self.edge_files.items():
            src_type = info['src']
            dst_type = info['dst']
            path = info['path']

            if src_type not in self.node_files or dst_type not in self.node_files:
                raise ValueError(f"Edge '{rel}' references unknown node types '{src_type}' or '{dst_type}'.")

            # Read CSV with no header; columns: source, target, props
            df = pd.read_csv(path, header=None, names=['source', 'target', 'props'])

            src_indices = df['source'].map(self.id_mapping[src_type]).tolist()
            dst_indices = df['target'].map(self.id_mapping[dst_type]).tolist()

            edge_index = torch.tensor([src_indices, dst_indices], dtype=torch.long)
            self.data[(src_type, rel, dst_type)].edge_index = edge_index

            # Parse and extract only 'weight'
            weight_list = []
            for s in df['props']:
                pdict = ast.literal_eval(s)
                if 'weight' not in pdict:
                    raise ValueError(f"Missing 'weight' key in props: {s}")
                weight_list.append(float(pdict['weight']))

            edge_weight_tensor = torch.tensor(weight_list, dtype=torch.float).unsqueeze(1)
            self.data[(src_type, rel, dst_type)].edge_attr = edge_weight_tensor

        return self.data

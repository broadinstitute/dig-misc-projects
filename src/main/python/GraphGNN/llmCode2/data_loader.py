
import json
import pandas as pd
import torch
from torch_geometric.data import HeteroData

class HeteroNetworkDataset:
    """
    Loads a heterogeneous graph from CSV files, according to a JSON config.

    Config format (config.json):
    {
      "node_files": {
        "<node_type>": "<path_to_csv>",
        ...
      },
      "edge_files": {
        "<relation_name>": {
          "src": "<src_node_type>",
          "dst": "<dst_node_type>",
          "path": "<path_to_edge_csv>"
        },
        ...
      }
      // (other keys are ignored by this loader)
    }

    Node CSVs must have at least an 'id' column. Any other columns are treated as features.
    Edge CSVs must have 'source' and 'target' columns (containing node‐IDs). Any additional columns
    are loaded into an edge_attr tensor.
    """

    def __init__(self, config_path: str):
        # Load JSON config
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.node_files = self.config.get('node_files', {})
        self.edge_files = self.config.get('edge_files', {})

        # Prepare containers
        self.data = HeteroData()
        # id_mapping[node_type] = { original_id_string: integer_index, ... }
        self.id_mapping = {}

    def load_data(self) -> HeteroData:
        # 1) Load all node types
        for ntype, filepath in self.node_files.items():
            df = pd.read_csv(filepath)
            if 'id' not in df.columns:
                raise ValueError(f"Node file for '{ntype}' must contain an 'id' column.")
            ids = df['id'].tolist()
            num_nodes = len(ids)

            # Build mapping from original ID → integer index [0 .. num_nodes-1]
            self.id_mapping[ntype] = {orig_id: idx for idx, orig_id in enumerate(ids)}

            # Inform PyG how many nodes exist of this type (no x tensor yet)
            self.data[ntype].num_nodes = num_nodes

            # If there are feature columns beyond 'id', load them into data[ntype].x
            feature_cols = [c for c in df.columns if c != 'id']
            if feature_cols:
                feats = torch.tensor(df[feature_cols].values, dtype=torch.float)
                if feats.shape[0] != num_nodes:
                    raise ValueError(f"Mismatch in number of rows vs. num_nodes for '{ntype}'.")
                self.data[ntype].x = feats

        # 2) Load all edge types
        for rel, info in self.edge_files.items():
            src_type = info['src']
            dst_type = info['dst']
            path = info['path']

            if src_type not in self.node_files or dst_type not in self.node_files:
                raise ValueError(f"Edge '{rel}' references unknown node types '{src_type}' or '{dst_type}'.")

            df = pd.read_csv(path)
            if 'source' not in df.columns or 'target' not in df.columns:
                raise ValueError(f"Edge file '{path}' must contain 'source' and 'target' columns.")

            # Map IDs → indices
            src_indices = df['source'].map(self.id_mapping[src_type]).tolist()
            dst_indices = df['target'].map(self.id_mapping[dst_type]).tolist()

            edge_index = torch.tensor([src_indices, dst_indices], dtype=torch.long)
            self.data[(src_type, rel, dst_type)].edge_index = edge_index

            # If there are any extra columns (e.g., 'weight', 'combined', 'beta_uncorrected'), load them
            attr_cols = [c for c in df.columns if c not in ['source', 'target']]
            if attr_cols:
                attr_tensor = torch.tensor(df[attr_cols].values, dtype=torch.float)
                if attr_tensor.shape[0] != edge_index.size(1):
                    raise ValueError(f"Number of edge attributes does not match #edges in '{rel}'.")
                self.data[(src_type, rel, dst_type)].edge_attr = attr_tensor

        return self.data



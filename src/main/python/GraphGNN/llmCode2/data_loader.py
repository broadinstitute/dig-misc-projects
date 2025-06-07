# imports
import json
import pandas as pd
import torch
from torch_geometric.data import HeteroData
import dcc_utils as dutils

# constants
logger = dutils.get_logger(__name__)
DEBUG = True

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

    def load_data(self, key_id='neo4j_id') -> HeteroData:
        # 1) Load all node types (only 'id' column)
        for ntype, filepath in self.node_files.items():
            logger.info(f"reading node file: {filepath}")

            df = pd.read_csv(filepath, dtype={key_id: int})
            if key_id not in df.columns:
                raise ValueError(f"Node file for '{ntype}' must contain an 'id' column.")
            df = df[[key_id]]

            ids = df[key_id].tolist()
            self.id_mapping[ntype] = {orig_id: idx for idx, orig_id in enumerate(ids)}
            self.data[ntype].num_nodes = len(ids)

            if DEBUG:
                print(f"[{ntype}] loaded {len(ids)} nodes")

        # 2) Load all edge types (extract only 'weight')
        for rel, info in self.edge_files.items():
            src_type = info['src']
            dst_type = info['dst']
            path     = info['path']

            logger.info(f"reading edge file: {path}")

            # read all as strings, skip blank lines
            df = pd.read_csv(
                path,
                header=None,
                names=['source', 'target', 'props'],
                dtype={'source': str, 'target': str, 'props': str},
                skip_blank_lines=True
            )

            # coerce non-numeric to NaN and drop
            df['source'] = pd.to_numeric(df['source'], errors='coerce')
            df['target'] = pd.to_numeric(df['target'], errors='coerce')
            df = df[df['source'].notna() & df['target'].notna()]

            # safe cast to int
            src_ids = df['source'].astype(int)
            dst_ids = df['target'].astype(int)

            # map to integer node indices
            src_mapped = src_ids.map(self.id_mapping[src_type])
            dst_mapped = dst_ids.map(self.id_mapping[dst_type])

            # keep only mapped edges
            mask = src_mapped.notnull() & dst_mapped.notnull()
            df         = df[mask]
            src_mapped = src_mapped[mask].astype(int)
            dst_mapped = dst_mapped[mask].astype(int)

            # build edge_index
            edge_index = torch.tensor(
                [src_mapped.tolist(), dst_mapped.tolist()],
                dtype=torch.long
            )
            self.data[(src_type, rel, dst_type)].edge_index = edge_index

            # extract weights
            weights = []
            for s in df['props']:
                try:
                    d = eval(s)
                    weights.append(float(d.get('weight', 0.0)))
                except Exception:
                    weights.append(0.0)

            self.data[(src_type, rel, dst_type)].edge_attr = \
                torch.tensor(weights, dtype=torch.float).unsqueeze(1)

            if DEBUG:
                print(f"[{src_type}—{rel}→{dst_type}] loaded {edge_index.size(1)} edges")

        if DEBUG:
            self.print_data_stats()

        return self.data

    def print_data_stats(self):
        """
        Print the number of nodes per node‐type and the number of edges per
        (src, rel, dst) edge‐type in self.data.
        """
        node_types, edge_types = self.data.metadata()

        print("=== Graph Statistics ===")
        for ntype in node_types:
            print(f"  • Node type '{ntype}': {self.data[ntype].num_nodes} nodes")

        for (src, rel, dst) in edge_types:
            cnt = self.data[(src, rel, dst)].edge_index.size(1)
            print(f"  • Edge type '{src}'—[{rel}]→'{dst}': {cnt} edges")

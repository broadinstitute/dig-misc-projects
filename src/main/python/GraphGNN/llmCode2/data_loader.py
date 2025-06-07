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
        Print counts and a small sample (first 10) of each node type and edge type, including edge weights.
        """
        node_types, edge_types = self.data.metadata()

        print("=== Graph Statistics ===")
        # Nodes
        for ntype in node_types:
            count = self.data[ntype].num_nodes
            print(f"  • Node type '{ntype}': {count} nodes")

            rev_map = {idx: orig for orig, idx in self.id_mapping[ntype].items()}
            sample_ids = [rev_map[i] for i in range(min(10, count))]
            print(f"    sample node IDs: {sample_ids}")

        # Edges
        for (src, rel, dst) in edge_types:
            edge_index = self.data[(src, rel, dst)].edge_index
            edge_attr = self.data[(src, rel, dst)].edge_attr
            num_edges = edge_index.size(1)
            print(f"  • Edge type '{src}'—[{rel}]→'{dst}': {num_edges} edges")

            # build reverse maps for original IDs
            rev_src = {idx: orig for orig, idx in self.id_mapping[src].items()}
            rev_dst = {idx: orig for orig, idx in self.id_mapping[dst].items()}

            # sample first 10 edges and their weights
            pairs_idx = list(
                zip(edge_index[0].tolist(), edge_index[1].tolist())
            )[:10]
            weights = edge_attr.squeeze(1).tolist()[:10]
            sample_triples = [
                (rev_src[s], rev_dst[d], w)
                for (s, d), w in zip(pairs_idx, weights)
            ]
            print(f"    sample edges (src, dst, weight): {sample_triples}")

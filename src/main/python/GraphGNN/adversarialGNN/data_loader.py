# imports
import json
import pandas as pd
import torch
from torch_geometric.data import HeteroData
import dcc_utils as dutils

# constants
debug = True
logger = dutils.get_logger(__name__)

class HeteroNetworkDataset:
    """
    Loads a heterogeneous graph from CSV files, according to a JSON config.

    Node CSVs must contain an 'id' column (string or integer).
    Edge CSVs must contain source,target,props with a 'weight' entry.
    Confounder CSVs (optional) must contain the same 'id' plus one or more metadata columns.

    On load_data(), this:
      1) Reads nodes and edges into HeteroData
      2) Loads per-node confounders (if provided) and always computes node degree
      3) Exposes data.confounders: a dict of [num_nodes × conf_dim] tensors
    """

    # def __init__(self, config_path: str, key_id: str = 'id'):
    def __init__(self, config_path: str, key_id: str = 'neo4j_id'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.node_files       = self.config.get('node_files', {})
        self.edge_files       = self.config.get('edge_files', {})
        # optional per-node confounder metadata
        self.confounder_files = self.config.get('confounder_files', {})

        self.key_id     = key_id
        self.id_mapping = {}          # original_id → integer index
        self.data       = HeteroData()

    def load_data(self, load_edges: bool = True) -> HeteroData:
        # 1) Load all node types
        for ntype, path in self.node_files.items():
            logger.info(f"Loading nodes for '{ntype}' from {path}")
            df = pd.read_csv(path, dtype={self.key_id: int})
            if self.key_id not in df.columns:
                raise ValueError(f"Node file '{ntype}' must contain column '{self.key_id}'")

            ids = df[self.key_id].tolist()
            self.id_mapping[ntype] = {orig: idx for idx, orig in enumerate(ids)}
            self.data[ntype].num_nodes = len(ids)
            if debug:
                logger.info(f"  • {ntype}: {len(ids)} nodes loaded")

        # 2) Load all edge types
        if load_edges:
            for rel, info in self.edge_files.items():
                src, dst = info['src'], info['dst']
                path      = info['path']
                logger.info(f"Loading edges '{src}–{rel}→{dst}' from {path}")

                df = pd.read_csv(
                    path,
                    header=None,
                    names=['source','target','props'],
                    dtype={'source':str,'target':str,'props':str},
                    skip_blank_lines=True
                )
                # coerce to int, drop invalid
                df['source'] = pd.to_numeric(df['source'], errors='coerce')
                df['target'] = pd.to_numeric(df['target'], errors='coerce')
                df = df.dropna(subset=['source','target'])
                df['source'] = df['source'].astype(int)
                df['target'] = df['target'].astype(int)

                src_idx = df['source'].map(self.id_mapping[src])
                dst_idx = df['target'].map(self.id_mapping[dst])
                mask    = src_idx.notnull() & dst_idx.notnull()
                src_idx = src_idx[mask].astype(int)
                dst_idx = dst_idx[mask].astype(int)
                df       = df[mask]

                edge_index = torch.tensor([src_idx.tolist(), dst_idx.tolist()], dtype=torch.long)
                weights    = []
                for s in df['props']:
                    try:
                        weights.append(float(eval(s).get('weight',0.0)))
                    except:
                        weights.append(0.0)
                edge_attr = torch.tensor(weights, dtype=torch.float).unsqueeze(1)

                # forward edge
                self.data[(src, rel, dst)].edge_index = edge_index
                self.data[(src, rel, dst)].edge_attr  = edge_attr
                # reverse edge for undirected
                rev_rel = rel + '_REV'
                self.data[(dst, rev_rel, src)].edge_index = edge_index.flip(0)
                self.data[(dst, rev_rel, src)].edge_attr  = edge_attr.clone()

                if debug:
                    logger.info(f"  • {src}–{rel}→{dst}: {edge_index.size(1)} edges")

        # 3) Build confounders dict (load metadata + compute degree)
        self.data.confounders = {}
        node_types, edge_types = self.data.metadata()

        for ntype in node_types:
            N = self.data[ntype].num_nodes
            # start with zeros for each confounder + degree
            # load external confounders if available
            if ntype in self.confounder_files:
                dfc = pd.read_csv(self.confounder_files[ntype], dtype={self.key_id:int})
                if self.key_id not in dfc:
                    raise ValueError(f"Confounder file for '{ntype}' needs column '{self.key_id}'")
                conf_cols = [c for c in dfc.columns if c != self.key_id]
            else:
                conf_cols = []

            conf_dim = len(conf_cols) + 1  # +1 for degree
            tensor   = torch.zeros((N, conf_dim), dtype=torch.float)

            # fill external confounders
            if conf_cols:
                for _, row in dfc.iterrows():
                    orig = row[self.key_id]
                    idx  = self.id_mapping[ntype].get(orig)
                    if idx is not None:
                        vals = [row[c] for c in conf_cols]
                        tensor[idx, :len(vals)] = torch.tensor(vals, dtype=torch.float)

            # compute degree over all edges
            deg = torch.zeros(N, dtype=torch.float)
            for (s, rel, d) in edge_types:
                eidx = self.data[(s, rel, d)].edge_index
                if s == ntype:
                    deg.scatter_add_(0, eidx[0], torch.ones(eidx.size(1)))
                if d == ntype:
                    deg.scatter_add_(0, eidx[1], torch.ones(eidx.size(1)))

            # 1) log1p‐transform to tame huge counts
            deg = torch.log1p(deg)

            # 2) z-score: mean=0, std=1 (clamp σ to avoid div-zero)
            mu, sigma = deg.mean(), deg.std().clamp(min=1e-6)
            deg = (deg - mu) / sigma

            if True:
                logger.info(
                    f"  • {ntype} deg → μ={deg.mean():.3f}, σ={deg.std():.3f}, "
                    f"min={deg.min():.3f}, max={deg.max():.3f}"
                )            

            # 3) write the fully normalized degree back
            tensor[:, -1] = deg
            # tensor[:, -1] = deg

            self.data.confounders[ntype] = tensor
            if debug:
                logger.info(f"  • {ntype} confounders: shape={tensor.shape}")

        if debug:
            self.print_data_stats()

        return self.data

    def print_data_stats(self):
        node_types, edge_types = self.data.metadata()
        logger.info("=== Graph Statistics ===")
        # nodes
        for ntype in node_types:
            cnt = self.data[ntype].num_nodes
            logger.info(f"  • Node '{ntype}': {cnt} nodes")
            sample = list(self.id_mapping[ntype].keys())[:10]
            logger.info(f"    sample IDs: {sample}")
        # edges
        for (s, rel, d) in edge_types:
            ei = self.data[(s, rel, d)].edge_index
            ea = self.data[(s, rel, d)].edge_attr
            logger.info(f"  • Edge '{s}–{rel}→{d}': {ei.size(1)} edges")
        # confounders
        for ntype, tensor in self.data.confounders.items():
            logger.info(f"  • Confounders for '{ntype}': shape={tuple(tensor.shape)}")
            

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)
    device = torch.device(config.get('device', 'cpu'))

    # 2) Load data
    dataset = HeteroNetworkDataset('config.json')
    data = dataset.load_data().to(device)

    # print the dataset mappings
    logger.info("got mappings type: {}".format(type(dataset.id_mapping)))
    for key, value in dataset.id_mapping.items():
        logger.info("got key: {} and value of type: {} and length: {}".format(key, type(value), len(value)))
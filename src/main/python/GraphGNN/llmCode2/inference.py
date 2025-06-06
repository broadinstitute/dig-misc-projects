
import json
import torch
from data_loader import HeteroNetworkDataset
from model import HeteroGNN

@torch.no_grad()
def load_model_and_predict(edge_queries):
    """
    Loads a saved HeteroGNN and returns link‐prediction scores for specified edges.

    Args:
      edge_queries: list of tuples, each:
        (src_type, relation_name, dst_type, src_id_string, dst_id_string)

    Returns:
      dict mapping (src_id, dst_id, relation) → probability ∈ [0,1].
    """
    # 1) Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    device = torch.device(config.get('device', 'cpu'))

    # 2) Load data (to get node mappings & graph structure)
    dataset = HeteroNetworkDataset('config.json')
    data = dataset.load_data()
    data = data.to(device)

    # 3) Extract metadata & num_nodes
    metadata = data.metadata()
    node_types, edge_types = metadata
    num_nodes_dict = {ntype: data[ntype].num_nodes for ntype in node_types}

    # 4) Build model & load weights
    hidden_channels = config['model_params']['hidden_channels']
    model = HeteroGNN(metadata, num_nodes_dict, hidden_channels).to(device)
    model.load_state_dict(torch.load(config['model_path'], map_location=device))
    model.eval()

    # 5) Compute node embeddings once
    z_dict = model(data.x_dict, data.edge_index_dict)

    results = {}
    for (src_type, rel, dst_type, src_id, dst_id) in edge_queries:
        # Map the user‐provided IDs into indices
        if src_type not in dataset.id_mapping or dst_type not in dataset.id_mapping:
            raise ValueError(f"Unknown node type in query: {src_type} or {dst_type}")

        if src_id not in dataset.id_mapping[src_type] or dst_id not in dataset.id_mapping[dst_type]:
            raise ValueError(f"ID not found for '{src_type}': {src_id} or for '{dst_type}': {dst_id}")

        src_idx = dataset.id_mapping[src_type][src_id]
        dst_idx = dataset.id_mapping[dst_type][dst_id]

        edge_index = torch.tensor([[src_idx], [dst_idx]], dtype=torch.long, device=device)
        # raw logit
        score = model.decode(z_dict, edge_index, src_type, dst_type)
        prob = torch.sigmoid(score).item()

        results[(src_id, dst_id, rel)] = prob

    return results

if __name__ == '__main__':
    # Example usage: replace with your own (src_type, rel, dst_type, src_id, dst_id)
    example_queries = [
        ('factor', 'FACTOR_GENE', 'gene', 'F123', 'G456'),
        ('trait', 'TRAIT_GENE', 'gene', 'T789', 'G012'),
    ]

    preds = load_model_and_predict(example_queries)
    for (src_id, dst_id, rel), p in preds.items():
        print(f"Relation ({rel}) between {src_id} → {dst_id}: probability = {p:.4f}")


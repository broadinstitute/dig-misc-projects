import json
import torch
import torch.nn.functional as F
from torch.optim import Adam
from torch_geometric.utils import negative_sampling
from data_loader import HeteroNetworkDataset
from model import HeteroGNN

def train():
    # 1) Load the JSON config
    with open('config.json', 'r') as f:
        config = json.load(f)

    device = torch.device(config.get('device', 'cpu'))

    # 2) Load data
    dataset = HeteroNetworkDataset('config.json')
    data = dataset.load_data()
    data = data.to(device)

    # 3) Extract metadata and num_nodes_dict
    metadata = data.metadata()  # (node_types_list, edge_types_list)
    node_types, edge_types = metadata
    num_nodes_dict = {ntype: data[ntype].num_nodes for ntype in node_types}

    # 4) Build model
    hidden_channels = config['model_params']['hidden_channels']
    model = HeteroGNN(metadata, num_nodes_dict, hidden_channels).to(device)

    lr = config['training_params']['learning_rate']
    wd = config['training_params']['weight_decay']
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=wd)

    epochs = config['training_params']['epochs']

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        # 5) Forward pass → get node embeddings
        z_dict = model(data.x_dict, data.edge_index_dict)

        # 6) For each relation, compute link‐prediction loss
        total_loss = torch.zeros(1, device=device)
        for edge_type in data.edge_index_dict.keys():
            src_type, rel, dst_type = edge_type
            edge_index = data[edge_type].edge_index  # [2, num_pos_edges]

            # Positive scores (logits)
            pos_scores = model.decode(z_dict, edge_index, src_type, dst_type)
            pos_labels = torch.ones(pos_scores.size(0), device=device)

            # Negative sampling: generate equal # of negative edges
            num_src = data[src_type].num_nodes
            num_dst = data[dst_type].num_nodes
            neg_edge_index = negative_sampling(
                edge_index,
                num_nodes=(num_src, num_dst),
                num_neg_samples=edge_index.size(1),
                method='sparse'  # default
            )
            neg_scores = model.decode(z_dict, neg_edge_index, src_type, dst_type)
            neg_labels = torch.zeros(neg_scores.size(0), device=device)

            # Combine positives & negatives
            scores = torch.cat([pos_scores, neg_scores], dim=0)
            labels = torch.cat([pos_labels, neg_labels], dim=0)

            # Binary cross‐entropy w/ logits
            loss = F.binary_cross_entropy_with_logits(scores, labels)
            total_loss += loss

        total_loss.backward()
        optimizer.step()

        print(f'Epoch {epoch:03d} | Loss: {total_loss.item():.4f}')

    # 7) Save trained model state_dict
    model_path = config['model_path']
    torch.save(model.state_dict(), model_path)
    print(f'\nTraining complete. Model saved to: {model_path}\n')

if __name__ == '__main__':
    train()



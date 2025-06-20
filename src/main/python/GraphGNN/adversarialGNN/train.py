import json
import torch
import torch.nn.functional as F
from torch.optim import Adam
from data_loader import HeteroNetworkDataset
# from model import HeteroGNN
from model import HeteroAdversarialGNN
import dcc_utils as dutils

# constants
logger = dutils.get_logger(__name__)
DEBUG = True

def train():
    # 1) Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    device = torch.device(config.get('device', 'cpu'))

    # 2) Load data
    dataset = HeteroNetworkDataset('config.json')
    data = dataset.load_data().to(device)

    # 3) Extract metadata and node counts
    metadata = data.metadata()  # (node_types_list, edge_types_list)
    node_types, edge_types = metadata
    num_nodes_dict = {ntype: data[ntype].num_nodes for ntype in node_types}

    # 4) Build model
    hidden_channels = config['model_params']['hidden_channels']
    confounder_dims = config['model_params']['confounder_dims']
    adv_lambda      = config['model_params'].get('adv_lambda', 0.1)
    # model = HeteroGNN(metadata, num_nodes_dict, hidden_channels).to(device)
    model = HeteroAdversarialGNN(metadata=metadata, num_nodes_dict=num_nodes_dict, hidden_channels=hidden_channels, 
                                 confounder_dims=confounder_dims, adv_lambda=adv_lambda).to(device)

    lr = config['training_params']['learning_rate']
    wd = config['training_params']['weight_decay']
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=wd)
    epochs = config['training_params']['epochs']

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        # 5) Forward pass: get node embeddings
        # 5) Forward pass: get embeddings *and* adversarial predictions
        # z_dict = model(data.edge_index_dict)
        z_dict, adv_preds = model(data.edge_index_dict)

        # 6) Compute link‐prediction loss for each relation type
        total_loss = torch.zeros(1, device=device)
        for edge_type, edge_index in data.edge_index_dict.items():
            src_type, rel, dst_type = edge_type
            num_src = data[src_type].num_nodes
            num_dst = data[dst_type].num_nodes

            # Positive scores & labels
            pos_scores = model.decode(z_dict, edge_index, src_type, dst_type)
            pos_labels = torch.ones(pos_scores.size(0), device=device)

            # ---- pure‐PyTorch negative sampling ----
            # Draw as many random (src, dst) pairs as there are positives.
            # Note: this may occasionally sample a real edge as "negative," 
            # but in large graphs the chance is low.
            num_pos = edge_index.size(1)
            neg_src = torch.randint(0, num_src, (num_pos,), device=device)
            neg_dst = torch.randint(0, num_dst, (num_pos,), device=device)
            neg_edge_index = torch.stack([neg_src, neg_dst], dim=0)
            # ---------------------------------------

            neg_scores = model.decode(z_dict, neg_edge_index, src_type, dst_type)
            neg_labels = torch.zeros(neg_scores.size(0), device=device)

            # Combine and compute BCE loss
            scores = torch.cat([pos_scores, neg_scores], dim=0)
            labels = torch.cat([pos_labels, neg_labels], dim=0)
            total_loss += F.binary_cross_entropy_with_logits(scores, labels)

        # 6b) adversarial nuisance‐regression loss
        L_adv = torch.zeros(1, device=device)
        for ntype, pred in adv_preds.items():
            # assume `data` carries a tensor of true confounders for this node‐type
            # e.g. data.confounders[ntype] is of shape [num_nodes, confounder_dims[ntype]]
            target = data.confounders[ntype].to(device)
            L_adv += F.mse_loss(pred, target)

        # 6c) combine
        total_loss = total_loss + adv_lambda * L_adv

        total_loss.backward()
        optimizer.step()

        # print(f"Epoch {epoch:03d} | Loss: {total_loss.item():.4f}")
        logger.info(f"Epoch {epoch:03d} | Loss: {total_loss.item():.4f}")

    # 7) Save the trained model
    torch.save(model.state_dict(), config['model_path'])
    # print(f"\nTraining complete. Model saved to: {config['model_path']}\n")
    logger.info(f"\nTraining complete. Model saved to: {config['model_path']}\n")

if __name__ == '__main__':
    train()

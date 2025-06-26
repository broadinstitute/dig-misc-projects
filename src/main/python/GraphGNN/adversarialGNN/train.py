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
    model = HeteroAdversarialGNN(
        metadata=metadata,
        num_nodes_dict=num_nodes_dict,
        hidden_channels=hidden_channels,
        confounder_dims=confounder_dims,
        adv_lambda=adv_lambda
    ).to(device)

    lr = config['training_params']['learning_rate']
    wd = config['training_params']['weight_decay']
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=wd)
    epochs = config['training_params']['epochs']

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        # 5) Forward pass: get embeddings *and* adversarial preds
        z_dict, adv_preds = model(data.edge_index_dict)

        # 6a) Task: link-prediction loss per relation (mean), then average
        task_losses = []
        for edge_type, edge_index in data.edge_index_dict.items():
            src_type, rel, dst_type = edge_type
            num_src = data[src_type].num_nodes
            num_dst = data[dst_type].num_nodes

            # Positive samples
            pos_scores = model.decode(z_dict, edge_index, src_type, dst_type)
            pos_labels = torch.ones_like(pos_scores)

            # Negative sampling (equal count)
            num_pos = edge_index.size(1)
            neg_src = torch.randint(0, num_src, (num_pos,), device=device)
            neg_dst = torch.randint(0, num_dst, (num_pos,), device=device)
            neg_edge_index = torch.stack([neg_src, neg_dst], dim=0)
            neg_scores = model.decode(z_dict, neg_edge_index, src_type, dst_type)
            neg_labels = torch.zeros_like(neg_scores)

            # BCE with mean reduction
            scores = torch.cat([pos_scores, neg_scores], dim=0)
            labels = torch.cat([pos_labels, neg_labels], dim=0)
            loss_rel = F.binary_cross_entropy_with_logits(scores, labels, reduction='mean')
            task_losses.append(loss_rel)

        # average across all relation‐types
        L_task = torch.stack(task_losses).mean()

        # 6b) Adversarial: MSE per node‐type (mean), then average
        adv_losses = []
        for ntype, pred in adv_preds.items():
            target = data.confounders[ntype].to(device)
            # ensure same shape
            if pred.shape != target.shape:
                pred = pred.view_as(target)
            loss_adv = F.mse_loss(pred, target, reduction='mean')
            adv_losses.append(loss_adv)

        L_adv = F.mse_loss(pred, target, reduction='mean')
        # L_adv = torch.stack(adv_losses).mean()

        # 6c) combine
        total_loss = L_task + adv_lambda * L_adv
        total_loss.backward()
        optimizer.step()

        logger.info(
            f"Epoch {epoch:03d} | "
            f"L_task: {L_task.item():.4f} | "
            f"L_adv: {L_adv.item():.4f} | "
            f"Total: {total_loss.item():.4f}"
        )

    # 7) Save the trained model
    torch.save(model.state_dict(), config['model_path'])
    logger.info(f"\nTraining complete. Model saved to: {config['model_path']}\n")


if __name__ == '__main__':
    train()

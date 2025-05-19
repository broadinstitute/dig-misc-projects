
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from torch_geometric.nn import HeteroConv, GCNConv, SAGEConv, GATConv
from torch_geometric.loader import HGTLoader
from neo4j import GraphDatabase
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class Neo4jExtractor:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def close(self):
        self.driver.close()
        
    def extract_nodes(self, label):
        with self.driver.session() as session:
            result = session.run(f"MATCH (n:{label}) RETURN n")
            nodes = []
            for record in result:
                node = record["n"]
                properties = dict(node.items())
                properties["neo4j_id"] = node.id  # Store Neo4j internal ID
                nodes.append(properties)
            return pd.DataFrame(nodes)
    
    def extract_edges(self, start_label, edge_type, end_label):
        with self.driver.session() as session:
            query = f"""
                MATCH (a:{start_label})-[r:{edge_type}]->(b:{end_label})
                RETURN id(a) as source_id, properties(a) as source_props,
                       id(b) as target_id, properties(b) as target_props,
                       properties(r) as edge_props
            """
            result = session.run(query)
            edges = []
            for record in result:
                edge = {
                    "source_id": record["source_id"],
                    "target_id": record["target_id"],
                    "edge_props": record["edge_props"]
                }
                edges.append(edge)
            return pd.DataFrame(edges)

# Feature extraction and node/edge processing functions
def process_nodes(node_df, feature_cols=None):
    """Process node dataframe to extract features and IDs"""
    if feature_cols is None:
        # If no features specified, use all columns except neo4j_id
        feature_cols = [col for col in node_df.columns if col != 'neo4j_id' and col != 'id']
    
    # Create mapping from Neo4j ID to consecutive index
    node_mapping = {row['neo4j_id']: i for i, row in node_df.iterrows()}
    
    # Extract features
    features = node_df[feature_cols].copy()
    
    # Handle non-numeric columns (e.g., 'label') by one-hot encoding
    for col in features.columns:
        if features[col].dtype == 'object':
            # Simple one-hot encoding
            dummies = pd.get_dummies(features[col], prefix=col)
            features = pd.concat([features.drop(col, axis=1), dummies], axis=1)
    
    # Convert to tensor
    if len(features.columns) == 0:
        # If no features, create dummy feature of ones
        x = torch.ones(len(node_df), 1)
    else:
        x = torch.tensor(features.values, dtype=torch.float)
    
    return x, node_mapping

def process_edges(edge_df, src_mapping, dst_mapping, weight_col=None):
    """Process edge dataframe to create edge index and optional edge features"""
    # Create edge index
    edge_index = torch.tensor([
        [src_mapping[src] for src in edge_df['source_id']],
        [dst_mapping[dst] for dst in edge_df['target_id']]
    ], dtype=torch.long)
    
    # Extract edge features if specified
    if weight_col is not None and weight_col in edge_df['edge_props'].iloc[0]:
        # Extract weight from edge properties
        edge_attr = torch.tensor([props[weight_col] for props in edge_df['edge_props']], 
                                  dtype=torch.float).view(-1, 1)
    else:
        edge_attr = None
    
    return edge_index, edge_attr

class HeteroGNN(torch.nn.Module):
    def __init__(self, hid_dim, out_dim, metadata, device):
        super().__init__()
        
        # First layer of convolutions
        self.conv1 = HeteroConv({
            edge_type: GATConv((-1, -1), hid_dim, add_self_loops=False)
            for edge_type in metadata[1]
        })
        
        # Second layer of convolutions
        self.conv2 = HeteroConv({
            edge_type: GATConv((-1, -1), hid_dim, add_self_loops=False)
            for edge_type in metadata[1]
        })
        
        # Output layers for different node types (if needed)
        self.out_layers = nn.ModuleDict()
        for node_type in metadata[0]:
            self.out_layers[node_type] = nn.Linear(hid_dim, out_dim)
        
        self.device = device
    
    def forward(self, x_dict, edge_index_dict):
        # First convolution layer
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {key: F.relu(x) for key, x in x_dict.items()}
        
        # Second convolution layer
        x_dict = self.conv2(x_dict, edge_index_dict)
        x_dict = {key: F.relu(x) for key, x in x_dict.items()}
        
        # Output projection for each node type
        out_dict = {node_type: self.out_layers[node_type](x) 
                   for node_type, x in x_dict.items()}
        
        return out_dict

def main():
    # Neo4j Connection Parameters
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "your_password"  # Replace with your actual password
    
    # Connect to Neo4j
    extractor = Neo4jExtractor(uri, username, password)
    
    # Define node and edge types based on your schema
    node_types = ['Factor', 'GeneSet', 'Gene', 'Trait']
    edge_types = [
        ('Factor', 'FACTOR_GENE', 'Gene'),
        ('Factor', 'FACTOR_GENE_SET', 'GeneSet'),
        ('Trait', 'TRAIT_FACTOR', 'Factor'),
        ('Trait', 'TRAIT_GENE', 'Gene'),
        ('Trait', 'TRAIT_GENE_SET', 'GeneSet')
    ]
    
    # Extract nodes and edges
    nodes = {}
    node_mappings = {}
    
    # Extract nodes
    for node_type in node_types:
        nodes[node_type] = extractor.extract_nodes(node_type)
        # Create simple node features
        if node_type == 'Factor' or node_type == 'Trait':
            # For nodes with a label property
            nodes[node_type]['feat'], node_mappings[node_type] = process_nodes(
                nodes[node_type], feature_cols=['label']
            )
        else:
            # For nodes without specific properties
            nodes[node_type]['feat'], node_mappings[node_type] = process_nodes(
                nodes[node_type]
            )
    
    # Extract edges
    edges = {}
    for src_type, edge_type, dst_type in edge_types:
        edge_key = (src_type, edge_type, dst_type)
        edges[edge_key] = extractor.extract_edges(src_type, edge_type, dst_type)
    
    # Create HeteroData object
    data = HeteroData()
    
    # Add node features
    for node_type in node_types:
        data[node_type].x = nodes[node_type]['feat']
        
        # Add node labels (for supervised learning, if needed)
        # Here we're creating dummy labels for demonstration
        # In practice, you would use real labels for your task
        data[node_type].y = torch.zeros(len(nodes[node_type]), dtype=torch.long)
    
    # Add edges
    for (src_type, edge_type, dst_type) in edge_types:
        edge_key = (src_type, edge_type, dst_type)
        
        # Get appropriate weight column based on edge type
        if edge_type == 'FACTOR_GENE' or edge_type == 'FACTOR_GENE_SET' or edge_type == 'TRAIT_FACTOR':
            weight_col = 'weight'
        elif edge_type == 'TRAIT_GENE':
            weight_col = 'combined'  # or 'prior', depending on your needs
        elif edge_type == 'TRAIT_GENE_SET':
            weight_col = 'beta'  # or 'beta_uncorrected', depending on your needs
        else:
            weight_col = None
        
        edge_index, edge_attr = process_edges(
            edges[edge_key], 
            node_mappings[src_type], 
            node_mappings[dst_type],
            weight_col
        )
        
        # Add to data object
        data[src_type, edge_type, dst_type].edge_index = edge_index
        if edge_attr is not None:
            data[src_type, edge_type, dst_type].edge_attr = edge_attr
    
    # Split nodes for training/validation/testing
    # For example, let's split the 'Gene' nodes (you can choose any node type)
    target_node_type = 'Gene'
    num_nodes = data[target_node_type].x.size(0)
    
    # Create train/val/test masks
    train_idx, test_idx = train_test_split(
        np.arange(num_nodes), test_size=0.2, random_state=42
    )
    train_idx, val_idx = train_test_split(
        train_idx, test_size=0.25, random_state=42  # 0.25 x 0.8 = 0.2
    )
    
    # Convert to boolean masks
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)
    
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True
    
    data[target_node_type].train_mask = train_mask
    data[target_node_type].val_mask = val_mask
    data[target_node_type].test_mask = test_mask
    
    # Check if CUDA is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Move data to device
    data = data.to(device)
    
    # Model parameters
    hidden_dim = 64
    output_dim = 16  # Or number of classes if doing node classification
    
    # Initialize model
    model = HeteroGNN(
        hid_dim=hidden_dim,
        out_dim=output_dim,
        metadata=data.metadata(),
        device=device
    ).to(device)
    
    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    # Define a task (e.g., node classification, link prediction)
    # Here we'll implement a simple link prediction task
    def train():
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        out_dict = model(data.x_dict, data.edge_index_dict)
        
        # For this example, we'll use a simple reconstruction loss
        # In practice, you'd define a task-specific loss
        loss = 0
        for edge_type in data.edge_types:
            src, rel, dst = edge_type
            
            # Get node embeddings
            src_emb = out_dict[src]
            dst_emb = out_dict[dst]
            
            # Get edge indices
            edge_index = data[edge_type].edge_index
            
            # Sample negative edges
            num_edges = edge_index.size(1)
            
            # Positive edge predictions
            pos_pred = (src_emb[edge_index[0]] * dst_emb[edge_index[1]]).sum(dim=1)
            
            # Random negative edges
            neg_src_idx = torch.randint(0, src_emb.size(0), (num_edges,), device=device)
            neg_dst_idx = torch.randint(0, dst_emb.size(0), (num_edges,), device=device)
            neg_pred = (src_emb[neg_src_idx] * dst_emb[neg_dst_idx]).sum(dim=1)
            
            # BPR loss: -log(sigmoid(pos_pred - neg_pred))
            loss += F.binary_cross_entropy_with_logits(
                pos_pred - neg_pred, 
                torch.ones_like(pos_pred)
            )
        
        loss.backward()
        optimizer.step()
        
        return loss.item()
    
    # Training loop
    for epoch in range(100):
        loss = train()
        if epoch % 10 == 0:
            print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}')
    
    # Example use case: Node embeddings for downstream tasks
    with torch.no_grad():
        out_dict = model(data.x_dict, data.edge_index_dict)
        
        # Now out_dict contains embeddings for each node type
        # You can use these embeddings for various downstream tasks
        
        # For example, get embeddings for all Gene nodes
        gene_embeddings = out_dict['Gene'].detach().cpu().numpy()
        
        print(f"Generated embeddings for {len(gene_embeddings)} Gene nodes")
        
        # Example: Link prediction
        # For demonstration, predicting links between Factor and Gene
        src_type, edge_type, dst_type = 'Factor', 'FACTOR_GENE', 'Gene'
        
        factor_emb = out_dict[src_type]
        gene_emb = out_dict[dst_type]
        
        # Calculate similarity scores for all possible Factor-Gene pairs
        # (in practice, you might want to use batching for large graphs)
        scores = torch.matmul(factor_emb, gene_emb.t())
        
        # Top-k predictions
        k = 5
        top_scores, top_indices = scores.topk(k, dim=1)
        
        print(f"Top {k} Gene predictions for each Factor:")
        for i in range(min(5, len(factor_emb))):
            factor_id = nodes['Factor'].iloc[i]['id']
            predicted_genes = [nodes['Gene'].iloc[j]['id'] for j in top_indices[i]]
            print(f"Factor {factor_id}: {predicted_genes}")
    
    # Close Neo4j connection
    extractor.close()

if __name__ == "__main__":
    main()
    
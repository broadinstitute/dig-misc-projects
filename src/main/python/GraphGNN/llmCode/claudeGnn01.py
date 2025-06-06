

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, GATConv

class HeteroGNN(torch.nn.Module):
    """
    Heterogeneous Graph Neural Network model for processing different node and edge types
    
    Args:
        hid_dim (int): Dimension of hidden layers
        out_dim (int): Dimension of output embeddings
        metadata (tuple): Graph metadata (node_types, edge_types)
        num_layers (int): Number of GNN layers
        dropout (float): Dropout probability
        conv_type (str): Type of graph convolution ('GATConv', 'GCNConv', 'SAGEConv', etc.)
    """
    def __init__(self, hid_dim, out_dim, metadata, num_layers=2, dropout=0.2, conv_type='GATConv'):
        super().__init__()
        
        self.hid_dim = hid_dim
        self.out_dim = out_dim
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Store node and edge types
        self.node_types = metadata[0]
        self.edge_types = metadata[1]
        
        # Create multiple convolution layers
        self.convs = nn.ModuleList()
        
        for i in range(num_layers):
            # For the first layer, input dim is -1 (inferred from data)
            # For subsequent layers, input dim is hid_dim
            
            # Choose the convolution type
            if conv_type == 'GATConv':
                conv_layer = HeteroConv({
                    edge_type: GATConv((-1, -1), hid_dim, add_self_loops=False)
                    for edge_type in self.edge_types
                })
            # Add more convolution types as needed
            # elif conv_type == 'GCNConv':
            #     conv_layer = HeteroConv({
            #         edge_type: GCNConv(-1, hid_dim)
            #         for edge_type in self.edge_types
            #     })
            else:
                raise ValueError(f"Unsupported convolution type: {conv_type}")
                
            self.convs.append(conv_layer)
        
        # Output layers for different node types
        self.out_layers = nn.ModuleDict()
        for node_type in self.node_types:
            self.out_layers[node_type] = nn.Linear(hid_dim, out_dim)
    
    def forward(self, x_dict, edge_index_dict):
        """
        Forward pass
        
        Args:
            x_dict (dict): Dictionary mapping node types to feature matrices
            edge_index_dict (dict): Dictionary mapping edge types to edge indices
            
        Returns:
            dict: Dictionary mapping node types to output embeddings
        """
        # Apply convolution layers with ReLU activations and dropout
        for i in range(self.num_layers):
            x_dict = self.convs[i](x_dict, edge_index_dict)
            
            # Apply ReLU and dropout to all node types
            x_dict = {key: F.relu(x) for key, x in x_dict.items()}
            x_dict = {key: F.dropout(x, p=self.dropout, training=self.training) 
                     for key, x in x_dict.items()}
        
        # Apply output layers
        out_dict = {node_type: self.out_layers[node_type](x) 
                   for node_type, x in x_dict.items()}
        
        return out_dict
    
    def save(self, path):
        """Save the model parameters"""
        torch.save(self.state_dict(), path)
    
    def load(self, path, device=None):
        """Load model parameters from path"""
        if device:
            self.load_state_dict(torch.load(path, map_location=device))
        else:
            self.load_state_dict(torch.load(path))
    
    @staticmethod
    def get_embedding_similarity(src_emb, dst_emb, k=5):
        """
        Calculate similarity between source and destination embeddings
        
        Args:
            src_emb (Tensor): Source node embeddings
            dst_emb (Tensor): Destination node embeddings
            k (int): Number of top predictions
            
        Returns:
            tuple: (scores, indices) of top-k predictions
        """
        # Calculate similarity scores (dot product)
        scores = torch.matmul(src_emb, dst_emb.t())
        
        # Get top-k predictions
        top_scores, top_indices = scores.topk(k, dim=1)
        
        return top_scores, top_indices
    
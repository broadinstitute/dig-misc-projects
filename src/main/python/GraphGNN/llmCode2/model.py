import torch
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, GCNConv

class HeteroGNN(torch.nn.Module):
    """
    A two‐layer heterogeneous GNN using GCNConv on each relation. Each node type has a trainable
    Embedding of size `hidden_channels`. No external node features are used.

    Args:
      metadata: returned from data.metadata(): (node_types_list, edge_types_list)
      num_nodes_dict: dict mapping each node_type → #nodes of that type
      hidden_channels: dimensionality of all embeddings & hidden layers
    """
    def __init__(self, metadata, num_nodes_dict: dict, hidden_channels: int):
        super().__init__()
        node_types, edge_types = metadata
        self.node_types = node_types
        self.edge_types = edge_types
        self.hidden_channels = hidden_channels

        # 1) Embedding layer per node type
        self.embeddings = torch.nn.ModuleDict()
        for ntype in node_types:
            num_nodes = num_nodes_dict[ntype]
            # Each node ID gets a learned embedding of size hidden_channels
            self.embeddings[ntype] = torch.nn.Embedding(num_nodes, hidden_channels)

        # 2) Two HeteroConv layers (using GCNConv for each relation)
        conv_dict_1 = {}
        conv_dict_2 = {}
        for edge_type in edge_types:
            # GCNConv expects input dim = hidden_channels for both src & dst
            conv_dict_1[edge_type] = GCNConv((-1, -1), hidden_channels)
            conv_dict_2[edge_type] = GCNConv((-1, -1), hidden_channels)

        self.conv1 = HeteroConv(conv_dict_1, aggr='sum')
        self.conv2 = HeteroConv(conv_dict_2, aggr='sum')

    def forward(self, edge_index_dict) -> dict:
        """
        Args:
          edge_index_dict: dict mapping (src_type, rel, dst_type) → edge_index tensor.

        Returns:
          z_dict: dict mapping node_type → final node embeddings (size [num_nodes, hidden_channels]).
        """
        # 1) Initialize each node_type’s feature matrix as the full embedding matrix
        z_dict = {}
        for ntype in self.node_types:
            # embeddings[ntype].weight is shape [num_nodes(ntype), hidden_channels]
            z_dict[ntype] = self.embeddings[ntype].weight

        # 2) First HeteroConv + ReLU
        z_dict = self.conv1(z_dict, edge_index_dict)
        for ntype in z_dict:
            z_dict[ntype] = F.relu(z_dict[ntype])

        # 3) Second HeteroConv (no activation on output)
        z_dict = self.conv2(z_dict, edge_index_dict)
        return z_dict

    def decode(self, z_dict: dict, edge_index: torch.Tensor, src_type: str, dst_type: str) -> torch.Tensor:
        """
        Dot‐product decoder for a batch of edges of a single relation.

        Args:
          z_dict: node embeddings dict (from forward)
          edge_index: LongTensor of shape [2, num_edges]
          src_type: source node_type string
          dst_type: destination node_type string

        Returns:
          Tensor of shape [num_edges], each entry = dot(z_src, z_dst).
        """
        src_z = z_dict[src_type]
        dst_z = z_dict[dst_type]
        src_idx, dst_idx = edge_index
        return (src_z[src_idx] * dst_z[dst_idx]).sum(dim=1)

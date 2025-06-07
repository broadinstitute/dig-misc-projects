import torch
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, GCNConv

class HeteroGNN(torch.nn.Module):
    def __init__(self, metadata, num_nodes_dict: dict, hidden_channels: int):
        super().__init__()
        node_types, edge_types = metadata
        self.node_types = node_types
        self.edge_types = edge_types

        # 1) Embedding per node type
        self.embeddings = torch.nn.ModuleDict({
            ntype: torch.nn.Embedding(num_nodes_dict[ntype], hidden_channels)
            for ntype in node_types
        })

        # # 2) Two HeteroConv layers: use fixed in_channels=hidden_channels
        # conv_dict_1 = {
        #     edge_type: GCNConv(hidden_channels, hidden_channels)
        #     for edge_type in edge_types
        # }
        # conv_dict_2 = {
        #     edge_type: GCNConv(hidden_channels, hidden_channels)
        #     for edge_type in edge_types
        # }

        # self.conv1 = HeteroConv(conv_dict_1, aggr='sum')
        # self.conv2 = HeteroConv(conv_dict_2, aggr='sum')

        # 2) Two HeteroConv layers: disable self-loops on each GCNConv
        conv_dict_1 = {
            edge_type: GCNConv(hidden_channels, hidden_channels,
                              add_self_loops=False)
            for edge_type in edge_types
        }
        conv_dict_2 = {
            edge_type: GCNConv(hidden_channels, hidden_channels,
                              add_self_loops=False)
            for edge_type in edge_types
        }

        self.conv1 = HeteroConv(conv_dict_1, aggr='sum')
        self.conv2 = HeteroConv(conv_dict_2, aggr='sum')


    def forward(self, edge_index_dict) -> dict:
        # Initialize from embeddings
        z_dict = {ntype: emb.weight for ntype, emb in self.embeddings.items()}

        z_dict = self.conv1(z_dict, edge_index_dict)
        for ntype in z_dict:
            z_dict[ntype] = F.relu(z_dict[ntype])

        z_dict = self.conv2(z_dict, edge_index_dict)
        return z_dict

    def decode(self, z_dict, edge_index, src_type, dst_type):
        src_z = z_dict[src_type]
        dst_z = z_dict[dst_type]
        src_idx, dst_idx = edge_index
        return (src_z[src_idx] * dst_z[dst_idx]).sum(dim=1)

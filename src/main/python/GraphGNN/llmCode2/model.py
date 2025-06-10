
# imports
import torch
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, SAGEConv
import json
from data_loader import HeteroNetworkDataset
import dcc_utils as dutils

# constants
logger = dutils.get_logger(__name__)
DEBUG = True

# class
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

        # 2) Two HeteroConv layers using SAGEConv (supports bipartite in-out)
        conv_dict_1 = {
            edge_type: SAGEConv((hidden_channels, hidden_channels), hidden_channels)
            for edge_type in edge_types
        }
        conv_dict_2 = {
            edge_type: SAGEConv((hidden_channels, hidden_channels), hidden_channels)
            for edge_type in edge_types
        }

        self.conv1 = HeteroConv(conv_dict_1, aggr='sum')
        self.conv2 = HeteroConv(conv_dict_2, aggr='sum')


    def forward(self, edge_index_dict) -> dict:
        # 1) Start from learned embeddings for every node type
        z_dict = {ntype: emb.weight for ntype, emb in self.embeddings.items()}

        # 2) First round of message‐passing
        h_dict = self.conv1(z_dict, edge_index_dict)
        # Merge updates back into z_dict, applying ReLU—and keep originals for types with no incoming edges
        for ntype in self.node_types:
            if ntype in h_dict and h_dict[ntype] is not None:
                z_dict[ntype] = F.relu(h_dict[ntype])
            # else: leave z_dict[ntype] as the original embedding

        # 3) Second round of message‐passing
        h2_dict = self.conv2(z_dict, edge_index_dict)
        for ntype in self.node_types:
            if ntype in h2_dict and h2_dict[ntype] is not None:
                z_dict[ntype] = h2_dict[ntype]
            # else: leave the previous z_dict[ntype] unchanged

        return z_dict

    def decode(self, z_dict, edge_index, src_type, dst_type):
        src_z = z_dict[src_type]
        dst_z = z_dict[dst_type]
        src_idx, dst_idx = edge_index
        return (src_z[src_idx] * dst_z[dst_idx]).sum(dim=1)


def load_model_and_data(path_model=None):
    with open('config.json', 'r') as f:
        config = json.load(f)
    device = torch.device(config.get('device', 'cpu'))

    # 2) Load data for mappings
    dataset = HeteroNetworkDataset('config.json')
    data = dataset.load_data().to(device)

    # 3) Metadata and node counts
    metadata = data.metadata()
    node_types, edge_types = metadata
    num_nodes_dict = {ntype: data[ntype].num_nodes for ntype in node_types}

    # 4) Build model & load weights
    hidden_channels = config['model_params']['hidden_channels']
    model = HeteroGNN(metadata, num_nodes_dict, hidden_channels).to(device)

    # load model weights
    if not path_model:
        model.load_state_dict(torch.load(config['model_to_load_path'], map_location=device))
    else:
        model.load_state_dict(torch.load(config[path_model], map_location=device))

    # return
    return model, data, dataset


def get_node_embeddings(model, data):
    # initialize
    z_dict = None

    # # load model
    # with open('config.json') as f:
    #     config = json.load(f)
    # device = torch.device(config.get('device','cpu'))

    # dataset = HeteroNetworkDataset('config.json')
    # data    = dataset.load_data().to(device)

    # # 2) Build model & load weights
    # metadata      = data.metadata()
    # num_nodes_dict= {ntype: data[ntype].num_nodes for ntype in metadata[0]}
    # hidden_dim    = config['model_params']['hidden_channels']

    # model = HeteroGNN(metadata, num_nodes_dict, hidden_dim).to(device)
    # model.load_state_dict(torch.load(config['model_path'], map_location=device))
    model.eval()

    # 3) Run one forward pass (this applies both conv layers)
    with torch.no_grad():
        z_dict = model(data.edge_index_dict) 

    # return
    return z_dict


def save_dataset_id_mapping(dataset, log=False):
    '''
    will save the dataset mappings to file
    '''
    # get the config
    config = dutils.load_config()

    # get the dataset id mappings
    id_mapping = dataset.id_mapping

    with open(config.get(dutils.KEY_INFERENCE).get(dutils.KEY_DATA_MAPPING), 'w') as f:
        json.dump(id_mapping, f, indent=2)




if __name__ == "__main__":
    model, data, dataset = load_model_and_data()
    logger.info("got loaded model: {}".format(model))

    node_embeddings = get_node_embeddings(model, data)
    # logger.info("got node embeddings: {}".format(node_embeddings))
    for key, value in node_embeddings.items():
        logger.info("for embedding key: {}, got tensor shape: {}".format(key, value.shape))

    # print("dataset: {}".format(dataset.id_mapping))
    save_dataset_id_mapping(dataset=dataset)
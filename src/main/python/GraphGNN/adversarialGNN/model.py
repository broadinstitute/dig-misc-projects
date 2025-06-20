
# imports
import torch
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, SAGEConv
from torch.autograd import Function
import json
from data_loader import HeteroNetworkDataset
import dcc_utils as dutils

# constants
logger = dutils.get_logger(__name__)
DEBUG = True

# class
# Gradient Reversal Layer
class GradReverse(Function):
    @staticmethod
    def forward(ctx, x, lambda_):
        ctx.lambda_ = lambda_
        return x.view_as(x)
    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.lambda_, None

class HeteroAdversarialGNN(torch.nn.Module):
    def __init__(self, metadata, num_nodes_dict: dict, hidden_channels: int,
                 confounder_dims: dict, adv_lambda: float = 0.1):
        super().__init__()
        node_types, edge_types = metadata
        self.node_types = node_types
        self.edge_types = edge_types
        self.hidden_channels = hidden_channels
        self.adv_lambda = adv_lambda

        # 1) Embedding per node type
        self.embeddings = torch.nn.ModuleDict({
            ntype: torch.nn.Embedding(num_nodes_dict[ntype], hidden_channels)
            for ntype in node_types
        })

        # 2) Two-layer HeteroConv backbone
        conv_dict_1 = { edge: SAGEConv((hidden_channels, hidden_channels), hidden_channels)
                        for edge in edge_types }
        conv_dict_2 = { edge: SAGEConv((hidden_channels, hidden_channels), hidden_channels)
                        for edge in edge_types }

        self.conv1 = HeteroConv(conv_dict_1, aggr='sum')
        self.conv2 = HeteroConv(conv_dict_2, aggr='sum')

        # 3) Adversarial MLPs to predict confounders (nuisance attributes)
        #    One MLP per node type with >0 confounders
        self.mlp_adv = torch.nn.ModuleDict({
            ntype: torch.nn.Sequential(
                torch.nn.Linear(hidden_channels, hidden_channels),
                torch.nn.ReLU(),
                torch.nn.Linear(hidden_channels, confounder_dims[ntype])
            )
            for ntype in node_types if confounder_dims.get(ntype, 0) > 0
        })

    def forward(self, edge_index_dict):
        # 1) Initial embeddings for all node types
        z_dict = {nt: emb.weight for nt, emb in self.embeddings.items()}

        # 2) First conv layer + ReLU
        h_dict = self.conv1(z_dict, edge_index_dict)
        for ntype, h in h_dict.items():
            if h is not None:
                z_dict[ntype] = F.relu(h)

        # 3) Second conv layer (no activation)
        h2_dict = self.conv2(z_dict, edge_index_dict)
        for ntype, h2 in h2_dict.items():
            if h2 is not None:
                z_dict[ntype] = h2

        # 4) Adversarial head: predict confounders with gradient reversal
        adv_preds = {}
        for ntype, mlp in self.mlp_adv.items():
            z = z_dict[ntype]
            # apply gradient reversal
            z_rev = GradReverse.apply(z, self.adv_lambda)
            adv_preds[ntype] = mlp(z_rev)

        return z_dict, adv_preds

    def decode(self, z_dict, edge_index, src_type, dst_type):
        src_z = z_dict[src_type]; dst_z = z_dict[dst_type]
        src_idx, dst_idx = edge_index
        return (src_z[src_idx] * dst_z[dst_idx]).sum(dim=1)


def load_model_and_data(path_model=None):
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    device = torch.device(config.get('device', 'cpu'))

    # Load dataset and move to device
    dataset = HeteroNetworkDataset('config.json')
    data = dataset.load_data().to(device)

    # Metadata and node counts
    metadata = data.metadata()
    node_types, edge_types = metadata
    num_nodes_dict = {nt: data[nt].num_nodes for nt in node_types}

    # Confounder dimensions per node type from config
    confounder_dims = config['model_params']['confounder_dims']
    hidden_channels = config['model_params']['hidden_channels']
    adv_lambda = config['model_params'].get('adv_lambda', 0.1)

    # Build model and load weights
    model = HeteroAdversarialGNN(metadata, num_nodes_dict,
                                 hidden_channels, confounder_dims,
                                 adv_lambda).to(device)
    if not path_model:
        path_model = config['model_to_load_path']
    logger = dutils.get_logger(__name__)
    logger.info(f"Loading model from {path_model}")
    model.load_state_dict(torch.load(path_model, map_location=device))

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


# imports
import os
import numpy as np
import pandas as pd
import torch
from neo4j import GraphDatabase
import pickle


# constants
NEO4J_IP_PORT = 'localhost:7887'
if os.getenv('NEO4J_IP_PORT'):
    NEO4J_IP_PORT = os.getenv('NEO4J_IP_PORT')
NEO4J_URI = "bolt://{}".format(NEO4J_IP_PORT)
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# Define node and edge types based on your schema
NODE_TYPES = ['Factor', 'GeneSet', 'Gene', 'Trait']
EDGE_TYPES = [
    ('Factor', 'FACTOR_GENE', 'Gene'),
    ('Factor', 'FACTOR_GENE_SET', 'GeneSet'),
    ('Trait', 'TRAIT_FACTOR', 'Factor'),
    ('Trait', 'TRAIT_GENE', 'Gene'),
    ('Trait', 'TRAIT_GENE_SET', 'GeneSet')
]


# file constants
DIR_DATA = "/home/javaprog/Data/Broad/PortalAI/Neo4j"
FILE_NODES = ""
FILE_EDGES = ""


# classes
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
        # If no features specified, use all columns except neo4j_id and id
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
    if weight_col is not None and len(edge_df) > 0 and 'edge_props' in edge_df.columns:
        if edge_df['edge_props'].iloc[0] is not None and weight_col in edge_df['edge_props'].iloc[0]:
            # Extract weight from edge properties
            edge_attr = torch.tensor([props.get(weight_col, 0.0) for props in edge_df['edge_props']], 
                                    dtype=torch.float).view(-1, 1)
        else:
            edge_attr = None
    else:
        edge_attr = None
    
    return edge_index, edge_attr

def extract_and_save_data(output_dir, uri=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD):
    """Extract data from Neo4j and save to disk"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Neo4j Connection Parameters
    # uri = "bolt://localhost:7687"
    # username = "neo4j"
    # password = "your_password"  # Replace with your actual password
    
    # Connect to Neo4j
    extractor = Neo4jExtractor(uri, username, password)
    
    
    # Extract nodes and save to disk
    nodes = {}
    node_mappings = {}
    
    for node_type in NODE_TYPES:
        print(f"Extracting {node_type} nodes of size: {len(node_type)}")
        nodes[node_type] = extractor.extract_nodes(node_type)
        
        # Save raw node data
        nodes[node_type].to_csv(os.path.join(output_dir, f"{node_type}_nodes.csv"), index=False)
        
        # # Process node features
        # if node_type == 'Factor' or node_type == 'Trait':
        #     # For nodes with a label property
        #     nodes[node_type]['feat'], node_mappings[node_type] = process_nodes(
        #         nodes[node_type], feature_cols=['label']
        #     )
        # else:
        #     # For nodes without specific properties
        #     nodes[node_type]['feat'], node_mappings[node_type] = process_nodes(
        #         nodes[node_type]
        #     )
        
        # # Save processed node features
        # torch.save(nodes[node_type]['feat'], os.path.join(output_dir, f"{node_type}_features.pt"))
        
        # # Save node mapping
        # with open(os.path.join(output_dir, f"{node_type}_mapping.pkl"), 'wb') as f:
        #     pickle.dump(node_mappings[node_type], f)
    
    # Extract edges and save to disk
    edges = {}
    for src_type, edge_type, dst_type in EDGE_TYPES:
        edge_key = (src_type, edge_type, dst_type)
        print(f"Extracting {edge_type} edges from {src_type} to {dst_type}...")
        
        # Extract edges
        edges[edge_key] = extractor.extract_edges(src_type, edge_type, dst_type)
        print("got list of size: {}".format(len(edges[edge_key])))
                
        # Save raw edge data
        edges[edge_key].to_csv(os.path.join(output_dir, f"{src_type}_{edge_type}_{dst_type}_edges.csv"), index=False)
        
        # # Determine appropriate weight column
        # if edge_type == 'FACTOR_GENE' or edge_type == 'FACTOR_GENE_SET' or edge_type == 'TRAIT_FACTOR':
        #     weight_col = 'weight'
        # elif edge_type == 'TRAIT_GENE':
        #     weight_col = 'combined'  # or 'prior', depending on your needs
        # elif edge_type == 'TRAIT_GENE_SET':
        #     # weight_col = 'beta'  # or 'beta_uncorrected', depending on your needs
        #     weight_col = 'beta_uncorrected'  # or 'beta_uncorrected', depending on your needs
        # else:
        #     weight_col = None
        
        # # Process edges
        # edge_index, edge_attr = process_edges(
        #     edges[edge_key],
        #     node_mappings[src_type],
        #     node_mappings[dst_type],
        #     weight_col
        # )
        
        # # Save processed edge data
        # torch.save(edge_index, os.path.join(output_dir, f"{src_type}_{edge_type}_{dst_type}_edge_index.pt"))
        # if edge_attr is not None:
        #     torch.save(edge_attr, os.path.join(output_dir, f"{src_type}_{edge_type}_{dst_type}_edge_attr.pt"))
    
    # Save metadata about the graph
    metadata = {
        'node_types': NODE_TYPES,
        'edge_types': EDGE_TYPES
    }
    
    with open(os.path.join(output_dir, 'metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f)
    
    # Close Neo4j connection
    extractor.close()
    
    print(f"Data extraction complete. Files saved to {output_dir}")

if __name__ == "__main__":
    extract_and_save_data(output_dir=DIR_DATA)
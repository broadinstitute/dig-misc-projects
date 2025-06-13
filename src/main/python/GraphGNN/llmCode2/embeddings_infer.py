

# imports
import csv
import os
import json
import dcc_utils as dutils
import pandas as pd
from model import load_model_and_data, get_node_embeddings


# constants
logger = dutils.get_logger(__name__)
DEBUG = True


# methods
def parse_node_files():
  """
  Reads CSV files and creates a nested dictionary structure.
  
  Returns:
      dict: Structure like {type: {neo4j_id: id, ...}, ...}
  """
  # load the config
  config = dutils.load_config()
  map_node_files = config.get(dutils.KEY_NODE_FILES)    

  # Initialize result dictionary
  result = {}
  
  # Process each file
  for node_type, file_path in map_node_files.items():
      try:
          # Check if file exists
          if not os.path.exists(file_path):
              print(f"Warning: File {file_path} not found. Skipping {node_type}.")
              continue
          
          # Initialize dictionary for this node type
          result[node_type] = {}
          
          # Read CSV file
          with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
              reader = csv.DictReader(csvfile)
              
              # Process each row
              for row in reader:
                  neo4j_id = row['neo4j_id']
                  node_id = row['id']
                  
                  # Add to result dictionary (neo4j_id -> id mapping)
                  result[node_type][neo4j_id] = node_id
          
          logger.info(f"Successfully processed {file_path}: {len(result[node_type])} entries")
          
      except Exception as e:
          logger.info(f"Error processing {file_path}: {str(e)}")
          continue
  
  return result


def create_tensor_map(map_node_embeddings, map_node_ids, dataset, log=False):
  '''
  will create a map of node embddings
  '''
  # initialize
  map_result = {}

  # loop through the node types
  for node_type, map_id_to_name in map_node_ids.items():
    logger.info("processing node type: {} with sample data: {}".format(node_type, list(map_id_to_name.items())[:5]))

    # get the node embeddings for each element
    for key_id, value_name in map_id_to_name.items():
      # get the index and then the tensor from the embedding
      map_ids = dataset.id_mapping.get(node_type)

      # print("Looking for key: '{}' of type: {}".format(key_id, type(key_id)))
      # print(f"Key exists: {str(key_id) in map_ids}")
      # print(f"Result: {map_ids.get(key_id)}")
      # logger.info("looking for id: '{}' in map: {}".format(key_id, list(map_ids.items())[:5]))
      idx_node = map_ids.get(int(key_id), None)

      if idx_node:
        node_embedding = map_node_embeddings[node_type][idx_node]
        # add to map_result with key as name, value as tensor
        map_result[value_name] = node_embedding

      else:
        logger.info("no index for node type: {} and id: {}".format(node_type, key_id))
          

  # return
  return map_result


def create_tensor_map_by_node_type(map_node_embeddings, map_node_ids, dataset, log=False):
  '''
  will create a map of node embddings
  '''
  # initialize
  map_result = {}

  # loop through the node types
  for node_type, map_id_to_name in map_node_ids.items():
    map_embeddings = {}
    logger.info("processing node type: {} with sample data: {}".format(node_type, list(map_id_to_name.items())[:5]))

    # get the node embeddings for each element
    for key_id, value_name in map_id_to_name.items():
      # get the index and then the tensor from the embedding
      map_ids = dataset.id_mapping.get(node_type)

      # print("Looking for key: '{}' of type: {}".format(key_id, type(key_id)))
      # print(f"Key exists: {str(key_id) in map_ids}")
      # print(f"Result: {map_ids.get(key_id)}")
      # logger.info("looking for id: '{}' in map: {}".format(key_id, list(map_ids.items())[:5]))
      idx_node = map_ids.get(int(key_id), None)

      if idx_node:
        node_embedding = map_node_embeddings[node_type][idx_node]
        # add to map_result with key as name, value as tensor
        map_embeddings[value_name] = node_embedding

      else:
        logger.info("no index for node type: {} and id: {}".format(node_type, key_id))

      # add to final map 
      map_result[node_type] = map_embeddings
          

  # return
  return map_result


def main():
  """
  Main function to demonstrate usage
  """
  # Parse the files
  parsed_data = parse_node_files()
  
  # Display results
  print("\n=== Parsing Results ===")
  for node_type, mappings in parsed_data.items():
      print(f"\n{node_type.upper()} nodes:")
      print(f"  Total entries: {len(mappings)}")
      
      # Show first few entries as examples
      if mappings:
          print("  Sample entries:")
          for i, (neo4j_id, node_id) in enumerate(mappings.items()):
              if i < 3:  # Show first 3 entries
                  print(f"    {neo4j_id} -> {node_id}")
              else:
                  break
          if len(mappings) > 3:
              print(f"    ... and {len(mappings) - 3} more")
  
  # Example of accessing the data
  print("\n=== Usage Example ===")
  if 'gene' in parsed_data and parsed_data['gene']:
      first_neo4j_id = next(iter(parsed_data['gene']))
      gene_id = parsed_data['gene'][first_neo4j_id]
      print(f"Gene with neo4j_id '{first_neo4j_id}' has id '{gene_id}'")
  
  return parsed_data


def save_tensors_to_csv(map_tensor, output_filename='tensor_data.csv'):
    """
    Convert dictionary of PyTorch tensors to pandas DataFrame and save as CSV.
    
    Args:
        tensor_dict: Dictionary where keys are strings and values are PyTorch tensors
        output_filename: Name of the output CSV file
    """
    
    # Convert tensors to numpy arrays and create rows
    rows = []
    
    for key, tensor in map_tensor.items():
        # Convert tensor to numpy array
        if tensor.requires_grad:
            tensor_np = tensor.detach().numpy()
        else:
            tensor_np = tensor.numpy()
        
        # Create row with key as first element, followed by tensor values
        row = [key] + tensor_np.tolist()
        rows.append(row)
    
    # Create column names: 'key' + 'value_0', 'value_1', ..., 'value_63'
    columns = ['key'] + [f'val_{i}' for i in range(64)]
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=columns)
    
    # Save to CSV
    df.to_csv(output_filename, index=False)
    print(f"Data saved to {output_filename}")
    print(f"DataFrame shape: {df.shape}")
    print(f"First few columns of first row:")
    print(df.iloc[0, :3])  # Show first 5 columns of first row
    
    return df


def save_node_embeddings(z_dict, dataset, output_dir="embeddings"):
    """
    For each node type in z_dict, save a CSV:
    <output_dir>/<node_type>_embeddings.csv
    Columns: id, dim0, dim1, ..., dim{D-1}
    """
    for ntype, emb in z_dict.items():
        # emb: tensor [num_nodes, hidden_dim]
        arr = emb.cpu().numpy()
        hidden_dim = arr.shape[1]

        # invert the id_mapping so index → original ID
        inv_map = {idx: orig for orig, idx in dataset.id_mapping[ntype].items()}
        ids = [inv_map[i] for i in range(arr.shape[0])]

        # build DataFrame
        cols = [f"dim{i}" for i in range(hidden_dim)]
        df = pd.DataFrame(arr, index=ids, columns=cols)
        df.index.name = ntype + "_id"

        # write to CSV
        out_path = os.path.join(output_dir, f"{ntype}_embeddings.csv")
        df.to_csv(out_path)
        logger.info(f"Saved {ntype} embeddings to {out_path}")


if __name__ == "__main__":
    # get config
    config = dutils.load_config()

    # data = main()
    map_nodes = parse_node_files()
    for map_type, map_value in map_nodes.items():
        print("{}: {}".format(map_type, json.dumps(list(map_value.items())[:2], indent=2)))

    # get the node embeddings and the dataset for mappings of neo4j id
    path_model = config.get(dutils.KEY_INFERENCE).get(dutils.KEY_MODEL_PATH)
    model, data, dataset = load_model_and_data(path_model=path_model)
    logger.info("from path: {}, got loaded model: {}".format(path_model, model))

    z_dict = get_node_embeddings(model, data)
    # logger.info("got node embeddings: {}".format(node_embeddings))
    for key, value in z_dict.items():
        logger.info("for embedding key: {}, got tensor shape: {}".format(key, value.shape))

    # get the map of tensors by node name
    z_dict = get_node_embeddings(model=model, data=data)
    #   map_node_tensor = create_tensor_map(map_node_embeddings=z_dict, map_node_ids=map_nodes, dataset=dataset)

    # get the embedding tensors by node type
    map_embedding_by_type = create_tensor_map_by_node_type(map_node_embeddings=z_dict, map_node_ids=map_nodes, dataset=dataset)

    # loop through type
    for node_type, map_node_tensor in map_embedding_by_type.items():
       logger.info("for node type: {} got tensor map of length: {}".format(node_type, len(map_node_tensor)))
       path_embeddings_file = config.get(dutils.KEY_INFERENCE).get(dutils.KEY_NODE_EMBEDDINGS_BY_TYPE)
       save_tensors_to_csv(map_tensor=map_node_tensor, output_filename=path_embeddings_file.format(node_type))


    # # save the tensor map to df csv file
    # path_embeddings_file = config.get(dutils.KEY_INFERENCE).get(dutils.KEY_NODE_EMBEDDINGS)
    # save_tensors_to_csv(map_tensor=map_node_tensor, output_filename=path_embeddings_file)
    # # print("got tensor map: {}".format(map_node_tensor))








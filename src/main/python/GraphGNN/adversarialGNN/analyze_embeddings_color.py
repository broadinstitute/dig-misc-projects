

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import umap.umap_ as umap
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')
import dcc_utils as dutils


# constants
logger = dutils.get_logger(__name__)
DEBUG = True

DIR_DATA = "/Users/mduby/Data/Broad/PortalAI/Embeddings/20250712advGnnGeneCombinedMinusPriorEpoch300Loss0_24"
FILE_EMBEDDING = "{}/node_embeddings_trait.csv".format(DIR_DATA)
FILE_MAPPING = "{}/pigean-phenotypes.csv".format(DIR_DATA)
FILE_PNG = "{}/Analysis/umap_parameter_comparison_color_trait.png".format(DIR_DATA)


def create_umap_comparison_file_for_node_type_color(
        csv_file: str,
        mapping_file: str,
        node_type: str
    ):
    """
    Creates a grid of UMAP plots for the embeddings in `csv_file`,
    coloring points by their display name (loaded from `mapping_file`).
    """
    # 1. Read in your embeddings and your mapping
    df = pd.read_csv(csv_file)  
    mapping = pd.read_csv(mapping_file)  # must have 'trait' and 'display_name' columns

    # log
    print("using embedding file: {}".format(csv_file))
    print("using mapping file: {}".format(mapping_file))

    # 2. Merge so df gets a 'display_group' column
    df = df.merge(
        mapping[['phenotype','display_group']],
        left_on='key', right_on='phenotype',
        how='left'
    )
    if df['display_group'].isnull().any():
        missing = df.loc[df['display_group'].isnull(), 'key'].unique()
        print(f"Warning: no display_group found for keys: {missing}")

    # 3. Prepare numeric features
    feature_cols = [c for c in df.columns if c.startswith('val_')]
    X = df[feature_cols].values
    X_scaled = StandardScaler().fit_transform(X)

    # 4. Build a color‐map for each display name
    groups = df['display_group'].unique()
    n = len(groups)
    print("got usnique groups of size: {}".format(n))
    # get an HSV colormap with exactly n equally‐spaced hues
    cmap = plt.cm.get_cmap('hsv', n)
    color_dict = {g: cmap(i) for i, g in enumerate(groups)}    
    # not enough colors for 60 groups
    # labels = df['display_group'].unique()
    # print("got usnique groups of size: {}".format(len(labels)))
    # cmap = plt.get_cmap('tab20')         # up to 20 distinct colors
    # color_dict = {lab: cmap(i) for i, lab in enumerate(labels)}

    # 5. UMAP parameter grid
    param_combinations = [
        {'n_neighbors': 3,  'min_dist': 0.001, 'title': 'n_n=3,  m_d=0.001'},
        {'n_neighbors': 5,  'min_dist': 0.005, 'title': 'n_n=5,  m_d=0.005'},
        {'n_neighbors': 5,  'min_dist': 0.01,  'title': 'n_n=5,  m_d=0.01'},
        {'n_neighbors': 10, 'min_dist': 0.002, 'title': 'n_n=10, m_d=0.002'},
        {'n_neighbors': 15, 'min_dist': 0.001, 'title': 'n_n=15, m_d=0.001'},
        {'n_neighbors': 10, 'min_dist': 0.01,  'spread': 0.3,
         'title': 'n_n=10, m_d=0.01, spread=0.3'},
    ]

    # 6. Set up figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), squeeze=False)

    for i, params in enumerate(param_combinations):
        row, col = divmod(i, 3)
        reducer = umap.UMAP(
            n_neighbors=params['n_neighbors'],
            min_dist=params['min_dist'],
            n_components=2,
            random_state=42,
            **({'spread': params['spread']} if 'spread' in params else {})
        )
        embedding = reducer.fit_transform(X_scaled)
        ax = axes[row][col]

        # 7. Plot each display_name as its own scatter
        for lab in groups:
            mask = df['display_group'] == lab
            ax.scatter(
                embedding[mask, 0],
                embedding[mask, 1],
                c=[color_dict[lab]],
                label=lab,
                alpha=0.7,
                s=50
            )

        ax.set_title(params['title'])
        ax.set_xlabel('UMAP Dimension 1')
        ax.set_ylabel('UMAP Dimension 2')
        ax.grid(True, alpha=0.3)
        ax.legend(
            title='Display Group',
            bbox_to_anchor=(1.05, 1),
            loc='upper left',
            fontsize='small'
        )

    plt.tight_layout()
    # out_path = f"umap_parameter_comparison_{node_type}.png"
    out_path = FILE_PNG
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Saved: {out_path}")



def create_umap_visualization(csv_file_path, output_file=None):
    """
    Create a UMAP visualization from CSV data with numerical features.
    
    Parameters:
    csv_file_path (str): Path to the CSV file
    output_file (str, optional): Path to save the plot. If None, displays the plot.
    """
    
    # Read the CSV file
    print("Reading CSV file...")
    df = pd.read_csv(csv_file_path)
    print(f"Data shape: {df.shape}")
    
    # Extract the key column and numerical features
    keys = df['key'].values
    feature_columns = [col for col in df.columns if col.startswith('val_')]
    features = df[feature_columns].values
    
    print(f"Number of samples: {len(keys)}")
    print(f"Number of features: {len(feature_columns)}")
    
    # Standardize the features
    print("Standardizing features...")
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Apply UMAP
    print("Applying UMAP dimensionality reduction...")
    umap_reducer = umap.UMAP(
        n_neighbors=15,      # Number of neighbors to consider
        min_dist=0.1,        # Minimum distance between points
        n_components=2,      # 2D visualization
        metric='euclidean',  # Distance metric
        random_state=42      # For reproducibility
    )
    
    embedding = umap_reducer.fit_transform(features_scaled)
    
    # Create the visualization
    plt.figure(figsize=(12, 8))
    
    # Create scatter plot
    scatter = plt.scatter(
        embedding[:, 0], 
        embedding[:, 1], 
        c=np.arange(len(embedding)),  # Color by index
        cmap='viridis',
        alpha=0.7,
        s=50
    )
    
    # Add labels for each point (showing first 20 chars of key)
    for i, key in enumerate(keys):
        plt.annotate(
            key[:20] + '...' if len(key) > 20 else key,
            (embedding[i, 0], embedding[i, 1]),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
            alpha=0.7
        )
    
    plt.colorbar(scatter, label='Sample Index')
    plt.title('UMAP Visualization of High-Dimensional Data', fontsize=16, fontweight='bold')
    plt.xlabel('UMAP Dimension 1', fontsize=12)
    plt.ylabel('UMAP Dimension 2', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save or display the plot
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
    else:
        plt.show()
    
    # Print some statistics
    print("\nUMAP Results:")
    print(f"Original dimensions: {features.shape[1]}")
    print(f"Reduced dimensions: {embedding.shape[1]}")
    print(f"Embedding range - X: [{embedding[:, 0].min():.2f}, {embedding[:, 0].max():.2f}]")
    print(f"Embedding range - Y: [{embedding[:, 1].min():.2f}, {embedding[:, 1].max():.2f}]")
    
    return embedding, umap_reducer

def create_enhanced_umap_plot(csv_file_path, output_file=None):
    """
    Create an enhanced UMAP visualization with multiple plot types.
    """
    # Read and process data
    df = pd.read_csv(csv_file_path)
    keys = df['key'].values
    feature_columns = [col for col in df.columns if col.startswith('val_')]
    features = df[feature_columns].values
    
    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Apply UMAP
    umap_reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
    embedding = umap_reducer.fit_transform(features_scaled)
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Basic scatter plot
    axes[0, 0].scatter(embedding[:, 0], embedding[:, 1], alpha=0.7, s=50)
    axes[0, 0].set_title('Basic UMAP Scatter Plot')
    axes[0, 0].set_xlabel('UMAP Dimension 1')
    axes[0, 0].set_ylabel('UMAP Dimension 2')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Colored by index
    scatter1 = axes[0, 1].scatter(embedding[:, 0], embedding[:, 1], 
                                  c=np.arange(len(embedding)), cmap='viridis', alpha=0.7, s=50)
    axes[0, 1].set_title('UMAP Colored by Sample Index')
    axes[0, 1].set_xlabel('UMAP Dimension 1')
    axes[0, 1].set_ylabel('UMAP Dimension 2')
    axes[0, 1].grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=axes[0, 1])
    
    # Plot 3: Density plot
    axes[1, 0].hexbin(embedding[:, 0], embedding[:, 1], gridsize=20, cmap='Blues', alpha=0.7)
    axes[1, 0].set_title('UMAP Density Plot')
    axes[1, 0].set_xlabel('UMAP Dimension 1')
    axes[1, 0].set_ylabel('UMAP Dimension 2')
    
    # Plot 4: With labels
    axes[1, 1].scatter(embedding[:, 0], embedding[:, 1], alpha=0.7, s=50)
    for i, key in enumerate(keys):
        axes[1, 1].annotate(f'{i}', (embedding[i, 0], embedding[i, 1]), 
                           xytext=(2, 2), textcoords='offset points', fontsize=8)
    axes[1, 1].set_title('UMAP with Sample Numbers')
    axes[1, 1].set_xlabel('UMAP Dimension 1')
    axes[1, 1].set_ylabel('UMAP Dimension 2')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Enhanced plot saved to: {output_file}")
    else:
        plt.show()
    
    return embedding, umap_reducer


def create_umap_comparison_file_for_node_type(csv_file, node_type):
    '''
    creates a umap graphic file for the dataframe provided
    '''
    # Read data
    file_out = "umap_parameter_comparison_{}.png".format(node_type)
    df = pd.read_csv(csv_file)

    # log
    print("\nExperimenting with different UMAP parameters for node type: {}".format(node_type))

    # get the features
    feature_columns = [col for col in df.columns if col.startswith('val_')]
    features = df[feature_columns].values
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Try different parameter combinations
    # param_combinations = [
    #     {'n_neighbors': 5, 'min_dist': 0.01, 'title': 'n_neighbors=5, min_dist=0.01'},
    #     {'n_neighbors': 30, 'min_dist': 0.5, 'title': 'n_neighbors=30, min_dist=0.5'},
    #     {'n_neighbors': 15, 'min_dist': 0.1, 'title': 'n_neighbors=15, min_dist=0.1 (default)'}
    # ]
    
    param_combinations = [
        # very extreme: almost purely local structure
        {'n_neighbors': 3,  'min_dist': 0.001,  'title': 'n_neighbors=3,  min_dist=0.001'},

        # still small neighbor‐count but allow slight breathing room
        {'n_neighbors': 5,  'min_dist': 0.005,  'title': 'n_neighbors=5,  min_dist=0.005'},

        {'n_neighbors': 5, 'min_dist': 0.01, 'title': 'n_neighbors=5, min_dist=0.01'},

        # a bit more neighbors to capture slightly larger “micro‐clusters”
        {'n_neighbors': 10, 'min_dist': 0.002,  'title': 'n_neighbors=10, min_dist=0.002'},

        # mid‐range neighbor count but force ultra‐tight packing
        {'n_neighbors': 15, 'min_dist': 0.001,  'title': 'n_neighbors=15, min_dist=0.001'},

        # you can also experiment with the 'spread' param—
        # e.g. spread=0.3 makes clusters even more condensed
        {'n_neighbors': 10, 'min_dist': 0.01,  'spread': 0.3,
        'title': 'n_neighbors=10, min_dist=0.01, spread=0.3'},
    ]

    # fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    for i, params in enumerate(param_combinations):
        # Calculate row and column indices
        row = i // 3
        col = i % 3
        
        umap_reducer = umap.UMAP(
            n_neighbors=params['n_neighbors'],
            min_dist=params['min_dist'],
            n_components=2,
            random_state=42
        )
        embedding = umap_reducer.fit_transform(features_scaled)
        
        axes[row, col].scatter(embedding[:, 0], embedding[:, 1], alpha=0.7, s=50)
        axes[row, col].set_title(params['title'])
        axes[row, col].set_xlabel('UMAP Dimension 1')
        axes[row, col].set_ylabel('UMAP Dimension 2')
        axes[row, col].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(file_out, dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Parameter comparison plot saved as '{}'".format(file_out))



def create_umap_comparison_file_for_node_type_jason_test(csv_file, node_type):
    '''
    creates a umap graphic file for the dataframe provided
    '''
    # Read data
    file_out = "umap_parameter_comparison_color_{}.png".format(node_type)
    df = pd.read_csv(csv_file)

    # log
    print("\nExperimenting with different UMAP parameters for node type: {}".format(node_type))

    # # get the features
    # feature_columns = [col for col in df.columns if col.startswith('val_')]
    # features = df[feature_columns].values
    # scaler = StandardScaler()
    # features_scaled = scaler.fit_transform(features)
    
    # Try different parameter combinations
    # param_combinations = [
    #     {'n_neighbors': 5, 'min_dist': 0.01, 'title': 'n_neighbors=5, min_dist=0.01'},
    #     {'n_neighbors': 30, 'min_dist': 0.5, 'title': 'n_neighbors=30, min_dist=0.5'},
    #     {'n_neighbors': 15, 'min_dist': 0.1, 'title': 'n_neighbors=15, min_dist=0.1 (default)'}
    # ]
    
    param_combinations = [
        # # very extreme: almost purely local structure
        # {'n_neighbors': 3,  'min_dist': 0.001,  'title': 'n_neighbors=3,  min_dist=0.001'},

        # # still small neighbor‐count but allow slight breathing room
        # {'n_neighbors': 5,  'min_dist': 0.005,  'title': 'n_neighbors=5,  min_dist=0.005'},

        # {'n_neighbors': 5, 'min_dist': 0.01, 'title': 'n_neighbors=5, min_dist=0.01'},

        # # a bit more neighbors to capture slightly larger “micro‐clusters”
        # {'n_neighbors': 10, 'min_dist': 0.002,  'title': 'n_neighbors=10, min_dist=0.002'},

        # # mid‐range neighbor count but force ultra‐tight packing
        # {'n_neighbors': 15, 'min_dist': 0.001,  'title': 'n_neighbors=15, min_dist=0.001'},

        # you can also experiment with the 'spread' param—
        # e.g. spread=0.3 makes clusters even more condensed
        {'n_neighbors': 10, 'min_dist': 0.01,  'spread': 0.3,
        'title': 'n_neighbors=10, min_dist=0.01, spread=0.3'},
    ]

    # fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for i, params in enumerate(param_combinations):
        # Calculate row and column indices
        row = i // 3
        col = i % 3

        embedding = get_umap_of_embeddings(df=df, params=params)

        # umap_reducer = umap.UMAP(
        #     n_neighbors=params['n_neighbors'],
        #     min_dist=params['min_dist'],
        #     n_components=2,
        #     random_state=42
        # )

        # # umap
        # embedding = umap_reducer.fit_transform(features_scaled)
        
        # split the embeddin df based on value of y dimension
        # mask = df['embedding'].apply(lambda vec: vec[1] > 0)
        mask = embedding[:, 1] > 0

        # features_scaled_pos   = features_scaled[ mask ]   # rows where embedding[:,1] > 0
        # features_scaled_nonpos = features_scaled[~mask ]  # rows where embedding[:,1] <= 0

        # embedding_pos = umap_reducer.fit_transform(features_scaled_pos)
        # embedding_nonpos = umap_reducer.fit_transform(features_scaled_nonpos)

        embedding_pos = get_umap_of_embeddings(df=df[mask], params=params)
        embedding_nonpos = get_umap_of_embeddings(df=df[~mask], params=params)

        title_plot = [params['title'], 'y_umap pos', 'y_umap neg']

        print("got 2 dataframes of shape: {} and {} from shape: {}".format(embedding_pos.shape, embedding_nonpos.shape, embedding.shape))

        for index_row, df_to_plot in enumerate([embedding, embedding_pos, embedding_nonpos]):
            print("doing row: {}".format(index_row))
            axes[index_row].scatter(df_to_plot[:, 0], df_to_plot[:, 1], alpha=0.7, s=50)
            axes[index_row].set_title(title_plot[index_row])
            axes[index_row].set_xlabel('UMAP Dimension 1')
            axes[index_row].set_ylabel('UMAP Dimension 2')
            axes[index_row].grid(True, alpha=0.3)
            
            # axes[row, index_row].scatter(df_to_plot[:, 0], df_to_plot[:, 1], alpha=0.7, s=50)
            # axes[row, index_row].set_title(title_plot[index_row])
            # axes[row, index_row].set_xlabel('UMAP Dimension 1')
            # axes[row, index_row].set_ylabel('UMAP Dimension 2')
            # axes[row, index_row].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(file_out, dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Parameter comparison plot saved as '{}'".format(file_out))


def get_umap_of_embeddings(df, params):
    # scale
    feature_columns = [col for col in df.columns if col.startswith('val_')]
    features = df[feature_columns].values
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # umap
    umap_reducer = umap.UMAP(
        n_neighbors=params['n_neighbors'],
        min_dist=params['min_dist'],
        n_components=2,
        random_state=42
    )

    # umap
    embedding = umap_reducer.fit_transform(features_scaled)

    # return
    return embedding


def create_umap_comparison_dataframes_for_node_type(csv_file, node_type, only_xy=False):
    '''
    creates dataframes with UMAP x/y coordinates for different parameter combinations
    and saves them to CSV files
    '''
    # Read data
    df = pd.read_csv(csv_file)

    # log
    print("\nCreating UMAP dataframes with different parameters for node type: {}".format(node_type))

    # get the features
    feature_columns = [col for col in df.columns if col.startswith('val_')]
    features = df[feature_columns].values
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Try different parameter combinations
    param_combinations = [
        # very extreme: almost purely local structure
        {'n_neighbors': 3,  'min_dist': 0.001,  'title': 'n_neighbors_3_min_dist_0.001'},

        # still small neighbor‐count but allow slight breathing room
        {'n_neighbors': 5,  'min_dist': 0.005,  'title': 'n_neighbors_5_min_dist_0.005'},

        {'n_neighbors': 5, 'min_dist': 0.01, 'title': 'n_neighbors_5_min_dist_0.01'},

        # a bit more neighbors to capture slightly larger "micro‐clusters"
        {'n_neighbors': 10, 'min_dist': 0.002,  'title': 'n_neighbors_10_min_dist_0.002'},

        # mid‐range neighbor count but force ultra‐tight packing
        {'n_neighbors': 15, 'min_dist': 0.001,  'title': 'n_neighbors_15_min_dist_0.001'},

        # you can also experiment with the 'spread' param—
        # e.g. spread=0.3 makes clusters even more condensed
        {'n_neighbors': 10, 'min_dist': 0.01,  'spread': 0.3,
        'title': 'n_neighbors_10_min_dist_0.01_spread_0.3'},
    ]

    saved_files = []
    
    for i, params in enumerate(param_combinations):
        print(f"Processing parameter combination {i+1}/{len(param_combinations)}: {params['title']}")
        
        # Create UMAP reducer with current parameters
        umap_params = {
            'n_neighbors': params['n_neighbors'],
            'min_dist': params['min_dist'],
            'n_components': 2,
            'random_state': 42
        }
        
        # Add spread parameter if specified
        if 'spread' in params:
            umap_params['spread'] = params['spread']
            
        umap_reducer = umap.UMAP(**umap_params)
        embedding = umap_reducer.fit_transform(features_scaled)
        
        # Create dataframe with original data plus UMAP coordinates
        if only_xy:
            result_df = pd.DataFrame({
                'key': df['key'],
                'umap_x': embedding[:, 0],
                'umap_y': embedding[:, 1]
            })                 
        else:
            result_df = df.copy()
            result_df['umap_x'] = embedding[:, 0]
            result_df['umap_y'] = embedding[:, 1]

        # Create filename
        file_out = f"umap_data_{node_type}_{params['title']}.csv"
        
        # Save to CSV
        result_df.to_csv(file_out, index=False)
        saved_files.append(file_out)
        
        print(f"  Saved: {file_out}")
    
    print(f"\nAll UMAP dataframes saved for node type '{node_type}':")
    for file in saved_files:
        print(f"  - {file}")
    
    return saved_files


# Example usage
if __name__ == "__main__":
    # load configuration
    config = dutils.load_config()

    # get the node embedding file names
    file_name = config.get(dutils.KEY_INFERENCE).get(dutils.KEY_NODE_EMBEDDINGS_BY_TYPE)

    # for node_type in ['gene', 'trait', 'gene_set', 'factor']:
    for node_type in ['trait']:
        csv_file = file_name.format(node_type)

        # create_umap_comparison_file_for_node_type(csv_file=csv_file, node_type=node_type)
        # create_umap_comparison_dataframes_for_node_type(csv_file=csv_file, node_type=node_type, only_xy=True)
        create_umap_comparison_file_for_node_type_color(csv_file=FILE_EMBEDDING, node_type=node_type, mapping_file=FILE_MAPPING)




    


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

# Example usage
if __name__ == "__main__":
    # load configuration
    config = dutils.load_config()

    # get the node embedding file names
    file_name = config.get(dutils.KEY_INFERENCE).get(dutils.KEY_NODE_EMBEDDINGS_BY_TYPE)

    # Replace 'your_data.csv' with the path to your CSV file
    csv_file = file_name.format('gene')
    
    print("Creating basic UMAP visualization...")
    embedding, reducer = create_umap_visualization(csv_file)
    
    print("\nCreating enhanced UMAP visualization...")
    embedding_enhanced, reducer_enhanced = create_enhanced_umap_plot(csv_file, 'umap_enhanced.png')
    
    # You can also experiment with different UMAP parameters
    print("\nExperimenting with different UMAP parameters...")
    
    # Read data
    df = pd.read_csv(csv_file)
    feature_columns = [col for col in df.columns if col.startswith('val_')]
    features = df[feature_columns].values
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Try different parameter combinations
    param_combinations = [
        {'n_neighbors': 5, 'min_dist': 0.01, 'title': 'n_neighbors=5, min_dist=0.01'},
        {'n_neighbors': 30, 'min_dist': 0.5, 'title': 'n_neighbors=30, min_dist=0.5'},
        {'n_neighbors': 15, 'min_dist': 0.1, 'title': 'n_neighbors=15, min_dist=0.1 (default)'}
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for i, params in enumerate(param_combinations):
        umap_reducer = umap.UMAP(
            n_neighbors=params['n_neighbors'],
            min_dist=params['min_dist'],
            n_components=2,
            random_state=42
        )
        embedding = umap_reducer.fit_transform(features_scaled)
        
        axes[i].scatter(embedding[:, 0], embedding[:, 1], alpha=0.7, s=50)
        axes[i].set_title(params['title'])
        axes[i].set_xlabel('UMAP Dimension 1')
        axes[i].set_ylabel('UMAP Dimension 2')
        axes[i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('umap_parameter_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Parameter comparison plot saved as 'umap_parameter_comparison.png'")

    
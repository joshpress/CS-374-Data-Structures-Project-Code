# CS-374 Data Structures Project: Knowledge Graph

## Overview

This project implements a knowledge graph on the [Kensho Derived Wikimedia Dataset](https://www.kaggle.com/datasets/kenshoresearch/kensho-derived-wikimedia-data) using Pandas, NetworkX and Pyvis. It supports rendering the knowledge graph and performing queries on it. Datasets can also be created from the top viewed articles with more branching out.

## Driver File
The driver file shows the main functions of the knowledge graph such as creating a dataset, rendering the knowledge graph, and querying it.
## Creating Dataset

 The createDataset.py file contains a function `createDataset(top_views, branch)` that generates a dataset from the [Kensho Derived Wikimedia Dataset](https://www.kaggle.com/datasets/kenshoresearch/kensho-derived-wikimedia-data), which is a cleaned dataset of Wikipedia data from 2019. The function takes in `top_views` which filters to only the top `n` viewed articles, then looks at other top articles 
 related to those with `branch`. The function returns a `top_graph` DataFrame that can be saved to a CSV for future use. The files needed from Kaggle to generate the dataset are:
   - `item.csv`
   - `page.csv`
   - `property_aliases.csv`
   - `statements.csv`

## Loading Dataset and creating Knowledge Graph
The `createKnowledgeGraph` file contains the `KnowledgeGraph` class. The constructor takes in a csv file from `createDataset` then creates a NetworkX directed graph object. The graph is stored in `G`.


### Files
The file naming convention is `top_n_branch_k.csv`, where `n` is the top viewed articles with `k` branches out from them.
Included files are:
  - `top_5_branch_2.csv`, `top_10_branch_2.csv` for smaller visualizations
  - `top_50_branch_10.csv`, for larger visualizations
  - `top_15000_branch_10.csv`, for query method
### Class Methods
1. `createKnowledgeGraph()`, a helper function for creating the NetworkX graph object. Converts the Pandas DataFrame into a NetworkX graph object and assigns node and edge labels.


2. `renderGraph()` which creates a Pyvis visualization of the graph in an HTML file. The method takes in `font_size` and `file_name` which are 12 and `knowledge_graph.html` by default. A physics slider is available at the bottom to adjust node spacing and ordering.


3. `query()` searches the graph for neighbors, then creates a set of neighbors of the search term. The method takes in:
      *  `search_term` to search for, a `directed` boolean, which converts the graph into an undirected graph to broaden the search terms, False by default. 
      * `search_limit` limits the number of matches to expand from. Limit is 5
      * `neighbor_limit` limits the number of neighbors from each match. The default is 5.
      * `file_name` is the name of the subgraph, default is `query_subgraph.html`.

      The result is a list of IDs, neighbors, edge aliases and a Pyvis visualization.

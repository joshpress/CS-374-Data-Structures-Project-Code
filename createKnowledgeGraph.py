import pandas as pd
import networkx as nx
from pyvis.network import Network


class KnowledgeGraph:
    '''
   Creates a knowledge graph from the CSV files generated from createKnowledgeGraph.
   Plots use pyvis which is saved in an HTML file.
   Methods: 
   getGraph() returns the NetworkX graph object.
   renderGraph() is used to render the knowledge graph in pyvis.
   query() looks for neighbors of the search term, returns results and a plot.
    '''

    def __init__(self, csv_file):
        self.graph_csv = csv_file
        self.graph_df = pd.read_csv(self.graph_csv)
        self.G = self.createKnowledgeGraph()  # networkx graph object

    # helper function for creating graph from dataframe
    def createKnowledgeGraph(self):

        # build graph from the dataframe
        G = nx.from_pandas_edgelist(
            self.graph_df,
            source='source_item_id',
            target='target_item_id',
            edge_attr='en_alias',
            create_using=nx.DiGraph()
        )

        # renaming columns to make a label map
        source_df = self.graph_df[['source_item_id', 'en_label_src']]
        source_df = source_df.rename(
            columns={'source_item_id': 'id', 'en_label_src': 'label'})

        target_df = self.graph_df[['target_item_id', 'en_label_tgt']].rename(
            columns={'target_item_id': 'id', 'en_label_tgt': 'label'})

        # create a mapping for source to target
        label_df = pd.concat([source_df, target_df]).drop_duplicates()
        label_map = dict(zip(label_df['id'], label_df['label']))
        nx.set_node_attributes(G, label_map, 'label')

        # map the (source,target) as well as alias (edge label)
        edge_label_map = dict(zip(zip(
            self.graph_df['source_item_id'], self.graph_df['target_item_id']), self.graph_df['en_alias']))
        nx.set_edge_attributes(G, edge_label_map, 'en_alias')

        return G
    

    # renderGraph creates a visualization using pyvis, saved as an HTML file
    def renderGraph(self, font_size=12, file_name="knowledge_graph.html"):

        # setting edge labels, data parameter is for source, target, edge label
        # str is to fix an error where the graph wasn't rendering
        for u, v, data in self.G.edges(data=True):
            edge_label = data.get('en_alias', '')
            data["title"] = str(edge_label)
            data["label"] = str(edge_label)
            data["font"] = {"size": font_size}

        # setting font size for nodes
        for node_id, data in self.G.nodes(data=True):
            node_label = data.get('label', '')
            data["title"] = str(node_label)
            data["label"] = str(node_label)
            data["font"] = {"size": font_size}

        # converting networkx graph to pyvis
        pyvis_graph = Network(notebook=True, height='500px', 
                              width='100%', directed=True, cdn_resources='in_line')
        pyvis_graph.from_nx(self.G)
        pyvis_graph.show_buttons(filter_=['physics'])
        # this code helps fix the utf-8 error on windows
        html = pyvis_graph.generate_html()
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Graph rendered in '{file_name}'")

    # query searches the graph for the term as well as its neighbors,
    # undirected helps make the search more flexible
    # result is a list of matches and a pyvis plot
    def query(self, search_term, directed=False,
              search_limit=5, neighbor_limit=5, file_name="query_subgraph.html"):

        # create a copy so the original graph isn't modified
        G_temp = self.G.copy()
        # convert to undirected graph for easier traversal
        if not directed:
            G_temp = self.G.to_undirected()
        # get edge labels and map source to target
        edge_labels = nx.get_edge_attributes(G_temp, 'en_alias')
        edge_label_map = {(u, v): label for (
            u, v), label in edge_labels.items()}
        label_map = nx.get_node_attributes(G_temp, 'label')

        search_term = search_term.lower()
        matches = []
        for id, label in label_map.items():
            # making sure the label is a string
            if isinstance(label, str) and search_term.lower() in label.lower():
                matches.append(id)
        # if we find a match, add it to the set
        if matches:

            node_set = set()
            for node_id in matches[:search_limit]:
                # add the node to the set of results
                node_set.add(node_id)
                neighbors = list(G_temp.neighbors(node_id))
                limited_neighbors = neighbors[:neighbor_limit]
                print(
                    f"neighbors of '{label_map.get(node_id)}' (node id: {node_id}):")
                # look at the neighbors of the node/successors for directed
                for neighbor in limited_neighbors:
                    node_set.add(neighbor)
                    # look for both directions of the edge label
                    alias = edge_label_map.get((node_id, neighbor)) or edge_label_map.get(
                        (neighbor, node_id)) or ''

                    print(
                        f"{label_map.get(neighbor)} id {neighbor}, edge alias: {alias}")

            G_subgraph = G_temp.subgraph(node_set)
            # setting edge labels for the subgraph
            for u, v, data in G_subgraph.edges(data=True):
                edge_label = data.get('en_alias', '')
                data["title"] = str(edge_label)
                data["label"] = str(edge_label)
            pyvis_graph = Network(notebook=True, height='500px',
                                  width='100%', cdn_resources='in_line', directed=directed)
            pyvis_graph.from_nx(G_subgraph)
            pyvis_graph.show_buttons(filter_=['physics'])

            # saving as utf-8 again
            html = pyvis_graph.generate_html()
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Subgraph rendered in '{file_name}'")

        else:
            print(f"'{search_term}' not found in the graph.")

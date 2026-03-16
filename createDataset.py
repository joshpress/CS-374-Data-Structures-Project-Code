import pandas as pd


def createDataset(top_views=1000, branch=10):
    '''
   creates a dataset for the top n most viewed items on the Kensho Wikidata files.
   branches based out from the top items
   returns a pandas dataframe with the top items, their source and target connections, as well as edge labels


   this assumes the item.csv, page.csv, property_aliases.csv, and statements.csv files are in the same directory as this script.

    '''
    try:
        # Wikidata item labels and descriptions in English.
        item = pd.read_csv('item.csv')
        # Wikipedia page metadata.
        page = pd.read_csv('page.csv')  
        # Wikidata property aliases in English.
        property_aliases = pd.read_csv('property_aliases.csv')
        # Truthy QPQ Wikidata item statements.
        statements = pd.read_csv('statements.csv')
    except FileNotFoundError:
        print("CSV(s) not found")
        return None

    top_ids = page.nlargest(top_views, 'views')[['item_id']]

    full_graph = pd.merge(top_ids, statements, left_on='item_id',
                          right_on='source_item_id', how='inner')

    # look at the other items that are conncected to the top n items, branching out
    top_n_per_entity = full_graph.groupby('source_item_id').head(branch)

    top_graph = pd.merge(top_n_per_entity, item,
                         left_on='source_item_id', right_on='item_id', how='left')
    #getting source and target for mapping
    top_graph = pd.merge(top_graph, item, left_on='target_item_id',
                         right_on='item_id', how='left', suffixes=('_src', '_tgt'))

    property_aliases = property_aliases.drop_duplicates(subset=['property_id'])
    # final merge for edge labels
    top_graph = pd.merge(top_graph, property_aliases,
                         left_on='edge_property_id', right_on='property_id', how='left')

    return top_graph
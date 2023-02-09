from manageNetwork import network
import pandas as pd

metadata = pd.read_csv('metadata.csv')
dbUrl = metadata.iloc[0]['db_url']
db_name = metadata.iloc[0]['db_name']
db_pass = metadata.iloc[0]['db_pass']
net = network(dbUrl, db_name, db_pass)

net = network('bolt://localhost:7687', 'neo4j', 'burna-36')

db_name = "neo4j"

#remove database
net.removeNet(db_name)
#add categories to the graph
net.add_node_category("categories", db_name)
#add edges between categories
net.add_edge_category("categories", db_name)
#add entites to the graph
net.add_node_entity("entities", db_name)
#add edges between categories and entities
net.add_edge_entity("entities", db_name)
#add edges between entities of the graph
net.add_edge_relations("entities", "relations", db_name)
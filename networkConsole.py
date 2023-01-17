from manageNetwork import network


net = network('bolt://localhost:7687', 'neo4j', 'burna-36')

db_name = "neo4j"

net.removeNet(db_name)
net.add_node_category("categories", db_name)
net.add_edge_category("categories", db_name)
net.add_node_entity("entities", db_name)
net.add_edge_entity("entities", db_name)
net.add_edge_relations("entities", "relations", db_name)
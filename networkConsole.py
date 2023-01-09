from manageNetwork import network


net = network('bolt://localhost:7687', 'neo4j', '228218')

net.add_node_category("categories", "network")
net.add_edge_category("categories", "network")
net.add_node_entity("entities", "network")
net.add_edge_entity("entities", "network")
net.add_edge_relations("entities", "relations", "network")
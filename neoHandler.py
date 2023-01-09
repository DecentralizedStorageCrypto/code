import logging
from neo4j import GraphDatabase

class NEO4J:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    @staticmethod
    def enable_log(level, output_stream):
        handler = logging.StreamHandler(output_stream)
        handler.setLevel(level)
        logging.getLogger("neo4j").addHandler(handler)
        logging.getLogger("neo4j").setLevel(level)

    def create_new_player(self, db_name, labels=None, player=None, link=None, twitter=None, des=None):
        print(labels)
        if len(labels) == 1:
            label1 = labels[0]
            query = f"MERGE (:`{label1}` {{name: \"{player}\", link:\"{link}\", twitter:\"{twitter}\", des:\"{des}\"}})"
            with self.driver.session(database=db_name) as session:
                session.run(query)
        elif len(labels) == 2:
            label1 = labels[0]
            label2 = labels[1]
            query = f"MERGE (:`{label1}`:`{label2}` {{name: \"{player}\", link:\"{link}\", twitter:\"{twitter}\", des:\"{des}\"}})"
            with self.driver.session(database=db_name) as session:
                session.run(query)
        elif len(labels) == 3:
            label1 = labels[0]
            label2 = labels[1]
            label3 = labels[2]
            query = f"MERGE (:`{label1}`:`{label2}`:`{label3}` {{name: \"{player}\", link:\"{link}\", twitter:\"{twitter}\", des:\"{des}\"}})"
            with self.driver.session(database=db_name) as session:
                session.run(query)



    def create_new_edge_cat(self, db_name, labels1, node1, labels2, node2):

        if len(labels1) == 1 and len(labels2) == 1:
            label1_1 = labels1[0]
            label2_1 = labels2[0]
            query = f"MATCH (n1:`{label1_1}` {{name: \"{node1}\"}}), (n2:`{label2_1}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 2 and len(labels2) == 1:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label2_1 = labels2[0]
            query = f"MATCH (n1:`{label1_1}`:`{label1_2}` {{name: \"{node1}\"}}), (n2:`{label2_1}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 3 and len(labels2) == 1:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label1_3 = labels1[2]
            label2_1 = labels2[0]
            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`:`{label1_3}` {{name: \"{node1}\"}}), (n2:`{label2_1}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 1 and len(labels2) == 2:
            label1_1 = labels1[0]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            query = f"MATCH (n1:`{label1_1}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 1 and len(labels2) == 3:
            label1_1 = labels1[0]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            label2_3 = labels2[2]

            query = f"MATCH (n1:`{label1_1}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`:`{label2_3}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 2 and len(labels2) == 2:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label2_1 = labels2[0]
            label2_2 = labels2[1]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}` {{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 3 and len(labels2) == 3:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label1_3 = labels1[2]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            label2_3 = labels2[2]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`:`{label1_3}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`:`{label2_3}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:rcategory]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 2 and len(labels2) == 3:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            label2_3 = labels2[2]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`:`{label2_3}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 3 and len(labels2) == 2:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label1_3 = labels1[2]
            label2_1 = labels2[0]
            label2_2 = labels2[1]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`:`{label1_3}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`{{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:category]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)


    def create_new_edge_rel(self, db_name, labels1, node1, labels2, node2, weight=None):

        if len(labels1) == 1 and len(labels2) == 1:
            label1_1 = labels1[0]
            label2_1 = labels2[0]
            query = f"MATCH (n1:`{label1_1}` {{name: \"{node1}\"}}), (n2:`{label2_1}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 2 and len(labels2) == 1:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label2_1 = labels2[0]
            query = f"MATCH (n1:`{label1_1}`:`{label1_2}` {{name: \"{node1}\"}}), (n2:`{label2_1}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 3 and len(labels2) == 1:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label1_3 = labels1[2]
            label2_1 = labels2[0]
            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`:`{label1_3}` {{name: \"{node1}\"}}), (n2:`{label2_1}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 1 and len(labels2) == 2:
            label1_1 = labels1[0]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            query = f"MATCH (n1:`{label1_1}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 1 and len(labels2) == 3:
            label1_1 = labels1[0]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            label2_3 = labels2[2]

            query = f"MATCH (n1:`{label1_1}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`:`{label2_3}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 2 and len(labels2) == 2:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label2_1 = labels2[0]
            label2_2 = labels2[1]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}` {{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 3 and len(labels2) == 3:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label1_3 = labels1[2]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            label2_3 = labels2[2]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`:`{label1_3}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`:`{label2_3}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 2 and len(labels2) == 3:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label2_1 = labels2[0]
            label2_2 = labels2[1]
            label2_3 = labels2[2]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`:`{label2_3}` {{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

        elif len(labels1) == 3 and len(labels2) == 2:
            label1_1 = labels1[0]
            label1_2 = labels1[1]
            label1_3 = labels1[2]
            label2_1 = labels2[0]
            label2_2 = labels2[1]

            query = f"MATCH (n1:`{label1_1}`:`{label1_2}`:`{label1_3}`{{name: \"{node1}\"}}), (n2:`{label2_1}`:`{label2_2}`{{name: \"{node2}\"}}) " \
                    f"CREATE (n1)-[:relation {{weight:\"{weight}\"}}]->(n2)"
            with self.driver.session(database=db_name) as session:
                session.run(query)

    def find_player(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, person_name)
            for row in result:
                print("Found person: {row}".format(row=row))

    def clear_graph(self, db_name):
        delete_graph = "MATCH (n)" \
                       "DETACH DELETE n"
        with self.driver.session(database=db_name) as session:
            session.run(delete_graph)

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [row["name"] for row in result]

# if __name__ == "__main__":
#
#     bolt_url = "bolt://localhost:7687"
#     user = "neo4j"
#     password = "228218"
#     NEO4J.enable_log(logging.INFO, sys.stdout)
#     neo = NEO4J(bolt_url, user, password)
#     # neo.create_new_player("coin", "siacoin")
#     # neo.create_new_edge("coin", "siacoin", "coin", "filecoin", 1.4)
#     # neo.find_person("Alice")
#     neo.clear_graph()
#     neo.close()
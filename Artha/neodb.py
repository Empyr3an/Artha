from neo4j import GraphDatabase
# import sqlite3
# from twitter import TwitterAPI, TSQLite
import sqlite3
import csv

path = "/Users/harshasomisetty/Library/Application Support/com.Neo4j.Relate/"\
        "Data/dbmss/dbms-8c0b6b9b-8405-42f7-aee7-4bff9bf1d898/import/"\
        "follows.csv"


class Neo:

    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.session = self.driver.session()
        # automatically create unique id constraint
        self.session.run('''CREATE CONSTRAINT twitter_id IF NOT EXISTS ON (n:Person)
                            ASSERT n.id IS UNIQUE''')

    # TODO only add if node doensn't already exist
    def create_node(self, params):
        self.session.run("CREATE(p:Person $param)", param=params)

    def update_csv_location(self, username, location="../data/users"):

        conn_temp = sqlite3.connect(location+f"/u{username}.db")
        conn_temp.row_factory = self.dict_factory

        try:
            temp_follows = conn_temp.cursor() \
                                    .execute("select * from following") \
                                    .fetchall()
        except Exception:
            return -1

        with open(path, "w+") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                                                "id",
                                                "name",
                                                "username"
                                                ])
            writer.writeheader()
            writer.writerows(temp_follows)
        return len(temp_follows)

    def load_csv_data(self, username, location="../data/users"):
        if username == "checkra_":
            self.update_csv_location(username, location="../data")
            self.session.run('''
                            Merge (n:Person {username: 'checkra_'})
                            ON CREATE SET n.id ='1356259499431129092',
                                        n.name = 'Checkra',
                                        n.username = 'checkra_'
                             ''')
        else:
            csv_length = self.update_csv_location(username)

        if csv_length > 0:
            # insert all nodes from csv
            self.session.run('''
                        USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS
                        FROM 'file:/follows.csv' AS row
                        MERGE (n:Person {id:row.id})
                        ON CREATE SET n.id = row.id,
                                    n.name = row.name,
                                    n.username = row.username
                        ''')

            # create all edges
            node_result = self.session.run(
                        "USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS "
                        "FROM 'file:/follows.csv' AS row "
                        "MATCH (m:Person {username: '"+username+"'}) "
                        "MATCH (n:Person {id:row.id}) "
                        "MERGE (m)-[r:FOLLOWS]->(n) "
                        "return count(r)"
                        )

            return node_result
        else:
            return -1

    # TODO only add if relation doensn't already exist
    def create_relation(self, from_username, to_username):
        result = self.session.run("MATCH (n:Person), (m:Person) "
                                  "WHERE n.username = $from_username "
                                  "AND m.username = $to_username "
                                  "MERGE (n)-[:FOLLOWS]->(m)"
                                  "RETURN n.username, m.username",
                                  from_username=from_username,
                                  to_username=to_username)

        return [record for record in result]

    def check_relation(self, from_id, to_id):
        result = self.session.run("MATCH (n:Person {id: $from_id})-[r]-> "
                                  "(m:Person {id: $to_id})"
                                  "RETURN n,type(r),m",
                                  from_id=from_id, to_id=to_id)
        return [record for record in result]

    def clear_db(self):
        self.session.run("MATCH (n) DETACH DELETE (n)")
        return "Deleted"

    def get_nodes(self):
        nodes = self.session.run("MATCH (n) RETURN (n)")
        return [record["n"] for record in nodes]

    def get_relations(self):
        relations = self.session.run("MATCH (n)-[r]-> (m) RETURN n, r, m")
        return [record["r"] for record in relations]

    def print_nodes(self):
        for rec in self.get_nodes():
            print(rec["username"], rec["id"])

    def print_relations(self):
        for rec in self.get_relations():
            print(rec.start_node["username"],
                  rec.start_node["id"],
                  rec.type,
                  rec.end_node["username"],
                  rec.end_node["id"]
                  )

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = str(row[idx])
        return d

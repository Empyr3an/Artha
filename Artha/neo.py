from neo4j import GraphDatabase
# import sqlite3
# from twitter import TwitterAPI, TSQLite


class Neo:

    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.session = self.driver.session()

    def create_node(self, params):
        self.session.run("CREATE(p:Person $param)", param=params)

    def create_relation(session, from_id, to_id, type="Follows"):
        result = session.run("match (n:Person {id: $from_id}), "
                             "(m:Person {id: $to_id})"
                             f"merge (n)-[:{type}]- (m)",
                             "return n.username, m.username",
                             from_id=from_id, to_id=to_id)

        return [record for record in result]

    def check_relation(session, from_id, to_id):
        result = session.run("MATCH (n:Person {id: $from_id})-[r]- "
                             "(m:Person {id: $to_id})"
                             "RETURN n,type(r),m",
                             from_id=from_id, to_id=to_id)
        return [record for record in result]

    def clear_db(self):
        self.session.run("MATCH (n)-[r]- (m) DELETE r")
        self.session.run("MATCH (n) DELETE (n)")

    def get_nodes(self):
        nodes = self.session.run("MATCH (n) RETURN (n)")
        return [record["n"] for record in nodes]

    def get_relations(self):
        relations = self.session.run("MATCH (n)-[r]- (m) RETURN n, r, m")
        return [record["r"] for record in relations]

    def print_nodes(self):
        for rec in self.get_nodes():
            print(rec["username"])

    def print_relations(self):
        for rec in self.get_relations():
            print(rec.start_node["username"],
                  rec.type,
                  rec.end_node["username"]
                  )

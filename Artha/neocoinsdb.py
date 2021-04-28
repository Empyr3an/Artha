from neo4j import GraphDatabase
import csv
import Artha.crypto_data as crypto


class Neo:

    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.session = self.driver.session()
        self.path = "/Users/harshasomisetty/Library/Application Support/"\
                    "com.Neo4j.Relate/Data/dbmss/"\
                    "dbms-0dd5b437-acbf-4425-b485-3d197ae3db89/import/"

    def load_coins_data(self):
        markets = crypto.get_market_dict()
        inv_markets = crypto.get_invert_dict(markets)
        with open(self.path+"coins.csv", "w+") as w:
            cw = csv.writer(w)
            cw.writerow(["Name"])
            cw.writerows([[key] for ind, key in
                          enumerate(list(inv_markets.keys()))])
        self.session.run('''USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS
                                FROM 'file:/coins.csv' AS row
                                MERGE (n:Coin {name:row.Name})''')
        print("Updated coins")

    def clear_db(self):
        self.session.run("MATCH (n) DETACH DELETE (n)")
        return "Deleted"

    def get_nodes(self):
        nodes = self.session.run("MATCH (n) RETURN (n)")
        return [record["n"] for record in nodes]

    def get_relations(self):
        relations = self.session.run("MATCH (n)-[r]-> (m) RETURN n, r, m")
        return [record["r"] for record in relations]

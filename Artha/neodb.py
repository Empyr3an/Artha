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

    def update_coins_data(self):
        markets = crypto.get_market_dict()
        inv_markets = crypto.get_invert_dict(markets)
        with open(self.path+"coins.csv", "w+") as w:
            cw = csv.writer(w)
            cw.writerow(["ticker"])
            cw.writerows([[key] for ind, key in
                          enumerate(list(inv_markets.keys()))])

    # TODO add full name to coin nodes
    def load_coins(self):
        self.update_coins_data()

        self.session.run('''USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS
                            FROM 'file:/coins.csv' AS row
                            MERGE (n:Coin {ticker:row.ticker})''')
        print("Updated coins")

    def update_follows_csv(self, data, location=None):
        if not location:
            location = self.path+'follows.csv'

        with open(location, 'w+') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(["from", "id", "name", "username"])
            for row in data:
                csv_out.writerow(row)

        return len(data)

    def load_follows(self, data):
        length = self.update_follows_csv(data)

        if length > 0:
            # insert all nodes from csv
            follow_result = self.session.run('''
                        USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS
                        FROM 'file:/follows.csv' AS row
                        MERGE (n:Person {id:row.id})
                        ON CREATE SET n.id = row.id,
                                    n.name = row.name,
                                    n.username = row.username
                        ''')
            print("loaded People")
            # create all edges

            return follow_result
        else:
            return -1

    def load_relations(self, data):
        length = self.update_follows_csv(data)

        if length > 0:
            node_result = self.session.run('''
                        USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS
                        FROM 'file:/follows.csv' AS row
                        MATCH (m:Person {username:row.from})
                        MATCH (n:Person {id:row.id})
                        MERGE (m)-[r:FOLLOWS]->(n)
                        return count(r)
                    ''')
            print("loaded relations")
            return node_result
        else:
            return -1

    def update_mentions_data(self, data, location=None):
        if not location:
            location = self.path+'mentions.csv'

        with open(location, 'w+') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['username', 'ticker', 'weight'])
            for row in data:
                csv_out.writerow(row)

        return len(data)

    def load_mentions(self, data):

        length = self.update_mentions_data(data)

        if length > 0:
            result = self.session.run('''
                        USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS
                        FROM 'file:/mentions.csv' AS row
                        MATCH (n:Coin {ticker:row.ticker})
                        MATCH (m:Person {username:row.username})
                        MERGE (m)-[r:CALLOUT {weight:toFloat(row.weight)}]->(n)
                        return count(r)
                    ''')
            return [r for r in result]

    def create_coinMentions_view(self):

        self.session.run('''
            CALL gds.graph.create(
                'coinMentions',
                ['Person', 'Coin'],
                "CALLOUT",
                {
                    relationshipProperties: 'weight'
                }
            )
                         ''')

    def drop_coinMentions_view(self):
        self.session.run('''
            CALL gds.graph.drop('coinMentions') YIELD graphName;
                        ''')

    def page_rank(self):

        page_rank_result = self.session.run('''
            CALL gds.pageRank.stream('coinMentions', {
            maxIterations: 20,
            dampingFactor: 0.85,
            relationshipWeightProperty: 'weight'
            })
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).name AS name, score
            ORDER BY score DESC, name ASC
                        ''')

        return page_rank_result

    def clear_db(self):
        self.session.run("MATCH (n) DETACH DELETE (n)")
        print("deleted database")

    def clear_relations(self, label):
        if label:
            self.session.run("MATCH ()-[r:"+label+"]-() DELETE r")
        else:
            self.session.run("MATCH ()-[r]-() DELETE r")
        print("Deleted relations")

    def get_nodes(self, label=None):
        if label:
            nodes = self.session.run("MATCH (n:"+label+") RETURN (n)")
        else:
            nodes = self.session.run("MATCH (n) RETURN (n)")

        return [record["n"] for record in nodes]

    def get_relations(self, label=None):
        if label:
            relations = self.session.run("MATCH (n)-[r:"+label+"]-> (m) RETURN n, r, m")
        else:
            relations = self.session.run("MATCH (n)-[r]-> (m) RETURN n, r, m")

        return [record["r"] for record in relations]

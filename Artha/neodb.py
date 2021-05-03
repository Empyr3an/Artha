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
        # print("Updated coins")

    def update_follows_csv(self, data, location=None):
        if not location:
            location = self.path+'follows.csv'

        with open(location, 'w+') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(["from", "id", "name", "username", "weight"])
            for row in data:
                csv_out.writerow(row)

        return len(data)

    def load_follow_nodes(self, data):
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
            # print("loaded People")
            # create all edges

            return follow_result
        else:
            return -1

    # TODO add weight for number of people a person follows
    def load_follow_relations(self, data):
        length = self.update_follows_csv(data)

        if length > 0:
            node_result = self.session.run('''
                        USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS
                        FROM 'file:/follows.csv' AS row
                        MATCH (m:Person {username:row.from})
                        MATCH (n:Person {id:row.id})
                        MERGE (m)-[r:FOLLOWS {weight:toFloat(row.weight)}]->(n)
                        return count(r)
                    ''')
            # print("loaded relations")
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
                        MATCH (m:Person {username:row.username})
                        MERGE (n:Coin {ticker:row.ticker})
                        MERGE (m)-[r:CALLOUT {weight:toFloat(row.weight)}]->(n)
                        return count(r)
                    ''')
            return [r for r in result]

    def create_coinMentions_view(self):

        result = self.session.run('''
            CALL gds.graph.create(
                'mentions',
                {Person: {label: "Person"},Coin: {label: "Coin"}},
                {CALLOUT: {type: 'CALLOUT', orientation: 'UNDIRECTED'},
                FOLLOWS: {type: 'FOLLOWS', orientation: 'NATURAL'}
                },
                { relationshipProperties: 'weight'}
            )
            YIELD graphName, nodeCount, relationshipCount
            ''')
        return [r for r in result]

    def drop_coinMentions_view(self):
        self.session.run('''
            CALL gds.graph.drop('mentions') YIELD graphName;
                        ''')

# TODO MAKE VARIABLE DAMPENING FACTOR
    def pagerank(self, auto):

        exists = self.session.run("CALL gds.graph.exists('mentions') YIELD exists")
        if [r["exists"] for r in exists][0]:
            self.drop_coinMentions_view()

        self.create_coinMentions_view()

        page_rank_result = self.session.run('''
            CALL gds.pageRank.stream('mentions', {
            maxIterations: 20,
            dampingFactor: 0.85,
            relationshipWeightProperty: 'weight'
            })
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).ticker AS ticker, score
            ORDER BY score DESC, ticker ASC
                        ''')

        return [r for r in page_rank_result]

    def pagerank_scores(self, auto=False):
        
        return [[i["ticker"], i["score"]]
                for i in self.pagerank(auto)
                if i["score"] > .1500001 and i["ticker"]]

    def clear_nodes(self, label=None):
        if label:
            self.session.run("MATCH (n:"+label+") DETACH DELETE (n)")
        else:
            self.session.run("MATCH (n) DETACH DELETE (n)")
        # print("deleted nodes")

    def clear_relations(self, label):
        if label:
            self.session.run("MATCH ()-[r:"+label+"]-() DELETE r")
        else:
            self.session.run("MATCH ()-[r]-() DELETE r")
        # print("Deleted relations")

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

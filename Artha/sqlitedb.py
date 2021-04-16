
class TSQLite:

    @classmethod
    def db_name(cls, conn):
        return conn.cursor() \
                   .execute("PRAGMA database_list") \
                   .fetchall()[0][2] \
                   .split("/")[-1][1:-3]

    # takes in follows data(id, name, username) data and makes table
    @classmethod
    def follow_table(cls, conn, following):
        username = cls.db_name(conn)
        try:
            with conn:
                if "following" in cls.current_tables(conn):
                    conn.cursor().execute("DROP TABLE following")

                conn.cursor().execute("\
                    CREATE TABLE following\
                    (id str, name str, username str)")

                for user in following:
                    conn.cursor().execute("INSERT INTO following\
                                           VALUES(:id, \
                                                  :name, \
                                                  :username)",
                                          user)
                print("created follow table for ", username)
        except Exception as e:
            print(following[:10])
            raise e

    # takes in tweet json data, creates table
    # @classmethod
    # def tweet_table(cls, conn, tweets):
    #     username = cls.db_name(conn)

    #     try:
    #         with conn:
    #     except Exception as e:
    #         print(tweets[0])
    #         raise e

    @classmethod
    def drop_table(cls, conn, name):
        with conn:
            conn.cursor().execute("DROP TABLE u"+name)

    @classmethod
    def current_tables(cls, conn):
        tables = [v[0] for v in
                  conn.cursor().execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table';
                  """).fetchall()
                  if v[0] != "sqlite_sequence"]

        return tables


class TSQLite:
    # TODO Modify follow table to list usernames as well as IDs

    @classmethod
    def premaid_follow_table(cls, conn, following):
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
        except Exception as e:
            print(following[:10])
            raise e

    @classmethod
    def create_follow_table(cls, conn, twitter, username):
        print('creating table for', username)
        following = [str(id) for id in twitter.get_following1(username)]

        try:
            with conn:
                if "following" in cls.current_tables(conn):
                    conn.cursor().execute("DROP TABLE following")

                conn.cursor().execute("\
                    CREATE TABLE following\
                    (account_id str)")

                for user_id in following:
                    conn.cursor().execute("INSERT INTO following\
                                           VALUES(:account_id)", [user_id])
        except Exception as e:
            print(following[:10])
            raise e
        # print("updating mongo")
        # TMongo.update_account_data(twitter, username, following)

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

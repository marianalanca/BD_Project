import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """ CREATE TABLE auction_user (
            username text UNIQUE NOT NULL,
            password text NOT NULL,
            PRIMARY KEY(username)
        )
        """,
        """ CREATE TABLE auction (
            title		 text NOT NULL,
            description		 text NOT NULL,
            id			 text UNIQUE NOT NULL,
            finish_date		 DATE,
            biddding		 DOUBLE PRECISION NOT NULL,
            auction_user_username text NOT NULL,
            PRIMARY KEY(id)
        )
        """,
        """ CREATE TABLE bidding (
            price		 DOUBLE PRECISION NOT NULL,
            finish_date		 DATE,
            auction_id		 text,
            auction_user_username text,
            PRIMARY KEY(auction_id,auction_user_username)
        )
        """,
        """CREATE TABLE bidding_msg (
            id_			 text,
            content		 text,
            auction_user_username text NOT NULL,
            auction_id		 text NOT NULL,
            PRIMARY KEY(id_)
        )
        """,
        """ CREATE TABLE mural_msg (
            id			 text,
            content		 text,
            finish_date		 DATE,
            auction_id		 text NOT NULL,
            auction_user_username text NOT NULL,
            PRIMARY KEY(id)
        )
        """,
        """ CREATE TABLE history (
            change_date	 DATE NOT NULL,
            old_title	 text,
            old_description text,
            auction_id	 text,
            PRIMARY KEY(auction_id)
        )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
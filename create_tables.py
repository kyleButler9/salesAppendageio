import psycopg2
from config import config


def create_tables():
    """ create tables in the 'distribution' database """
    commands = (
        """
        CREATE TABLE orgs (
            org_id SERIAL PRIMARY KEY,
            org_name VARCHAR(255),
            address VARCHAR(255)
        )
        """,
        """
        CREATE TABLE pids (
            device_id SERIAL PRIMARY KEY,
            pid VARCHAR(20),
            category VARCHAR(20),
            quality VARCHAR(20),
            pallet INTEGER,
            org_id INTEGER NOT NULL,
            FOREIGN KEY (org_id)
                REFERENCES orgs (org_id)
                ON UPDATE CASCADE
        )
        """
    )
    conn = None
    try:
        # read the connection parameters
        params = config(ini_section='local_sales_appendage')
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

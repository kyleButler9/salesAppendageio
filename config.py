from configparser import ConfigParser


def config(ini_file='database.ini', ini_section='local_distribution_sheet'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(ini_file)

    # get section, default to postgresql
    db = {}
    if parser.has_section(ini_section):
        params = parser.items(ini_section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(ini_file_section, filename))

    return db
    
class dbOps:
    def __init__(self,ini_section):
        self.connectToDB(ini_section)
    def connectToDB(self,ini_section):
        try:
            # read database configuration
            params = config(ini_section=ini_section)
            # connect to the PostgreSQL database
            self.conn = psycopg2.connect(**params)
            # create a new cursor
            self.cur = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return self

    def queryDB(self,query):
        return pd.io.sql.read_sql_query(query,self.conn)
    def insertValues(self,*args):
        #broke func
        try:
            sql = \
            """
            INSERT INTO {}
            VALUES{}
            RETURNING {};
            """
            self.cur.execute(sql.format(tableName), (sn,pk,))
            self.conn.commit()
            return self.cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass

import tkinter as tk
import psycopg2
from config import config
from queryGoogleSheets import QueryOverview_cColumn
import pandas as pd
import socket
from os import path
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
    def insertValues(self,tableName,sn,pk):
        try:
            sql = \
            """
            INSERT INTO {}(sn,pk)
            VALUES(%s,%s)
            RETURNING device_id;
            """
            self.cur.execute(sql.format(tableName), (sn,pk,))
            self.conn.commit()
            return self.cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass
class GUI(dbOps):
    def __init__(self,**kwargs):
        dbOps.__init__(self,kwargs['ini_section'])
        self.tableName = kwargs['table']
        self.zebraIP = kwargs['zebraIP']
        self.root = tk.Tk()
        self.root.geometry("500x150")
        self.root.title('Sales Process Appendage')
        self.CreateFields()
        self.UpdateOrgs(QueryOverview_cColumn())
        self.pallet.insert(0,self.GetLastPalletNumber())
        self.Start()
    def UpdateOrgs(self,sheetYield):
        sql1 = \
        """
        SELECT org_name
        FROM orgs;
        """
        self.cur.execute(sql1)
        inAlready=[]
        for item in self.cur.fetchall():
            inAlready.append(item[0])
        newOrgs = set(sheetYield) - set(inAlready)
        sql2 = \
        """
        INSERT INTO orgs(org_name)
        VALUES(%s);
        """
        for org in newOrgs:
            self.cur.execute(sql2,(org,))
        self.conn.commit()
    def CreateFields(self):
        self.dest = tk.StringVar()
        self.dest.set('select a value:')
        self.destDropdown = tk.OptionMenu(self.root,self.dest,*QueryOverview_cColumn())
        self.palletLabel = tk.Label(text="Pallet ID #")
        self.pidLabel = tk.Label(text="PID")
        self.catLabel = tk.Label(text="Category")
        self.qualityLabel = tk.Label(text="Quality")

        self.quality = tk.Entry(fg="black", bg="white", width=15)
        self.cat = tk.Entry(fg="black", bg="white", width=15)
        self.pid = tk.Entry(fg="black", bg="white", width=15)
        self.pallet = tk.Entry(fg="black", bg="white", width=15)
        self.insertAndPrint = tk.Button(
            text="Insert PID and Print",
            width=15,
            height=2,
            bg="blue",
            fg="yellow",
        )
        self.justInsert = tk.Button(
            text="Just Insert PID",
            width=15,
            height=2,
            bg="blue",
            fg="yellow",
        )
        self.exportCSV = tk.Button(
            text="Export CSV for Dest",
            width=15,
            height=2,
            bg="blue",
            fg="yellow",
        )
        self.insertAndPrint.bind('<Button-1>', self.InsertAndPrint)
        self.justInsert.bind('<Button-1>', self.JustInsert)
        self.exportCSV.bind('<Button-1>', self.ExportCSV)
        self.root.bind('<Return>',self.InsertAndPrint)
        self.destDropdown.grid(row=0,column=0,columnspan=1)
        self.palletLabel.grid(row=2,column=2)
        self.pallet.grid(row=2,column=3)
        self.pidLabel.grid(row=2,column=0)
        self.pid.grid(row=2,column=1)
        self.catLabel.grid(row=1,column=2)
        self.cat.grid(row=1,column=3)
        self.qualityLabel.grid(row=1,column=0)
        self.quality.grid(row=1,column=1)
        self.insertAndPrint.grid(row=3,column=0)
        self.justInsert.grid(row=3,column=1)
        self.exportCSV.grid(row=3,column=3)
    def ExportCSV(self,event):
        try:
            sql = \
            """
            SELECT pid,pallet,quality,Category,org_name
            FROM pids
            INNER JOIN orgs ON pids.org_id = orgs.org_id
            WHERE org_name = '{}'
            """
            dest = self.dest.get()
            df = self.queryDB(sql.format(dest))
            file = open(path.join(path.expanduser('~'),
                'Downloads\{}.csv'.format(dest[:6])),'w')
            df['pallets'] = 'MD ' + str(df['pallet'].values[0])
            df.drop(columns=['pallet'])
            file.write(df.to_csv(index=False))
            file.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass


    def InsertAndPrint(self,event):
        try:
            sql = \
                """
                INSERT INTO pids(pid,category,quality,pallet,org_id)
                VALUES (
                    %s,%s,%s,%s,
                    (SELECT org_id FROM orgs WHERE org_name = %s)
                    )
                RETURNING device_id;
                """
            pallet = self.pallet.get()
            pid = self.pid.get()
            cat = self.cat.get()
            quality = self.quality.get()
            dest = self.dest.get()

            self.pid.delete(0,15)
            templateFile = open('template.prn','r')
            file = open('out.prn','w')
            template = templateFile.read()
            zpl = template.format(str(quality),
                str(cat),
                str(pid))
            self.SendToZebra(zpl)
            file.write(zpl)
            templateFile.close()
            file.close()


            self.cur.execute(sql,(pid,cat,quality,pallet,dest))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass
    def JustInsert(self,event):
        try:
            sql = \
                """
                INSERT INTO pids(pid,category,quality,pallet,org_id)
                VALUES (
                    %s,%s,%s,%s,(SELECT org_id FROM orgs WHERE org_name = %s))
                RETURNING device_id;
                """
            pallet = self.pallet.get()
            pid = self.pid.get()
            cat = self.cat.get()
            quality = self.quality.get()
            dest = self.dest.get()

            self.pid.delete(0,15)

            self.cur.execute(sql,(pid,cat,quality,pallet,dest))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass
    def SendToZebra(self,zpl):
        mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = self.zebraIP
        port = 9100
        try:
            mysocket.connect((host, port)) #connecting to host
        	#mysocket.send(b"^XA^A0N,50,50^FO50,50^FDSocket Test^FS^XZ")#using bytes
            mysocket.send('${' + zpl + '}$')
            mysocket.close() #closing connection
        except:
        	print("Error with the connection at zebra IP: " + self.zebraIP )
        finally:
            pass
    def GetLastPalletNumber(self):
        try:
            sql = \
            """
            SELECT MAX(pallet)
            FROM pids;
            """
            self.cur.execute(sql)
            pallet = self.cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            pallet = 'error'
        finally:
            return str(pallet)

    def Start(self):
        self.root.mainloop()
    def CloseGUI(self,event):
        self.root.destroy()
if __name__ == "__main__":
    gui = GUI(ini_section='local_sales_appendage',
            table='pids',
            zebraIP="10.80.209.106")

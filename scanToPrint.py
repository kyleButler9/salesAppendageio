import tkinter as tk
import psycopg2
from config import config
import pyperclip
import pandas as pd
import socket
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
        self.root.geometry("500x100")
        self.root.title('Sales Process Appendage')
        self.CreateFields()
        self.pallet.insert(0,self.GetLastPalletNumber())
        self.Start()
    def CreateFields(self):
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
        self.insertAndPrint.bind('<Button-1>', self.InsertAndPrint)
        self.justInsert.bind('<Button-1>', self.JustInsert)
        self.root.bind('<Return>',self.insertAndPrint)

        self.palletLabel.grid(row=1,column=2)
        self.pallet.grid(row=1,column=3)
        self.pidLabel.grid(row=1,column=0)
        self.pid.grid(row=1,column=1)
        self.catLabel.grid(row=0,column=2)
        self.cat.grid(row=0,column=3)
        self.qualityLabel.grid(row=0,column=0)
        self.quality.grid(row=0,column=1)
        self.insertAndPrint.grid(row=2,column=0)
        self.justInsert.grid(row=2,column=2)

    def InsertAndPrint(self,event):
        try:
            sql = \
                """
                INSERT INTO pids(pid,category,quality,pallet)
                VALUES (%s,%s,%s,%s)
                RETURNING device_id;
                """
            pallet = self.pallet.get()
            pid = self.pid.get()
            cat = self.cat.get()
            quality = self.quality.get()

            self.pid.delete(0,15)
            templateFile = open('template.prn','r')
            file = open('out.prn','w')
            template = templateFile.read()
            zpl = template.format(str(quality),str(cat),str(pid))
            self.SendToZebra(zpl)
            file.write(zpl)
            templateFile.close()
            file.close()


            self.cur.execute(sql,(pid,cat,quality,pallet))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            pass
    def JustInsert(self,event):
        try:
            sql = \
                """
                INSERT INTO pids(pid,category,quality,pallet)
                VALUES (%s,%s,%s,%s)
                RETURNING device_id;
                """
            pallet = self.pallet.get()
            pid = self.pid.get()
            cat = self.cat.get()
            quality = self.quality.get()

            self.pid.delete(0,15)

            self.cur.execute(sql,(pid,cat,quality,pallet))
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

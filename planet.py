import csv
import mysql.connector
from tabulate import *
def create_table():
    with open('planets.csv','r',encoding='utf8') as f:
        reader=csv.reader(f)
        heading=next(reader)
        data=list(reader)
        columns={}
        for i in data:
            for index,value in enumerate(i):
                dataheader=heading[index]
                if value.isdigit():
                    datatype='INT'
                    try:
                        float(value)
                        datatype ='FLOAT'
                    except:
                        pass
                else:
                    datatype='VARCHAR(255)'
                    columns[dataheader]=datatype
            query1='CREATE TABLE %s IF NOT EXIST('%['Planets']
            query2=','.join([f"{dataheader} {datatype}" for dataheader,datatype in columns.items()])
            query3=')'
            query = query1 + query2 + query3
            conobj=mysql.connector(host='localhost',user='root',passswd='groot',database='stars')
            curry=conobj.cursor()
            curry.execute(query)
            curry.execute('desc planets')
            re=curry.fetchall()
            headers=[desc[0] for desc in curry.description]
            print(tabulate(re,headers,tablefmt='grid'))
create_table()

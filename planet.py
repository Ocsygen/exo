import csv
import mysql.connector
from tabulate import tabulate

conobj = mysql.connector.connect(host='localhost', user='root', passwd='groot', database='stars') 
curry = conobj.cursor() 
headers = [] 

def isempty_table():
    global curry
    count_query = "SELECT COUNT(*) FROM planets"
    curry.execute(count_query)
    count = curry.fetchone()[0]
    return count == 0

def create_table():
    global conobj, curry, headers
    with open('planets.csv', 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        heading = next(reader)
        data = list(reader)
        columns = {}

        for i in data:
            for index, value in enumerate(i):
                dataheader = heading[index]
                if value.isdigit():
                    datatype = 'INT'
                    try:
                        float(value)
                        datatype = 'FLOAT'
                    except:
                        pass
                else:
                    datatype = 'VARCHAR(255)'
                if dataheader not in columns:
                    columns[dataheader] = datatype

        query1 = 'CREATE TABLE IF NOT EXISTS Planets ('
        query2 = ', '.join([f"{dataheader} {datatype}" for dataheader, datatype in columns.items()])
        query3 = ')'
        query = query1 + query2 + query3

        curry.execute(query)
        print("Table created successfully.")

            
        f.seek(0)
        next(reader) 
        for row in reader:
            curry.execute("INSERT INTO Planets VALUES ('%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s')", row)

        conobj.commit()
        print("Data inserted successfully.")

        '''curry.execute('DESC Planets')
        re = curry.fetchall()
        headers = [desc[0] for desc in curry.description]'''


def view_table():
    global curry, headers
    view_query = "SELECT * FROM planets"
    curry.execute(view_query) 
    view_forloopvar = curry.fetchall()
    headers = [desc[0] for desc in curry.description]
    if isempty_table(): 
        print("The Table is Empty!") 
    else: 
        print(tabulate(view_forloopvar, headers, tablefmt='grid'))

create_table()
view_table()
curry.close
conobj.close


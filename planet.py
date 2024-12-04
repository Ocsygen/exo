import csv
import mysql.connector
from tabulate import tabulate
import time #use this in our error exception blocks(check sort and update fucntion
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
            curry.execute("INSERT INTO Planets VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row)

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

def delete_table():
    global conobj, curry
    while True:
        print("""
Choose an option:
1. Delete the entire table
2. Delete some specific records
3. Exit the command
        """)
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            try:
                delete_query = "DROP TABLE IF EXISTS planets"
                curry.execute(delete_query)
                delete_confirmation = input("Are you sure you want to delete? y/Y or n/N? ")
                if delete_confirmation.lower() == 'y':
                    conobj.commit()
                    print("The entire table has been deleted.")
                elif delete_confirmation.lower() == 'n':
                    conobj.rollback()
                    print("Operation cancelled.")
                else:
                    print("Invalid option. Operation cancelled.")
            except mysql.connector.Error:
                print("Error - Invalid Connection")
            break

        elif choice == '2':
            try:
                column_name = input("Enter the column name for the condition: ")
                value = input("Enter the value for the condition: ")
                deleterecords_query = "DELETE FROM planets WHERE {} = %s".format(column_name)
                curry.execute(deleterecords_query, (value,))
                delete_confirmation = input("Are you sure you want to delete? y/Y or n/N? ")
                if delete_confirmation.lower() == 'y':
                    conobj.commit()
                    print(f"Records where {column_name} = '{value}' have been deleted.")
                elif delete_confirmation.lower() == 'n':
                    conobj.rollback()
                    print("Operation cancelled.")
                else:
                    print("Invalid option. Operation cancelled.")
            except mysql.connector.Error:
                print("Error - Invalid Connection")
            break

        elif choice == '3':
            print("Over and Out")
            break

        else:
            print("Invalid choice. Please try again.")


create_table()
view_table()
def sort():
    print('HOW DO YOU WANNA SORT THE TABLE? --> 1.Ascending || 2.Descending')
    i=int(input('Pick the no. correspinding to your choice:'))
    r=[]
    k=1
    for i in headers:
        r.append((k,i))
        k+=1
    column_tuple=tuple(r)
    try:
        if i == 1:
            print(tabulate(column_tuple,['Col_no','Col_name'],tablefmt='grid'))
            print('enter the corresponding no. of the column you want to sort by')
            g=int(input())
            sort_query='SELECT * FROM PLANETS ORDER BY %s'%(r[g-1][1])
            curry.execute(sort_query)
            print(tabulate(curry.fetchall(),headers=headers,tablefmt='grid'))
            print('Sorting has been successful')
        elif i == 2:
            print(tabulate(tuple(r),['Col_no','Col_name'],tablefmt='grid'))
            print('enter the corresponding no. of the column you want to sort by')
            g=int(input())
            sort_query='SELECT * FROM PLANETS ORDER BY %s DESC'%(r[g-1][1])
            curry.execute(sort_query)
            print(tabulate(curry.fetchall(),headers=headers,tablefmt='grid'))
            print('Sorting has been successful')
        else:
            print('INVALID INPUT')#add break statement in loop(won't work here)
    except:
        print('Sorting failed')
        print('An Error Has Occured')
        for i in range(3,0,-1):
            print('Breaking the loop in:',str(i),end='\r')
            time.sleep(1)
        print('The Loop has been restarted')
        
def update():
    r=[]
    k=1
    for i in headers:
        r.append((k,i))
        k+=1
    column_tuple=tuple(r)
    print(tabulate(column_tuple,headers=['Col_no','Col_name'],tablefmt='grid'))
    print('CHOOSE THE NUMBER CORRESPONDING TO THE COLUMN YOU WANT TO UPDATE:')
    o=int(input('-->'))
    planet_query='select Planet_name from planets'
    curry.execute(planet_query)
    planets=[]
    planets_2=[]
    sno=1
    for i in curry.fetchall():
        planets.append(i)
        planets_2.append((sno,i))
        sno+=1
    print(tabulate(tuple(planets_2),headers=['Planet no.','Planetname'],tablefmt='grid'))   
    try:
        Planet_name_input=int(input('enter the number corresponding to the planet in the table above'))
        Planet_name=planets[(Planet_name_input)-1][0]
        new_value=input('enter the new value that you want to input into the table')
        update_query="UPDATE PLANETS SET %s = %s where Planet_name='%s'"%(r[o-1][1],new_value,Planet_name)
        curry.execute(update_query)
        print('Are you sure about the changes your making?(y/n)')
        i=str(input())
        if i.upper()=='Y':
            conobj.commit()
            print('Table Updated Successfully')
        else:
            conobj.rollback()
            print('Table updation Aborted')
    except:
        print('Updation failed')
        print('An Error Has Occured')
        for i in range(3,0,-1):
            print('Breaking the loop in:',str(i),end='\r')
            time.sleep(1)
        print('The Loop has been restarted')
curry.close
conobj.close


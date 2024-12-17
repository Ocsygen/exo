import csv
import mysql.connector
from tabulate import tabulate
import time
import pickle

conobj = mysql.connector.connect(host='localhost', user='root', passwd='groot', database='stars')
curry = conobj.cursor()

headers = [] 
userid = None 
passwd = None
userid = []
passwd = []

def createloginid_table():
    try:
        curry.execute("""
        CREATE TABLE IF NOT EXISTS loginid (
            name VARCHAR(40),
            userid VARCHAR(20) PRIMARY KEY,
            passwd VARCHAR(20)
        )
        """)
        conobj.commit()
    except:
        print("An error occurred while creating the loginid table.")

createloginid_table()

def signup():
    global userid, passwd
    try:
        name = input("Enter your name: ")
        userid = input("Enter your userid: ")
        passwd = input("Enter your password: ")
        passwdverify = input("Enter your password again: ")
        if passwdverify == passwd:
            signup_query = "INSERT INTO loginid (name, userid, passwd) VALUES ('{}', '{}', '{}')".format(name, userid, passwd)
            curry.execute(signup_query)
            conobj.commit()
            print("Sign Up was successful. Please log in.")
        else:
            print("Passwords do not match. Please try again.")
            signup()
    except:
        print("An error occurred during signup.")

def login():
    attempts = 0
    idlist = []
    passwdlist = []

    try:
        curry.execute("SELECT * FROM loginid")
        loginfetch = curry.fetchall()
        for i in loginfetch:
            idlist.append(i[1])
            passwdlist.append(i[2])

        userid = input("Enter the userid: ")
        if userid.lower() in idlist:
            while attempts < 3:
                passwd = input("Enter the password: ")
                if passwd == passwdlist[idlist.index(userid.lower())]:
                    print("Login Successful")
                    return True
                else:
                    attempts += 1
                    print("Incorrect password. Try again.")
            print("Too many failed attempts. Please wait for 1 minute.")
            time.sleep(60)
            return login()
        else:
            print("User ID not found.")
    except:
        print("An error occurred during login.")
    return False

def main():
    acc_check = input("Do you have a registered account? y/n: ")
    if acc_check.lower() == "n":
        signup()
    if acc_check.lower() == "y":
        if login():
            print("Access granted to the rest of the commands.")
        else:
            print("Login failed. Redirecting to signup.")
            signup()

main() 

def isempty_table():
    global curry
    try:
        count_query = "SELECT COUNT(*) FROM planets"
        curry.execute(count_query)
        count = curry.fetchone()[0]
        return count == 0
    except:
        print("An error occurred while checking if the table is empty.")
        return True

def create_table():
    global conobj, curry, headers
    try:
        with open('planets.csv', 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            data = list(reader)
            columns = {}

            for i in data:
                for index, value in enumerate(i):
                    dataheader = headers[index]
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
    except:
        print("An error occurred while creating the table and inserting data.")

def view_table():
    global curry, headers
    try:
        rows_per_page = int(input("Enter the number of rows per page: "))
        page = 0

        while True:
            offset = page * rows_per_page
            view_query = "SELECT * FROM planets LIMIT {} OFFSET {}".format(rows_per_page, offset)
            curry.execute(view_query)
            view_forloopvar = curry.fetchall()
            headers = [desc[0] for desc in curry.description]

            print(tabulate(view_forloopvar, headers, tablefmt='grid'))

            if isempty_table():
                print("The Table is Empty!")
                break

            next_todo = input("Enter 'n' for next page, 'p' for previous page, or 'quit' to quit: ")
            if next_todo.lower() == 'n':
                page += 1
            elif next_todo.lower() == 'p' and page > 0:
                page -= 1
            elif next_todo.lower() == 'quit':
                break
            else:
                print("Invalid input - Exiting")
                break
    except:
        print("An error occurred while viewing the table.")


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
            except:
                print("An error occurred while deleting the table.")
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
            except:
                print("An error occurred while deleting specific records.")
            break

        elif choice == '3':
            print("Over and Out")
            break

        else:
            print("Invalid choice. Please try again.")

def sort_table():
    global curry, headers
    try:
        print('HOW DO YOU WANNA SORT THE TABLE? --> 1. Ascending || 2. Descending')
        i = int(input('Pick the no. corresponding to your choice: '))
        r = []
        k = 1
        for col in headers:
            r.append((k, col))
            k += 1
        column_tuple = tuple(r)

        if i == 1:
            print(tabulate(column_tuple, ['Col_no', 'Col_name'], tablefmt='grid'))
            print('Enter the corresponding no. of the column you want to sort by:')
            g = int(input())
            sort_query = 'SELECT * FROM planets ORDER BY {}'.format(r[g - 1][1])
            curry.execute(sort_query)
            print(tabulate(curry.fetchall(), headers=headers, tablefmt='grid'))
            print('Sorting has been successful')
        elif i == 2:
            print(tabulate(column_tuple, ['Col_no', 'Col_name'], tablefmt='grid'))
            print('Enter the corresponding no. of the column you want to sort by:')
            g = int(input())
            sort_query = 'SELECT * FROM planets ORDER BY {} DESC'.format(r[g - 1][1])
            curry.execute(sort_query)
            print(tabulate(curry.fetchall(), headers=headers, tablefmt='grid'))
            print('Sorting has been successful')
        else:
            print('INVALID INPUT')
        elif i == 3:
        print(tabulate(column_tuple, ['Col_no', 'Col_name'], tablefmt='grid'))
        print('Enter the corresponding no. of the column you want to join the table by:')
        g=int(input())
        no_records=int(input('enter the no. of records you wish to see per page '))
        page=0
        while True:
            try:
                offset = page * no_records
                join_view_query = "SELECT * FROM planets common join planets on planets.{}=planets.{} LIMIT {} OFFSET {}".format(r[g-1][1],r[g-1][1],no_records, offset)
                curry.execute(join_view_query)
                view_forloopvar = curry.fetchall()
                headers = [desc[0] for desc in curry.description]
                print(tabulate(view_forloopvar, headers, tablefmt='grid'))
                if isempty_table():
                    print("The Table is Empty!")
                    break
                next_todo = input("Enter 'n' for next page, 'p' for previous page, or 'quit' to quit: ")
                if next_todo.lower() == 'n':
                    page += 1
                elif next_todo.lower() == 'p' and page > 0:
                    page -= 1
                elif next_todo.lower() == 'quit':
                    break
                else:
                    print("Invalid input - Exiting")
                    break
            except MemoryError:
                print('The data size was too huge for python to parse through')
                break
    elif i == 4:
        print('''Choose the no. corresponding to aggregate function to group by with
        --->|1. AVERAGE |
        --->|2. COUNT |
        --->|3. SUM  |
        --->|4. MIN  |
        --->|5. MAX  |''')
        group_by_input=int(input())
        r = []
        k = 1
        for col in headers:
            r.append((k, col))
            k += 1
        column_tuple = tuple(r)
        if group_by_input==1:
            print(tabulate(r,['Col_name','Col_datatype'],tablefmt='grid'))
            print('enter the no. corresponding to the column you want to apply the aggregate function to ')
            column_no_2=int(input())
            print('enter the corresponding no. of the second column that you wanna group the data by')
            column_no_1=int(input())
            group_query = "SELECT {},AVG({}) from planets group by {}".format(r[column_no_1-1][1],r[column_no_2-1][1],r[column_no_1-1][1])
            curry.execute(group_query)
            
            print(tabulate(curry.fetchall(),[desc[0] for desc in curry.description],tablefmt='grid'))
        elif group_by_input==2:
            print(tabulate(r,['Col_name','Col_datatype'],tablefmt='grid'))
            print('enter the no. corresponding to the column you want to apply the aggregate function to ')
            column_no_2=int(input())
            print('enter the corresponding column of the second column that you wanna group the data by')
            column_no_1=int(input())
            group_query = "SELECT {},COUNT({}) from planets group by {}".format(r[column_no_1-1][1],r[column_no_2-1][1],r[column_no_1-1][1])
            curry.execute(group_query)
            print(tabulate(curry.fetchall(),[desc[0] for desc in curry.description],tablefmt='grid'))
        elif group_by_input==3:
            print(tabulate(r,['Col_name','Col_datatype'],tablefmt='grid'))
            print('enter the no. corresponding to the column you want to apply the aggregate function to ')
            column_no_2=int(input())
            print('enter the corresponding column of the second column that you wanna group the data by')
            column_no_1=int(input())
            group_query = "SELECT {},SUM({}) from planets group by {}".format(r[column_no_1-1][1],r[column_no_2-1][1],r[column_no_1-1][1])
            curry.execute(group_query)
            print(tabulate(curry.fetchall(),[desc[0] for desc in curry.description],tablefmt='grid'))
        elif group_by_input==4:
            print(tabulate(r,['Col_name','Col_datatype'],tablefmt='grid'))
            print('enter the no. corresponding to the column you want to apply the aggregate function to ')
            column_no_2=int(input())
            print('enter the corresponding column of the second column that you wanna group the data by')
            column_no_1=int(input())
            group_query = "SELECT {},MIN({}) from planets group by {}".format(r[column_no_1-1][1],r[column_no_2-1][1],r[column_no_1-1][1])
            curry.execute(group_query)
            print(tabulate(curry.fetchall(),[desc[0] for desc in curry.description],tablefmt='grid'))
        elif group_by_input==5:
            print(tabulate(r,['Col_name','Col_datatype'],tablefmt='grid'))
            print('enter the no. corresponding to the column you want to apply the aggregate function to ')
            column_no_2=int(input())
            print('enter the corresponding column of the second column that you wanna group the data by')
            column_no_1=int(input())
            group_query = "SELECT {},MAX({}) from planets group by {}".format(r[column_no_1-1][1],r[column_no_2-1][1],r[column_no_1-1][1])
            curry.execute(group_query)
            print(tabulate(curry.fetchall(),[desc[0] for desc in curry.description],tablefmt='grid'))
        else:
            print('invalid response')
            for i in range(3,0,-1):
                print('Redirecting to Menu in',str(i),end='\r')
                time.sleep(1)

    except:
        print('Sorting failed')
        print('An error has occurred')
        for i in range(3, 0, -1):
            print('Breaking the loop in:', str(i), end='\r')
            time.sleep(1)
        print('The loop has been restarted')
    

def update_table():
    global curry, conobj, headers
    try:
        r = []
        k = 1
        for i in headers:
            r.append((k, i))
            k += 1
        column_tuple = tuple(r)
        print(tabulate(column_tuple, headers=['Col_no', 'Col_name'], tablefmt='grid'))
        print('CHOOSE THE NUMBER CORRESPONDING TO THE COLUMN YOU WANT TO UPDATE:')
        o = int(input('-->'))
        planet_query = 'SELECT Planet_name FROM planets'
        curry.execute(planet_query)
        planets = []
        planets_2 = []
        sno = 1
        for i in curry.fetchall():
            planets.append(i)
            planets_2.append((sno, i))
            sno += 1
        print(tabulate(tuple(planets_2), headers=['Planet no.', 'Planetname'], tablefmt='grid'))
        Planet_name_input = int(input('Enter the number corresponding to the planet in the table above: '))
        Planet_name = planets[(Planet_name_input) - 1][0]
        new_value = input('Enter the new value that you want to input into the table: ')
        update_query = "UPDATE PLANETS SET {} = '{}' WHERE Planet_name='{}'".format(r[o - 1][1], new_value, Planet_name)
        curry.execute(update_query)
        print('Are you sure about the changes you are making? (y/n)')
        i = str(input())
        if i.upper() == 'Y':
            conobj.commit()
            print('Table Updated Successfully')
        else:
            conobj.rollback()
            print('Table updation Aborted')
    except:
        print("An error occurred while updating the table.")
        for i in range(3, 0, -1):
            print('Breaking the loop in:', str(i), end='\r')
            time.sleep(1)
        print('The Loop has been restarted')


def export_to_csv():
    try:
        curry.execute("SELECT * FROM planets")
        records = curry.fetchall()
        headers = [desc[0] for desc in curry.description]
        with open('planets_exportedfile.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(records)
        print("Table exported to planets_exportedfile.csv successfully.")
    except:
        print("An error occurred while exporting to CSV.")

def export_to_binary():
    try:
        curry.execute("SELECT * FROM planets")
        rows = curry.fetchall()
        with open('planets_exportedfile.txt', 'wb') as f:
            pickle.dump(rows, f)
        print("Table exported to planets_exportedfile.txt successfully.")
    except:
        print("An error occurred while exporting to binary.")


def filter_and_search_table():
    try:
        curry.execute("SELECT * FROM planets LIMIT 1")
        headers = [desc[0] for desc in curry.description]
    except:
        print("An error occurred while retrieving column names.")

    def paginated(query):
        try:
            rows_per_page = int(input("Enter the number of rows per page: "))
            page = 0

            while True:
                offset = page * rows_per_page
                paginated_query = "{} LIMIT {} OFFSET {}".format(query, rows_per_page, offset)
                curry.execute(paginated_query)
                results = curry.fetchall()

                print(tabulate(results, headers, tablefmt='grid'))

                next_todo = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").lower()
                if next_todo == 'n':
                    page += 1
                elif next_todo == 'p' and page > 0:
                    page -= 1
                elif next_todo == 'q':
                    break
                else:
                    print("Invalid input. Exiting.")
                    break
        except:
            print("An error occurred while paginating the results.")

    def aggregate(filtered_query):
        while True:
            print("""
            Choose an aggregate function:
            1. Sum
            2. Maximum
            3. Minimum
            4. Average
            5. Count 
            6. Exit
            """)
            choice = input("Enter your choice: ")

            try:
                if choice == '1':
                    column = input("Enter the column name for sum: ")
                    agg_query = "SELECT SUM({}) FROM ({})".format(column, filtered_query)
                elif choice == '2':
                    column = input("Enter the column name for maximum: ")
                    agg_query = "SELECT MAX({}) FROM ({})".format(column, filtered_query)
                elif choice == '3':
                    column = input("Enter the column name for minimum: ")
                    agg_query = "SELECT MIN({}) FROM ({})".format(column, filtered_query)
                elif choice == '4':
                    column = input("Enter the column name for average: ")
                    agg_query = "SELECT AVG({}) FROM ({})".format(column, filtered_query)
                elif choice == '5':
                    column = input("Enter the column name for count: ")
                    agg_query = "SELECT COUNT({}) FROM ({})".format(column, filtered_query)
                elif choice == '6':
                    break
                else:
                    print("Invalid choice. Please try again.")
                    continue

                curry.execute(agg_query)
                result = curry.fetchone()
                print("Result: {}".format(result[0]))
            except:
                print("An error occurred while performing the aggregate function.")

    while True:
        print("""
        Choose a filter option:
        1. Range Filtering
        2. Pattern Matching
        3. Is Null
        4. Is Not Null
        5. Greater Than
        6. Less Than
        7. No Filter
        8. Exit
        """)
        choice = input("Enter your choice: ")

        try:
            if choice == '1':
                column = input("Enter the column name for range filtering: ")
                min_value = input("Enter the minimum value: ")
                max_value = input("Enter the maximum value: ")
                filter_query = "SELECT * FROM planets WHERE {} BETWEEN '{}' AND '{}'".format(column, min_value, max_value)
                paginated(filter_query)
                aggregate(filter_query)
            elif choice == '2':
                column = input("Enter the column name for pattern matching: ")
                pattern = input("Enter the pattern (e.g., 'K%'): ")
                filter_query = "SELECT * FROM planets WHERE {} LIKE '{}'".format(column, pattern)
                paginated(filter_query)
                aggregate(filter_query)
            elif choice == '3':
                column = input("Enter the column name for is null: ")
                filter_query = "SELECT * FROM planets WHERE {} IS NULL".format(column)
                paginated(filter_query)
                aggregate(filter_query)
            elif choice == '4':
                column = input("Enter the column name for is not null: ")
                filter_query = "SELECT * FROM planets WHERE {} IS NOT NULL".format(column)
                paginated(filter_query)
                aggregate(filter_query)
            elif choice == '5':
                column = input("Enter the column name for greater than: ")
                value = input("Enter the value: ")
                filter_query = "SELECT * FROM planets WHERE {} > '{}'".format(column, value)
                paginated(filter_query)
                aggregate(filter_query)
            elif choice == '6':
                column = input("Enter the column name for less than: ")
                value = input("Enter the value: ")
                filter_query = "SELECT * FROM planets WHERE {} < '{}'".format(column, value)
                paginated(filter_query)
                aggregate(filter_query)
            elif choice == '7':
                filter_query = "SELECT * FROM planets"
                paginated(filter_query)
                aggregate(filter_query)
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please try again.")
        except:
            print("An error occurred while applying the filter.")


def menu_drive_table():
    while True:
        print("""
        Main Menu:
        1. Create Table
        2. View Table
        3. Update Table
        4. Filter Table
        5. Sort Table
        6. Convert to Another Format
        7. Delete Table
        8. Exit
        """)
        try:
            ch = int(input("Enter your choice: "))
            if ch == 1:
                create_table()
            elif ch == 2:
                view_table()
            elif ch == 3:
                update_table()
            elif ch == 4:
                filter_and_search_table()
            elif ch == 5:
                sort_table()
            elif ch == 6:
                print("""
                Conversion Options:
                1. Convert to CSV
                2. Convert to Binary
                """)
                convertchoice = int(input("Enter your choice: "))
                if convertchoice == 1:
                    export_to_csv()
                elif convertchoice == 2:
                    export_to_binary()
                else:
                    print("Enter an appropriate option.")
            elif ch == 7:
                delete_table()
            elif ch == 8:
                print("Exiting...")
                break
            else:
                print("Enter a valid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

menu_drive_table() 

curry.close
conobj.close 

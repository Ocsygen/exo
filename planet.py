import csv
import mysql.connector
from tabulate import tabulate
import time
import pickle
from art import *

conobj = mysql.connector.connect(host='localhost', user='root', passwd='groot', database='stars')
curry = conobj.cursor()

headers = [] 

print(text2art("WELCOME TO", space=1))
print(text2art("PROJECT SAGAN", space = 1 ))


def explain_table():
    headers = [
        (1, "Planet_Name", "The name of the planet."),
        (2, "SNR_Emission_15_micron", "Signal-to-noise ratio of the planet's emission at 15 microns."),
        (3, "SNR_Emission_5_micron", "Signal-to-noise ratio of the planet's emission at 5 microns."),
        (4, "SNR_Transmission_K_mag", "Signal-to-noise ratio of the planet's transmission in the K magnitude band."),
        (5, "Rp", "Radius of the planet (in Jupiter radii)."),
        (6, "Mp", "Mass of the planet (in Jupiter masses)."),
        (7, "Tday", "Day-side temperature of the planet (in Kelvin)."),
        (8, "Teq", "Equilibrium temperature of the planet (in Kelvin)."),
        (9, "log10g_p", "Logarithm (base 10) of the planet's surface gravity."),
        (10, "Period", "Orbital period of the planet (in days)."),
        (11, "Transit_Duration", "Duration of the planet's transit across its star (in hours)."),
        (12, "K_mag", "K magnitude of the star the planet orbits."),
        (13, "Distance", "Distance to the planet (in parsecs)."),
        (14, "Teff", "Effective temperature of the star the planet orbits (in Kelvin)."),
        (15, "log10g_s", "Logarithm (base 10) of the star's surface gravity."),
        (16, "Transit_Flag", "Indicator of whether the planet transits its star (1 if it does, 0 if it does not)."),
        (17, "Catalog_Name", "Name of the catalog from which the data is sourced.")
    ]
    
    print(tabulate(headers, headers=['Col_no', 'Col_name', 'Description'], tablefmt='grid'))
    

def createloginid_table():
    try:
        curry.execute("""
        CREATE TABLE IF NOT EXISTS logini (
            name VARCHAR(40),
            userid VARCHAR(20) PRIMARY KEY,
            passwd VARCHAR(20)
        )
        """)
        conobj.commit()
    except Exception as e:
        print("An error occurred while creating the loginid table.", str(e))

createloginid_table()

def signup():
    try:
        name = input("Enter your name: ")
        userid = input("Enter your userid: ")
        passwd = input("Enter your password: ")
        passwdverify = input("Enter your password again: ")
        if passwdverify == passwd:
            signup_query = "INSERT INTO logini (name, userid, passwd) VALUES (%s, %s, %s)"
            curry.execute(signup_query, (name, userid, passwd))
            conobj.commit()
            print("Sign Up was successful. Please log in.")
        else:
            print("Passwords do not match. Please try again.")
            signup()
    except Exception as e:
        print("An error occurred during signup.", str(e))

def login():
    attempts = 0
    try:
        curry.execute("SELECT * FROM logini")
        loginfetch = curry.fetchall()
        idlist = [i[1] for i in loginfetch]
        passwdlist = [i[2] for i in loginfetch]

        userid = input("Enter the userid: ")
        if userid in idlist:
            while attempts < 3:
                passwd = input("Enter the password: ")
                if passwd == passwdlist[idlist.index(userid)]:
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
    except Exception as e:
        print("An error occurred during login", str(e))
    return False

def main():
    acc_check = input("Do you have a registered account? y/n: ")
    if acc_check.lower() == "n":
        signup()
        if login():
            print("Access granted to the rest of the commands.")
        else:
            print("Login failed after signup.")
    elif acc_check.lower() == "y":
        if login():
            print("Access granted to the rest of the commands.")
        else:
            print("Login failed. Redirecting to signup.")
            signup()
            if login():
                print("Access granted to the rest of the commands.")
            else:
                print("Login failed after signup.")
    else:
        print("Invalid input. Please enter 'y' or 'n'.")
        main()

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
    global conobj, curry, headers
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
                curry.execute("DESC planets")
                headers = [desc[0] for desc in curry.fetchall()]

                r = []
                k = 1
                for col in headers:
                    r.append((k, col))
                    k += 1
                column_tuple = tuple(r)
                print(tabulate(column_tuple, headers=['Col_no', 'Col_name'], tablefmt='grid'))

                print('Enter the corresponding no. of the column you want to delete records by:')
                col_num = int(input('-->'))
                column_name = r[col_num - 1][1]
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
        # Fetch column names from the table
        curry.execute("DESC planets")
        headers = [desc[0] for desc in curry.fetchall()]

        print('HOW DO YOU WANNA SORT THE TABLE? --> 1. Ascending || 2. Descending')
        i = int(input('-->'))
        r = []
        k = 1
        for col in headers:
            r.append((k, col))
            k += 1
        column_tuple = tuple(r)

        if i == 1:
            print(tabulate(column_tuple, headers=['Col_no', 'Col_name'], tablefmt='grid'))
            print('Enter the corresponding no. of the column you want to sort by:')
            g = int(input('-->'))
            print('Enter the corresponding no. of the column you want to group by:')
            groupby_column_value = int(input('-->'))

            # Adjust the query to avoid only_full_group_by error
            sort_query = 'SELECT {0}, {1}, COUNT(*) FROM planets GROUP BY {0}, {1} ORDER BY {1}'.format(
                r[groupby_column_value - 1][1], r[g - 1][1])
            
            curry.execute(sort_query)
            result_headers = [r[groupby_column_value - 1][1], r[g - 1][1], "Count"]
            print(tabulate(curry.fetchall(), headers=result_headers, tablefmt='grid'))
            print('Sorting has been successful')

        elif i == 2:
            print(tabulate(column_tuple, headers=['Col_no', 'Col_name'], tablefmt='grid'))
            print('Enter the corresponding no. of the column you want to sort by:')
            g = int(input('-->'))
            print('Enter the corresponding no. of the column you want to group by:')
            groupby_column_value = int(input('-->'))

            # Adjust the query to avoid only_full_group_by error
            sort_query = 'SELECT {0}, {1}, COUNT(*) FROM planets GROUP BY {0}, {1} ORDER BY {1} DESC'.format(
                r[groupby_column_value - 1][1], r[g - 1][1])
            
            curry.execute(sort_query)
            result_headers = [r[groupby_column_value - 1][1], r[g - 1][1], "Count"]
            print(tabulate(curry.fetchall(), headers=result_headers, tablefmt='grid'))
            print('Sorting has been successful')

        else:
            print('Invalid response')
            for j in range(3, 0, -1):
                print('Redirecting to Menu in:', str(j), end='\r')

    except Exception as e:
        print('Sorting failed')
        print('An error has occurred:', str(e))
        for j in range(3, 0, -1):
            print('Breaking the loop in:', str(j), end='\r')
            time.sleep(1)
        print('The loop has been restarted')


def update_table():
    global curry, conobj, headers
    try:
        # Fetch column names from the table
        curry.execute("DESC planets")
        headers = [desc[0] for desc in curry.fetchall()]

        # Prepare the list of columns with corresponding numbers
        r = []
        k = 1
        for col in headers:
            r.append((k, col))
            k += 1
        column_tuple = tuple(r)
        print(tabulate(column_tuple, headers=['Col_no', 'Col_name'], tablefmt='grid'))

        print('CHOOSE THE NUMBER CORRESPONDING TO THE COLUMN YOU WANT TO UPDATE:')
        o = int(input('-->'))

        # Fetch planet names for updating
        planet_query = 'SELECT Planet_name FROM planets'
        curry.execute(planet_query)
        planets = []
        planets_2 = []
        sno = 1
        for row in curry.fetchall():
            planets.append(row)
            planets_2.append((sno, row))
            sno += 1
        print(tabulate(tuple(planets_2), headers=['Planet no.', 'Planetname'], tablefmt='grid'))

        Planet_name_input = int(input('Enter the number corresponding to the planet in the table above: '))
        Planet_name = planets[(Planet_name_input) - 1][0]
        new_value = input('Enter the new value that you want to input into the table: ')
        update_query = "UPDATE PLANETS SET {} = '{}' WHERE Planet_name='{}'".format(r[o - 1][1], new_value, Planet_name)
        curry.execute(update_query)

        print('Are you sure about the changes you are making? (y/n)')
        confirmation = input()
        if confirmation.upper() == 'Y':
            conobj.commit()
            print('Table Updated Successfully')
        else:
            conobj.rollback()
            print('Table updation Aborted')

    except Exception as e:
        print("An error occurred while updating the table:", str(e))
        for j in range(3, 0, -1):
            print('Breaking the loop in:', str(j), end='\r')
            time.sleep(1)
        print('The Loop has been restarted')


def export_to_csv():
    try:
        curry.execute("SELECT * FROM planets")
        records = curry.fetchall()
        headers = [desc[0] for desc in curry.description]

        with open('planets_exportedfile.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(records)
        
        print("Table exported to planets_exportedfile.csv successfully.")
    except Exception as e:
        print("An error occurred while exporting to CSV:", str(e))


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
    global curry, headers

    # Fetch column names from the table
    try:
        curry.execute("DESC planets")
        headers = [desc[0] for desc in curry.fetchall()]
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

                if not results:
                    print("No more records to display.")
                    break

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
        except Exception as e:
            print("An error occurred while paginating the results:", str(e))

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
                if choice in ['1', '2', '3', '4', '5']:
                    # Display column names with numbers
                    r = []
                    k = 1
                    for col in headers:
                        r.append((k, col))
                        k += 1
                    column_tuple = tuple(r)
                    print(tabulate(column_tuple, headers=['Col_no', 'Col_name'], tablefmt='grid'))

                    # User selects column number
                    col_num = int(input('Enter the corresponding no. of the column: '))
                    column = r[col_num - 1][1]

                    if choice == '1':
                        agg_query = "SELECT SUM({}) FROM ({}) as filtered".format(column, filtered_query)
                    elif choice == '2':
                        agg_query = "SELECT MAX({}) FROM ({}) as filtered".format(column, filtered_query)
                    elif choice == '3':
                        agg_query = "SELECT MIN({}) FROM ({}) as filtered".format(column, filtered_query)
                    elif choice == '4':
                        agg_query = "SELECT AVG({}) FROM ({}) as filtered".format(column, filtered_query)
                    elif choice == '5':
                        agg_query = "SELECT COUNT({}) FROM ({}) as filtered".format(column, filtered_query)

                    curry.execute(agg_query)
                    result = curry.fetchone()
                    print("Result: {}".format(result[0]))
                elif choice == '6':
                    break
                else:
                    print("Invalid choice. Please try again.")
            except Exception as e:
                print("An error occurred while performing the aggregate function:", str(e))

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
            if choice in ['1', '2', '3', '4', '5', '6']:
                # Display column names with numbers
                r = []
                k = 1
                for col in headers:
                    r.append((k, col))
                    k += 1
                column_tuple = tuple(r)
                print(tabulate(column_tuple, headers=['Col_no', 'Col_name'], tablefmt='grid'))

                # User selects column number
                col_num = int(input('Enter the corresponding no. of the column: '))
                column = r[col_num - 1][1]

                if choice == '1':
                    min_value = input("Enter the minimum value: ")
                    max_value = input("Enter the maximum value: ")
                    filter_query = "SELECT * FROM planets WHERE {} BETWEEN '{}' AND '{}'".format(column, min_value, max_value)
                elif choice == '2':
                    pattern = input("Enter the pattern (e.g., 'K%'): ")
                    filter_query = "SELECT * FROM planets WHERE {} LIKE '{}'".format(column, pattern)
                elif choice == '3':
                    filter_query = "SELECT * FROM planets WHERE {} IS NULL".format(column)
                elif choice == '4':
                    filter_query = "SELECT * FROM planets WHERE {} IS NOT NULL".format(column)
                elif choice == '5':
                    value = input("Enter the value: ")
                    filter_query = "SELECT * FROM planets WHERE {} > '{}'".format(column, value)
                elif choice == '6':
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
        except Exception as e:
            print("An error occurred while applying the filter:", str(e))


def menu_drive_table():
    while True:
        print("""
        Main Menu:
        1. Create Table
        2. View Table
        3. Explaination of Column Names
        4. Update Table
        5. Filter Table
        6. Sort Table
        7. Convert to Another Format
        8. Delete Table
        9. Exit
        """)
        try:
            ch = int(input("Enter your choice: "))
            if ch == 1:
                create_table()
            elif ch == 2:
                view_table()
            elif ch==3:
                explain_table()
            elif ch == 4:
                update_table()
            elif ch == 5:
                filter_and_search_table()
            elif ch == 6:
                sort_table()
            elif ch == 7:
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
            elif ch == 8:
                delete_table()
            elif ch == 9:
                print("Exiting...")
                break
            else:
                print("Enter a valid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

menu_drive_table() 

curry.close
conobj.close 

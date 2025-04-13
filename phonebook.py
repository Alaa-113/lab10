import psycopg2
import csv

# Connect to PostgreSQL database
def connect():
    return psycopg2.connect(
        host="localhost",
        database="phonebook_db",  
        user="postgres",              
        password="1234"       
    )

# Create table
def create_table():
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Insert from console
def insert_from_console():
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

# Insert from CSV file
def insert_from_csv(file_path):
    conn = connect()
    cur = conn.cursor()
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                cur.execute("INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)", (row[0].strip(), row[1].strip()))

            except psycopg2.Error as e:
                print(f"Error inserting {row}: {e}")
    conn.commit()
    cur.close()
    conn.close()

# Update data
def update_entry():
    target = input("Enter the name or phone to update: ")
    column = input("What do you want to update? (first_name/phone): ").strip()
    new_value = input("Enter new value: ").strip()
    
    if column not in ("first_name", "phone"):
        print("Invalid column")
        return

    conn = connect()
    cur = conn.cursor()
    if target.isdigit():
        cur.execute(f"UPDATE phonebook SET {column} = %s WHERE phone = %s", (new_value, target))
    else:
        cur.execute(f"UPDATE phonebook SET {column} = %s WHERE first_name = %s", (new_value, target))
    conn.commit()
    cur.close()
    conn.close()

# Query
def query_entries():
    filter_col = input("Filter by (first_name/phone): ").strip()
    filter_value = input("Enter value to search: ").strip()

    conn = connect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM phonebook WHERE {filter_col} ILIKE %s", (f"%{filter_value}%",))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

# Delete by username or phone
def delete_entry():
    target = input("Enter the username or phone to delete: ").strip()
    conn = connect()
    cur = conn.cursor()
    if target.isdigit():
        cur.execute("DELETE FROM phonebook WHERE phone = %s", (target,))
    else:
        cur.execute("DELETE FROM phonebook WHERE first_name = %s", (target,))
    conn.commit()
    cur.close()
    conn.close()


def main():
    create_table()  # Ensure table is created
    while True:
        print("\nPhoneBook Menu:")
        print("1. Insert from console")
        print("2. Insert from CSV")
        print("3. Update entry")
        print("4. Query entries")
        print("5. Delete entry")
        print("6. Exit")

        choice = input("Choose an option: ").strip()
        if choice == '1':
            insert_from_console()
        elif choice == '2':
            file_path = input("Enter CSV file path: ")
            insert_from_csv(file_path)
        elif choice == '3':
            update_entry()
        elif choice == '4':
            query_entries()
        elif choice == '5':
            delete_entry()
        elif choice == '6':
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()

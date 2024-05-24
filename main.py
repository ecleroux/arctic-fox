import pyodbc
import json

def get_mssql_database_structure(server, database, username, password):
    # Connect to the MSSQL database
    connection_string = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    # Get tables and their columns with type and constraints
    cursor.execute("""
        SELECT 
            table_name, 
            column_name, 
            data_type, 
            character_maximum_length, 
            column_default, 
            is_nullable 
        FROM information_schema.columns
    """)
    table_data = {}
    for row in cursor.fetchall():
        table_name, column_name, data_type, max_length, column_default, is_nullable = row
        if table_name not in table_data:
            table_data[table_name] = []
        table_data[table_name].append({
            "column_name": column_name,
            "data_type": data_type,
            "max_length": max_length,
            "column_default": column_default,
            "is_nullable": is_nullable == "YES"
        })

    # Get foreign key relationships
    cursor.execute("""
        SELECT 
            fk.name AS constraint_name,
            OBJECT_NAME(fk.parent_object_id) AS table_name,
            c.name AS column_name,
            OBJECT_NAME(fk.referenced_object_id) AS referenced_table,
            rc.name AS referenced_column
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.columns c ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
        INNER JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
    """)
    foreign_keys = {}
    for row in cursor.fetchall():
        constraint_name, table_name, column_name, referenced_table, referenced_column = row
        if table_name not in foreign_keys:
            foreign_keys[table_name] = []
        foreign_keys[table_name].append({
            "constraint_name": constraint_name,
            "column_name": column_name,
            "referenced_table": referenced_table,
            "referenced_column": referenced_column
        })

    # Close the database connection
    cursor.close()
    connection.close()

    # Combine the table data and foreign keys
    for table_name, columns in table_data.items():
        if table_name in foreign_keys:
            table_data[table_name].extend(foreign_keys[table_name])

    return table_data

def save_to_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    # Replace these with your MSSQL server details
    server_name = "your_server_name"
    database_name = "your_database_name"
    username = "your_username"
    password = "your_password"

    # Get the database structure
    db_structure = get_mssql_database_structure(server_name, database_name, username, password)

    # Save the database structure to a JSON file
    json_file_path = "database_structure.json"
    save_to_json(db_structure, json_file_path)

    print(f"Database structure saved to '{json_file_path}'")

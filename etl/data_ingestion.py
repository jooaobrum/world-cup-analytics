# Imports
import pandas as pd
import sqlalchemy as db
from pathlib import Path
import os
import tqdm

# Useful functions
def create_table(var_type, table_name, con):
    # Query to create a table
    query_drop = "DROP TABLE IF EXISTS {};".format(table_name)
    query_table = "CREATE TABLE {} (".format(table_name)

    # Fill the query with types and variables
    for i in range(len(var_type)):
        var = var_type.loc[i]['var']
        type = var_type.loc[i]['type']
        
        query_table = query_table + str(var) + ' ' + str(type) + ','

    query_table = query_table[:-1] + ');'

    # Drop table if exists and create a new one (replace)
    con.execute(query_drop)
    con.execute(query_table)


# Create a new database 
def create_database(db_name):
    Path('database/{}.db'.format(db_name)).touch()

def table_info(df):
    # Map the variables from python to sqlite
    sql_type = {'object': 'TEXT', 'int64': 'INTEGER', 'float64': 'REAL'}
    # Save the variable name and the type 
    var_type = pd.DataFrame(df.dtypes).reset_index().rename(columns={'index': 'var', 0: 'type'})
    
    # Change the type to sqlite format
    var_type['type'] = var_type['type'].astype(str).map(sql_type)

    return var_type



def main():
    
    db_name = 'brazil_wc2022.db'


    # Open the connection with the database
    print('Opening connection...')
    engine = db.create_engine('sqlite:///' + db_name)
    print('Ok')

    # Find all files 
    files = os.listdir()
    
    print('Creating table into the database...')
    for filename in tqdm.tqdm(files):
        if '.csv' in filename:
           
            table_name = filename.split('.')[0]
            # Read the data
            df = pd.read_csv(filename, index_col = [0])
            print(df)

            # Extract the variables and the types to create a table
            var_types = table_info(df)
           
            # Create table
            create_table(var_types, table_name, engine)

            # Insert the CSV into SQL
            df.to_sql(table_name, engine, if_exists='replace', index = False) 

    print('Ok')

if __name__ == "__main__":
    main()


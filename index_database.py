import sqlite3

filename = 'market.db'
connection = sqlite3.connect(filename)

cursor = connection.cursor()

def fix_table(name):
    cursor.execute(f"PRAGMA table_info({name});")
    columns = cursor.fetchall()

    price_columns = [f'"{col[1]}"' for col in columns if col[1] != 'time']

    print(price_columns)
    index_query = f"CREATE INDEX idx_price_history_{name} ON ask ({', '.join(price_columns)}, time);"

    print(index_query)

    cursor.execute(index_query)
    connection.commit()

fix_table('ask')
fix_table('bid')

connection.close()

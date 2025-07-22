"""
The column time is in seconds since the epoch. I would like to convert and then
group by month. Then for each month, create a copy of the table with only those
time values included and name the table yyyy_mm.
"""

import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import time
import os

def query(q_string, fname='market.db'):
    """
    Query the sqlite database and return a pandas dataframe
    """
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    data = pd.read_sql_query(q_string, conn)
    conn.close()
    return data

def write_pandas_to_sqlite(df, fname, table_name='ask'):
    """
    Write a pandas dataframe to a sqlite database
    """
    conn = sqlite3.connect(fname)
    if check_database_for_table(table_name, fname):
        print(f'Table {table_name} already exists in {fname}, dropping')
        conn.execute(f"DROP TABLE {table_name}")
    df.to_sql(table_name, conn, index=False)
    conn.close()

def check_database_for_table(table_name, database='market.db'):
    """
    Check if a table exists in a database
    """
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if c.fetchone():
        return True
    else:
        return False

def archive_database(table='ask', database='market.db'):
    print(f'Archiving {table} in {database}')
    data = query(f"""
    select *, datetime(time, 'unixepoch') as datestring
    from {table}
    """, database)
    data.datestring = pd.to_datetime(data.datestring)
    data['month_year'] = data.datestring.dt.to_period('M')

    for name, group in data.groupby('month_year'):
        output_database = f'archive/market_{name}.db'
        output_dataframe = (group
                            .drop(columns=['datestring', 'month_year', 'index'], errors='ignore')
                            .reset_index(drop=True)
                           )
        write_pandas_to_sqlite(output_dataframe, output_database, table)
        print(f'Wrote {name}/{table} to {output_database}')

"""
Next, we would like to be able to reconstitute the original database from the archives.
"""
def read_directory(directory):
    asks = []
    bids = []
    for file in os.listdir(directory):
        if file.endswith('.db'):
            ask = query('select * from ask', f'{directory}/{file}')
            bid = query('select * from bid', f'{directory}/{file}')
            asks.append(ask)
            bids.append(bid)
    if len(asks) == 0:
        print(f'No databases found in {directory}')
        return None, None
    asks = pd.concat(asks, ignore_index=True)
    bids = pd.concat(bids, ignore_index=True)
    asks = asks.sort_values('time').reset_index(drop=True)
    bids = bids.sort_values('time').reset_index(drop=True)
    return asks, bids

def reconstitute(archive_directory, output_database='market_super.db', limit=None):
    asks, bids = read_directory(archive_directory)
    # Limit is number of months if not None
    if limit:
        limit_in_seconds = limit * 30 * 24 * 60 * 60
        now = time.time()
        asks = asks[asks.time > now - limit_in_seconds]
        bids = bids[bids.time > now - limit_in_seconds]
    asks = asks.drop_duplicates(subset='time').sort_values('time').reset_index(drop=True)
    bids = bids.drop_duplicates(subset='time').sort_values('time').reset_index(drop=True)
    write_pandas_to_sqlite(asks, output_database, 'ask')
    write_pandas_to_sqlite(bids, output_database, 'bid')
    print(f'Wrote {output_database}')

def standard_operating_procedure():
    """ 
    Data is continuously written to market.db. Archiving will be
    done manually to avoid mistakes. And will never write over the
    actual market.db file. It will be my job to copy the data over.
    1. Load in all new and old data into a super database.
    2. Backup the super database so it is not lost.
    3. Create a new set of backup files.
    4. Create a view of the last 6 months. (can be copied manually)
    """
    print(f'@@@ Running standard operating procedure')
    # Print with the color red in linux terminal
    archive_ask, archive_bid = read_directory('archive')
    live_ask = query('select * from ask', 'market.db')
    live_bid = query('select * from bid', 'market.db')
    full_ask = (
            pd.concat([archive_ask, live_ask])
            .drop_duplicates(subset='time')
            .sort_values('time')
            .reset_index(drop=True)
            )
    full_bid = (
            pd.concat([archive_bid, live_bid])
            .drop_duplicates(subset='time')
            .sort_values('time')
            .reset_index(drop=True)
            )
    print(f'@@@ Loaded {len(full_ask)} asks and {len(full_bid)} bids')
    # Backup the super database
    write_pandas_to_sqlite(full_ask, 'market_super.db', 'ask')
    write_pandas_to_sqlite(full_bid, 'market_super.db', 'bid')
    print(f'@@@ Backed up super database to market_super.db')
    # Create the archive
    archive_database('ask', 'market_super.db')
    archive_database('bid', 'market_super.db')
    print(f'@@@ Archived super database')
    # Create the view
    reconstitute('archive', 'market_view.db', 6)
    print(f'@@@ Created view of last 6 months')


#|%%--%%| <RLTzBdFZAk|2tZSaZUjDe>

standard_operating_procedure()

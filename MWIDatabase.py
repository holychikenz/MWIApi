#!/usr/bin/env python3
import sqlite3
import json
import numpy as np
import datetime
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Market Watcher Interface')
    parser.add_argument('-a', '--archive', action='store_true', help='Archive the current market.db')
    parser.add_argument('-r', '--rebuild', action='store_true', help='Rebuild the current market.db from the archives')
    return parser.parse_args()

class MWIDatabase:
    def __init__(self, databaseFile):
        self.connection = sqlite3.connect(databaseFile)

    def createTable(self, name, firstRow):
        cursor = self.connection.cursor()
        rowstring = "( time INTEGER PRIMARY KEY,\""+"\",\"".join(firstRow)+"\")"
        cursor.execute(f'''CREATE TABLE {name} {rowstring}''')
        self.connection.commit()

    def appendRow(self, name, time, row):
        cursor = self.connection.cursor()
        #cursor.execute("CREATE INDEX IF NOT EXISTS ask_time ON ask(time)")
        #cursor.execute("CREATE INDEX IF NOT EXISTS bid_time ON bid(time)")
        # Check if the table exists yet, if not create it
        cursor.execute(f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name=\"{name}\" ''')
        if cursor.fetchone()[0]!=1:
            # Create a new table
            self.createTable( name, row.keys() )

        # Check the column names in existing table
        response = cursor.execute(f'''PRAGMA table_info({name})''')
        currentRowHeaders = [z[1] for z in response.fetchall()]
        # Check that current table does not need additional columns
        for key in row.keys():
            if key not in currentRowHeaders:
                cursor.execute(f'ALTER TABLE {name} ADD COLUMN \"{key}\"')
        # Check data is not missing entries
        for header in currentRowHeaders:
            if (header not in row.keys()) and (header != 'time'):
                row[header] = -1
        rowkeystring = "time"
        valuekeystring = f"{time}"
        for (k, v) in row.items():
            rowkeystring += f",\"{k}\""
            valuekeystring += f",{v}"
        ## Avoid adding a row that already exists
        cursor.execute(f'SELECT 1 FROM {name} WHERE time = {time}')
        rowExists = len(cursor.fetchall())
        if rowExists < 1:
            cursor.execute(f'INSERT INTO {name} ({rowkeystring}) VALUES ({valuekeystring})')
        # Finally, insert this new row
        self.connection.commit()

    def close(self):
        self.connection.close()


def archive(archive_dir):
    main_db = MWIDatabase("market.db")
    years = main_db.connection.execute("SELECT DISTINCT time FROM ask").fetchall()
    # From unix time to year
    years = np.unique([datetime.datetime.fromtimestamp(x[0]).year for x in years])
    ask_header = [k[1] for k in main_db.connection.execute(f"PRAGMA table_info(ask)").fetchall()][1:]
    for year in years:
        year_db = MWIDatabase(f"{archive_dir}/market_{year}.db")
        for table in ['ask', 'bid']:
            rows = main_db.connection.execute(f"SELECT * FROM {table} WHERE time >= {int(datetime.datetime(year, 1, 1).timestamp())} AND time < {int(datetime.datetime(year+1, 1, 1).timestamp())}").fetchall()
            for row in rows:
                row_time = row[0]
                row_stuff = {k:(row[i] if row[i] else -1) for i,k in enumerate(ask_header)}
                year_db.appendRow(table, row_time, row_stuff)
        year_db.close()
        print(f"Done processing {year}")
    main_db.close()

def rebuild_this_year(archive_dir):
    # Create a new market.db (kill the old one), then read all the archives and append them to the new
    # market.db
    os.remove("market.db")
    this_year = datetime.datetime.now().year
    year_files = os.listdir(archive_dir)
    main_db = MWIDatabase("market.db")
    for yf in year_files:
        year_db = MWIDatabase(f"{archive_dir}/{yf}")
        ask_header = [k[1] for k in year_db.connection.execute(f"PRAGMA table_info(ask)").fetchall()][1:]
        for table in ['ask', 'bid']:
            rows = year_db.connection.execute(f"""
                                                SELECT * FROM {table} WHERE time >= {
                                                    int(datetime.datetime(this_year, 1, 1).timestamp())}
                                                    AND time < {int(datetime.datetime(this_year+1, 1,
                                                    1).timestamp())}
                                                """).fetchall()
            for row in rows:
                row_time = row[0]
                row_stuff = {k:(row[i] if row[i] else -1) for i,k in enumerate(ask_header)}
                main_db.appendRow(table, row_time, row_stuff)
        year_db.close()
        print(f"Done processing {yf}")
    main_db.close()

if __name__ == '__main__':
    args = get_args()
    db = MWIDatabase("market.db")
    with open('milkyapi.json') as j:
        data = json.load(j)
        time = int(data['time'])
        market = data['market']
        # Two tables, ask and bid
        askRow = {k:v['ask'] for (k,v) in market.items()}
        bidRow = {k:v['bid'] for (k,v) in market.items()}
        db.appendRow('ask', time, askRow)
        db.appendRow('bid', time, bidRow)
    db.close()

    if args.archive:
        archive('archive')
    if args.rebuild:
        rebuild_this_year('archive')

import sqlite3
import json
import numpy as np

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
                # Add new column
                pass
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
        else:
            print(f"Skipping insertion: Time {time} exists in TABLE {name}")
        # Finally, insert this new row
        self.connection.commit()

    def close(self):
        self.connection.close()

if __name__ == '__main__':
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

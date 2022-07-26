#!/usr/bin/env python3
import time
import sqlite3
import pandas as pd
import json

def readDBGetMedian(hours, table):
    target = time.time() - hours*3600
    con = sqlite3.connect("file:market.db?mode=ro",uri=True)
    tab = pd.read_sql_query(f'SELECT * FROM {table} WHERE time > {target}', con)
    con.close()
    return tab.median()

def joinConvert(ask, bid):
    Dictionary = {}
    usetime = ask['time']
    Dictionary["time"] = usetime
    Dictionary["market"] = {}
    ask = ask.drop(['time'])
    bid = bid.drop(['time'])
    for key in ask.keys():
        Dictionary["market"][key] = {"ask":ask[key], "bid":bid[key]}
    return Dictionary

askdf = readDBGetMedian(24, "ask")
biddf = readDBGetMedian(24, "bid")

market = joinConvert(askdf, biddf)

with open("medianmarket.json", "w") as j:
    json.dump(market, j, indent=2)

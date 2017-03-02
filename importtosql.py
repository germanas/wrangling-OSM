import sqlite3
import csv
from pprint import pprint

sqlite_file = 'vilniusdb.db'    # name of the sqlite database file

def import_to_sql(dbname):
    # Connect to the database
    conn = sqlite3.connect(sqlite_file)
    # Get a cursor object
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS nodes')
    cur.execute('DROP TABLE IF EXISTS nodes_tags')
    cur.execute('DROP TABLE IF EXISTS ways')
    cur.execute('DROP TABLE IF EXISTS ways_tags')
    cur.execute('DROP TABLE IF EXISTS ways_nodes')
    conn.commit()

    # Create the table, specifying the column names and data types:
    cur.execute('''
        CREATE TABLE nodes(
        id INTEGER PRIMARY KEY NOT NULL,
        lat REAL,
        lon REAL,
        user TEXT,
        uid INTEGER,
        changeset INTEGER,
        timestamp TEXT)
    ''')
    cur.execute('''
        CREATE TABLE nodes_tags(id INTEGER,
        key TEXT,
        value TEXT,
        type TEXT, FOREIGN KEY (id) REFERENCES nodes(id))
    ''')
    cur.execute('''
        CREATE TABLE ways(id INTEGER PRIMARY KEY NOT NULL,
        user TEXT,
        uid INTEGER,
        version TEXT,
        changeset INTEGER,
        timestamp TEXT)
    ''')
    cur.execute('''
        CREATE TABLE ways_tags(
        id INTEGER NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        type TEXT, FOREIGN KEY (id) REFERENCES ways(id))
    ''')
    cur.execute('''
        CREATE TABLE ways_nodes(
        id INTEGER NOT NULL,
        node_id INTEGER NOT NULL,
        position INTEGER NOT NULL,FOREIGN KEY (id) REFERENCES ways(id), FOREIGN KEY (node_id) REFERENCES nodes(id))
    ''')

    # commit the changes
    conn.commit()

    # Read in the csv file as a dictionary, format the
    # data as a list of tuples:
    with open('nodes.csv','rb') as fin:
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['id'], i['lat'],i['lon'], i['user'].decode("utf-8"), i['uid'], i['changeset'], i['timestamp']) for i in dr]

    with open('nodes_tags.csv','rb') as fin2:
        dr2 = csv.DictReader(fin2) # comma is default delimiter
        to_db2 = [(i['id'], i['key'].decode("utf-8"),i['value'].decode("utf-8"), i['type']) for i in dr2]
        pprint(to_db2)

    with open('ways.csv','rb') as fin3:
        dr3 = csv.DictReader(fin3) # comma is default delimiter
        to_db3 = [(i['id'], i['user'].decode("utf-8"),i['uid'].decode("utf-8"), i['version'], i['changeset'], i['timestamp']) for i in dr3]

    with open('ways_tags.csv','rb') as fin4:
        dr4 = csv.DictReader(fin4) # comma is default delimiter
        to_db4 = [(i['id'], i['key'].decode("utf-8"),i['value'].decode("utf-8"), i['type']) for i in dr4]

    with open('ways_nodes.csv','rb') as fin5:
        dr5 = csv.DictReader(fin5) # comma is default delimiter
        to_db5 = [(i['id'], i['node_id'],i['position']) for i in dr5]

    # insert the formatted data
    cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)
    cur.executemany("INSERT INTO nodes_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db2)
    cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db3)
    cur.executemany("INSERT INTO ways_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db4)
    cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db5)
    # commit the changes
    conn.commit()
    # Just to test if this works
    cur.execute('SELECT * FROM ways_nodes')
    #all_rows = cur.fetchall()
    #print('1):')
    #pprint(all_rows)

    conn.close()

import_to_sql(sqlite_file)
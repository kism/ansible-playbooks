#!/usr/bin/env python3

import requests
import socket
import time
import sys
import sqlite3

from ping3 import ping
from sqlite3 import Error

iprange = "10.42.0."
influxhost = "graf.kg.lan"
influxport = "8086"
influxdatabase = "servicesexternal"
hostlist = []
debug = False


def print_debug(text):  # Debug messages in yellow if the debug global is true
    if debug:
        print("\033[93m" + text + "\033[0m")

def scanhosts(conn):
    for i in range(1, 254):
        ip = iprange + str(i)

        entry = None

        try:
            entry = socket.gethostbyaddr(ip)
        except socket.herror:
            time.sleep(0)

        timeepoch = int(time.time())

        if entry != None:
            print('Found: ' + entry[0] + ' at IP address: ' + ip)
            try:
                add_entry(conn, (entry[0], timeepoch))
            except sqlite3.IntegrityError:
                pass  # If the unique check fails, just move on
        else:
            print_debug('nothing at: ' + ip)


def add_entry(conn, entry):
    # Add entry to the elo table
    sql = ''' INSERT INTO hosts(hostname,lastalive)
            VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, entry)
    print('adding to database: ' + str(entry))


def gethosts(conn):
    cur = conn.cursor()
    cur.execute("SELECT hostname FROM hosts")
    list = cur.fetchall()
    # print(list)
    hostnamelist = []
    for hostname in list:
        hostnamelist.append(hostname[0])
    print(hostnamelist)
    return(hostnamelist)


def checkhosts(conn):
    hostlist = gethosts(conn)
    timeepoch = int(time.time())
    timestamp = timeepoch * 1000000000
    for host in hostlist:
        pingresult = ping(host)
        # print('\n DEBUG ' + host + ' ' + str(pingresult) + '\n')
        if pingresult == False:
            result = False
        else:
            result = True

        url = 'http://' + influxhost + ":" + influxport + "/write?db=" + influxdatabase

        data = "ping" + ',' + 'host=kg.lan' + ',lad=' + host + \
            ' ' + 'value=' + str(result) + ' ' + str(timestamp)
        print(url + ' | ' + data)
        try:
            x = requests.post(url, data=data)
        except requests.exceptions.ConnectionError:
            pass

        print(x)
        print('\n')
        time.sleep(0.1)


def create_connection(db_file):
    # Init to connect to db
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def create_table(conn, create_table_sql):
    # init to create table
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    database = "hosts.db"

    sql_create_elo_table = """ CREATE TABLE IF NOT EXISTS hosts (
                                        hostname  text      PRIMARY KEY,
                                        lastalive int       NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection(database)
    if conn is None:
        print("Error! cannot create the database connection.")

    create_table(conn, sql_create_elo_table)  # keyword, create table

    if len(sys.argv) == 1:
        print("Give parameter pls")
    elif sys.argv[1] == 'scan':
        scanhosts(conn)
    elif sys.argv[1] == 'ping':
        checkhosts(conn)
    else:
        print("What have you done? try 'scan' or 'ping' as a parameter")

    conn.commit()


if __name__ == '__main__':
    main()


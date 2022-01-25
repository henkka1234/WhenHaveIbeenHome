#!/usr/bin/python

import sqlite3
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from numpy import double
import json
import psycopg2
import sched, time

conn = sqlite3.connect('timedb.sqlite')
c = conn.cursor()

daysdb = sqlite3.connect('daysdb.sqlite')
daydbconn = daysdb.cursor()

try:
    daydbconn.execute('''SELECT count(name) FROM Days''')
    print("Database already exists, using that")
#If not create one
except:
    #0=came, 1=left
    #rowid
    daydbconn.execute('''CREATE TABLE Days (name TIMESTAMP, value DOUBLE(3,1), mac STRING, PRIMARY KEY(name,mac))''')
    print("Database not found.\nCreated a database")

def timeDifference(start, end):
    f = '%H:%M:%S'
    start = datetime.datetime.strptime(start,f)
    end = datetime.datetime.strptime(end,f)

    return end-start

def toTime(value):
    f = '%H:%M:%S'
    return datetime.datetime.strptime(value,f)

s = sched.scheduler(time.time, time.sleep)

def read_db(sc):
    #mac of the device that is used to track the user
    mac = 'AC:D6:18:44:2A:A3'
    c.execute('''SELECT DISTINCT day FROM Times WHERE mac=? ''', (mac,))
    data = c.fetchall()
    athomeFor = "00:00:00"
    athomeFor = timeDifference(athomeFor,athomeFor)
    days = list()

#Client has been home 24 hours if last day's last event is 0 and there are no events next day

    for line in data:
        days.append(line[0])
    for day in days:
        athomeFor = "00:00:00"
        athomeFor = timeDifference(athomeFor,athomeFor)
        c.execute('''SELECT hour, reason FROM Times WHERE day=? AND mac=? ''', (day,mac,))
        hours = c.fetchall()
        if hours[0][1]==1:
            athomeFor=timeDifference("00:00:00",hours[0][0])
        for ind, hour in enumerate(hours):
            if hour[1]==0 and ind<(len(hours)-1):
                athomeFor = athomeFor + timeDifference(hour[0],hours[ind+1][0])
            elif ind==(len(hours)-1) and hour[1]==0:
                athomeFor = athomeFor + timeDifference(hour[0],'23:59:59')
        #rounding the time at home to 1 decimal
        daydbconn.execute('''INSERT OR IGNORE INTO Days (name, value, mac)
                    VALUES (?,?,?)''', (day,round(athomeFor.seconds/3600.0,1),mac,))
        daysdb.commit()
    
    my_query = query_db("select name,value from Days WHERE mac='AC:D6:18:44:2A:A3'")
    json_output = json.dumps(my_query)
    print(json_output)
    with open('Days.json', 'w') as f:
        f.write(json_output)

    s.enter(10,1, read_db, (sc,))        
"""
def graph_data():
    daydbconn.execute('''SELECT name, value FROM Days''')
    data = daydbconn.fetchall()

    dates = []
    values = []
    f = '%Y-%M-%d'
    for row in data:
        dates.append(row[0])
        values.append(int(row[1].split(':')[0]))

    #plt.plot_date(dates,values,'-')
    plt.figure(figsize=(20,15))
    plt.bar(dates,values,width=0.8)
    plt.savefig('foo.png')
"""
def query_db(query, args=(), one=False):
    cur = daydbconn
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    return (r[0] if r else None) if one else r

s.enter(10,1,read_db, (s,))
s.run()

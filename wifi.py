#!/usr/bin/env python
#6 = reason; deauth = leaving; assoc=join
#7 = mac

#to be added:
#spoof mac to dns form pfsense dhcp list
#frontend

import sqlite3
import sched, time

base = sqlite3.connect('timedb.sqlite')
cur = base.cursor()
#Test if a database already exists
try:
    cur.execute('''SELECT count(day) FROM Times''')
    print("Database already exists, using that")
#If not create one
except:
    #0=came, 1=left
    #rowid
    cur.execute('''CREATE TABLE Times (day TIMESTAMP, hour TIMESTAMP, mac STRING, reason INT, PRIMARY KEY(day, hour))''')
    print("Database not found.\nCreated a database")

location = "asus.log"

#for the timed loop
s = sched.scheduler(time.time, time.sleep)

#If a client comes back (reason 0) before leaving first, ignore the log entry.

def cleanTimeDay(value):
    value = value.split('T')
    day = value[0]
    return day

def cleanTimeHour(value):
    value = value.split('T')
    tim = value[1].split('+')
    tim = tim[0]
    return tim

def update_db(sc):
    print("working")
    file = open(location)
    for line in file:
        line = line.split(" ")
        if len(line)>7:
            if line[6]=="Deauth_ind":
                #check that the client hasn't already left
                cur.execute('''SELECT reason FROM Times WHERE mac=? ORDER BY rowid DESC LIMIT 1''', (line[7].replace(',',''),))
                try:
                    latest = cur.fetchone()[0]
                    try:
                        latest = int(latest)
                    except:
                        pass
                except:
                    latest = 0
                if latest != 1:
                    cur.execute('''INSERT OR IGNORE INTO Times (day, hour, mac, reason)
                            VALUES (?,?,?,1)''', (cleanTimeDay(line[0]), cleanTimeHour(line[0]), line[7].replace(',','')))
                    base.commit()

            elif line[6]=="Assoc":
                #check that the client hasn't already came back
                cur.execute('''SELECT reason FROM Times WHERE mac=? ORDER BY rowid DESC LIMIT 1''', (line[7].replace(',',''),))
                try:
                    latest = cur.fetchone()[0]
                    latest = int(latest)
                except:
                    latest = 1
                if latest != 0:
                    cur.execute('''INSERT OR IGNORE INTO Times (day, hour, mac, reason)
                            VALUES (?,?,?,0)''', (cleanTimeDay(line[0]), cleanTimeHour(line[0]), line[7].replace(',','')))
                    base.commit()
    s.enter(10,1, update_db, (sc,))

s.enter(10,1,update_db, (s,))
s.run()
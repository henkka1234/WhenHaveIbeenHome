#!/usr/bin/env python
#6 = reason; deauth = leaving; assoc=join
#7 = mac

import sqlite3
import datetime
import sched, time
import json

#LOCATION OF THE LOG
location = "asus.log"
#MAC-ADDRESS
mac = 'AC:D6:18:44:2A:A3'
#LOCATION OF THE JSON FILE
fileLocation = "Days.json"
#LOCATION OF DETAILS.HTML, put this in assets folder!
detailsLocation = "details.html"
base = sqlite3.connect('timedb.sqlite')
cur = base.cursor()
#Test if a database already exists
try:
    cur.execute('''SELECT count(day) FROM Times''')
    print("timdb database already exists, using that")
#If not create one
except:
    #0=came, 1=left
    #rowid
    cur.execute('''CREATE TABLE Times (day TIMESTAMP, hour TIMESTAMP, mac STRING, reason INT, PRIMARY KEY(day, hour))''')
    print("timedb database not found.\nCreated a database")

daysdb = sqlite3.connect('daysdb.sqlite')
daydbconn = daysdb.cursor()

try:
    daydbconn.execute('''SELECT count(name) FROM Days''')
    print("daysdb database already exists, using that")
#If not create one
except:
    #0=came, 1=left
    #rowid
    daydbconn.execute('''CREATE TABLE Days (name TIMESTAMP, value DOUBLE(3,1), mac STRING, PRIMARY KEY(name,mac))''')
    print("daysdb database not found.\nCreated a database")

def timeDifference(start, end):
    f = '%H:%M:%S'
    start = datetime.datetime.strptime(start,f)
    end = datetime.datetime.strptime(end,f)

    return end-start

def toTime(value):
    f = '%H:%M:%S'
    return datetime.datetime.strptime(value,f)

#for the timed loop
s = sched.scheduler(time.time, time.sleep)

def cleanTimeDay(value):
    value = value.split('T')
    day = value[0]
    return day

def cleanTimeHour(value):
    value = value.split('T')
    tim = value[1].split('+')
    tim = tim[0]
    return tim

def query_db(query, args=(), one=False):
    cur = daydbconn
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    return (r[0] if r else None) if one else r

def read_db():
    cur.execute('''SELECT DISTINCT day FROM Times WHERE mac=? ''', (mac,))
    data = cur.fetchall()
    athomeFor = "00:00:00"
    athomeFor = timeDifference(athomeFor,athomeFor)
    days = list()

#Client has been home 24 hours if last day's last event is 0 and there are no events next day

    for line in data:
        days.append(line[0])
    for dayind, day in enumerate(days):
        athomeFor = "00:00:00"
        athomeFor = timeDifference(athomeFor,athomeFor)
        cur.execute('''SELECT hour, reason FROM Times WHERE day=? AND mac=? ''', (day,mac,))
        hours = cur.fetchall()
        #Calculating the at home hours and storing them in Days database
        #if first entry is leaving (1), calculate how long user was home before that
        if hours[0][1]==1:
            athomeFor=timeDifference("00:00:00",hours[0][0])
        #loop over the entries of one day
        for ind, hour in enumerate(hours):
            if hour[1]==0 and ind<(len(hours)-1):
                athomeFor = athomeFor + timeDifference(hour[0],hours[ind+1][0])
            #if the user comes home and doesn't leave anymore during the same day
            elif (ind==(len(hours)-1) and hour[1]==0 and dayind<len(days)-1):
                athomeFor = athomeFor + timeDifference(hour[0],'23:59:59')

        #Search the Daysdb for the day currently in the loop
        daydbconn.execute("SELECT value FROM Days WHERE mac=? AND name=?",(mac,day,))
        oldValues = daydbconn.fetchall()
        #if length of oldValues is 0 there aren't any entries for the day so we'll create one
        if len(oldValues)==0:
            daydbconn.execute('''INSERT OR IGNORE INTO Days (name, value, mac)
                        VALUES (?,?,?)''', (day,round(athomeFor.seconds/3600.0,1),mac,))
            daysdb.commit()
        #If there already is an entry, we'll check is the now calculated time at home greater that the old value
        else:
            #[0][0] as values are in tuples that are in arrays of size 1
            oldValues = oldValues[0][0]
            if(round(athomeFor.seconds/3600.0,1)>oldValues):
                daydbconn.execute('''UPDATE Days SET value = ? WHERE name=? AND mac=?''', (round(athomeFor.seconds/3600.0,1),day,mac,))
                daysdb.commit()
    
    #creating the json file
    my_query = query_db("select name,value from Days WHERE mac=?",(mac,))
    json_output = json.dumps(my_query)
    print(json_output)

    with open(fileLocation, 'w') as f:
        f.write(json_output)

#create new details.html at set intervals
def createDetails():
    cur.execute("SELECT DISTINCT day FROM Times WHERE mac=? ",(mac,))
    daysdb = cur.fetchall()
    days = []
    otherinfo = list()

    for day in daysdb:
        days.append(str(day[0]))
        cur.execute("SELECT hour, reason FROM Times WHERE day=? AND mac=? ",(str(day[0]),mac,))
        details = cur.fetchall()
        otherinfo.append((details))

    with open(detailsLocation, 'w') as f:
        f.write('''<link href="txtstyle.css" rel="stylesheet" type="text/css"> \n''')
        f.write("<h1>"+"This page shows the timestamps when the device "+mac+" has left the network</h1>\n")
        f.write("<h1>The format is (timestamp, 0 or 1)</h1>\n")
        f.write("<h1>0 = The device connected. 1 = The device disconnected")
        for ind, day in enumerate(days):
            f.write("<h2>"+day+"</h2>\n")
            for info in otherinfo[ind]:
                f.write("<p>"+str(info)+"</p>")

#The main 
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
    read_db()
    createDetails()
    s.enter(10,1, update_db, (sc,))

s.enter(10,1,update_db, (s,))
s.run()


 
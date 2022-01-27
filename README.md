# WhenHaveIbeenHome
Project that creates good looking charts about when you have been home based on your home WiFi logs

![Näyttökuva 2022-01-27 175736](https://user-images.githubusercontent.com/25725660/151395644-b20751de-6c3a-47ef-bfdf-c0ccc6574bbc.png)

## About

This program is built to work on Asus RT-AC68U WiFi router, other routers may have different log syntaxes which may not work with this application.

Wifi.py file is used as a backend service which collects data from the log and creates json-file for the frontend application.

Wifi.py reads log of WiFi-hotspot, parses it, creates and updates a sqlite database about when and which devices have joined and left the WiFi-station. The program also
calculates how long the device has been connected to the wifi network and thus how long and when the user has been home, it then creates a new database where it stores this information. The program also outputs the new database in json format for the frontend

The frontend is an Angular program based on ngx-graph demo. The frontend visualizes the data that it reads from the json file that wifi.py creates.

## Installation
Tested on Ubuntu 18.04.5 LTS Server, should work on other Linux distros too as long as prerequisites are met.
Some devices nowadays use randomized mac-addressm. For this program to work you have to use static mac-address. Android devices running Android 10 or newer default to randomized mac-address!
### Prerequisites
Rsyslog\
Python 3.7\
PIP3\
Psycopg2\
Numpy\
Apache2 or equivalent web-server\

Log in to your router and add your server's IP-address to the remote log server field:
![Näyttökuva 2022-01-26 001217](https://user-images.githubusercontent.com/25725660/151068657-9237b3b5-1865-4a8f-8a9c-8798b4c93641.png)

Configure Rsyslog to store the logs in the place most suitable for you
Update the log location to the field "location" in wifi.py
Update the mac-address you want to use to the field "mac" and update the location where you want to save the details.html file in wifi.py. Update also the location where to save the json file, this should be stored in the frontend's "assets" folder.
Run wifi.py, you can use Screen to run the wifi.py in the background.
Configure apache to serve the frontend (just point it to serve the "my-app" folder).

You can test the program with the provided asus.log file

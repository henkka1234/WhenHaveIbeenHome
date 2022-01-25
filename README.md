# WhenHaveIbeenHome
Project that creates good looking charts about when you have been home based on your home WiFi logs

![Näyttökuva 2022-01-26 003128](https://user-images.githubusercontent.com/25725660/151070741-a6273f3f-fcdb-400b-baae-c3afe96dcff8.png)


## About

This program is built to work on Asus RT-AC68U WiFi router, other routers may have different log syntaxes which may not work with this application.

Wifi.py and visualize.py files are used as backend services which together create json file for the frontend application.

Wifi.py reads log of WiFi-hotspot, parses it, creates and updates a sqlite database about when and which devices have joined and left the WiFi-station.
Visualize.py reads the database that wifi.py created. Visualize.py calculates how long the device has been connected to the wifi network and thus how long and when the user has been home. Visualize.py then creates a new database where it stores this information. The program also outputs the new database in json format for the frontend

The frontend is an Angular program based on ngx-graph demo. The frontend visualizes the data that it reads from the json file that visualize.py creates.

## Installation
Tested on Ubuntu 18.04.5 LTS Server, should work on other Linux distros too as long as prerequisites are met.
### Prerequisites
Rsyslog
Python 3.7
PIP3
Psycopg2
Numpy
Apache2 or equivalent web-server

Log in to your router and add your server's IP-address to the remote log server field:
![Näyttökuva 2022-01-26 001217](https://user-images.githubusercontent.com/25725660/151068657-9237b3b5-1865-4a8f-8a9c-8798b4c93641.png)

Configure Rsyslog to store the logs in the place most suitable for you
Update the log location to the field "location" in wifi.py
Update the mac-address you want to use to the field "mac" in visualization.py. Update also the location where to save the json file, this should be stored in the frontend's "assets" folder.
Run wifi.py first as visualization.py uses the database that wifi.py creates.
Start visualize.py, you can use Screen to run multiple shell instances at the same time.
Configure apache to serve the frontend (just point it to serve the "my-app" folder).

You can test if the program works with the provided asus.log file

## Coming soon
Simplifying the backend and combining the two python files for easier install.
Making the backend easier to configure, at the moment the MAC-address which is used to track when the user is home is hard coded in to the visualize.py
Simplifying the frontend as it's currently built on top of demo project.

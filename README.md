# WhenHaveIbeenHome
Program that creates statistics about when you have been home based on your home WiFi logs

## About

This program is built to work on Asus RT-AC68U WiFi router, other routers may have different log syntaxes which may not work with this application.

Wifi.py and visualize.py files are used as backend services which together create json file for the frontend application.

Wifi.py reads log of WiFi-hotspot, parses it, creates and updates a sqlite database about when and which devices have joined and left the WiFi-station.
Visualize.py reads the database that wifi.py created. Visualize.py calculates how long the device has been connected to the wifi network and thus how long and when the user has been home. Visualize.py then creates a new database where it stores this information. The program also outputs the new database in json format for the frontend

The frontend is an Angular program based on ngx-graph demo. The frontend reads the json file that visualize.py creates and creates graphs.

## Installation
Tested on Ubuntu 18.04.5 LTS Server, should work on other Linux distros too as long as prerequisites are met.
### Prerequisites
Rsyslog
Python 3.7
PIP3
Psycopg2
Numpy



## Coming soon
Simplifying the backend and combining the two python files for easier install.
Making the backend easier to configure, at the moment the MAC-address which is used to track when the user is home is hard coded in to the visualize.py
Simplifying the frontend as it's currently built on top of demo project.

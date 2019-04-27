# mqttbelkinups
a mqtt client for belkin ups via belkin bulldog plus web server

Functions:
  Reads, parses and trasforms into mqtt topics and publish 4 webpages taken from the belkin bulldog plus ups software.
  Create OPENHAB2 things, items and stimap files 

Prerequisites:
  Belkin ups connected via USB or RS232 to a windows machine
  Belkin bulldog plus ups software with webserver enabled
  A machine with python 3.7, paho.mqtt and beautifulsoup4 (it can be any kind of hw supporing python (i tested it on windows and debian machines)

Installation:
  copy upsqtt.py and upsqtt.conf in a directory
  optionally you can add a cron schedule on linux or ar scheduled job on windows
  
Running for the first time
  launch python upsqtt.py, it has 2 command line options:
    -f only create openhab files
    -b create broker definition in UPS.things file, only if also -f is specified on command line
  it will create 3 files, you can place them into the appropiate directory under openhab

Running
  launch python upsqtt.py
  optionally on linux you can create a cron job to start the script every x seconds/minutes/hours tha same on windows.

UPSQTT.CONF
this is the configuration files, it uses an ini like structure:

[upsqtt]
name=belkinups   <------ 

[server]

address = 10.11.12.13  <---- address of the machine running bulldog
port = 6969            <---- bulldog webserver port
user = admin           <---- bulldog webserver auth user
secret = palabrasegreta <--- bulldog webserver password

[broker]
address = broker.example.com   <------ broker address
port = 1833                    <------ broker port
user = mqttUser                <------ broker user
secret = palabrasegreta2       <------ broker password
bridge = yourbridge            <------ openhab2 bridge name (see notes)
keepalive = 30000              <------ broker configuration parameters
reconnect = 60000       
qos = 0
secure = false
retain = false
clientID = mqttUPSClient
root_topic = F6C800xxUNV      <------- root topic to publish, all the topics published will start with i.e. F6C800xxUNV/status

notes: if you already have an mqtt broker bridge defined in openhab please do use -b option and fill broker parameters with the same parameters used in the things file you already have. in other words use -b option only if this is the first mqtt bridge you are defining in openhab2



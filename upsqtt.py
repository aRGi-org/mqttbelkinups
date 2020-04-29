#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 aRGi <info@argi.mooo.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    aRGi Rob - initial implementation

# This is a MQTT client to publish Belkin UPS data as topics.

import configparser
import paho.mqtt.publish as publish
import urllib.request, json 
import sys
from bs4 import BeautifulSoup
import argparse
import time

def queryUPS():
        # get state data and parse them to a dict
        kl=[]
        with urllib.request.urlopen(top_level_url + "state.htm") as rooturl:
            soup = BeautifulSoup(str(rooturl.read().decode()), 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                i = row.findAll(bgcolor=True)
                if len(i) > 0:
                    for k in range(0,len(i)):
                        kl.append([i[k].text.strip().replace(" ","").replace(":","").lower(),'', 'string', i[k].text.strip().replace(":","")])
            lk = 0				
            for row in rows:
                j = row.findAll("font")
                if len(j) > 0:
                    for k in range(0,len(j)):
                        kl[lk][1] = j[k].text.strip()
                    lk=lk+1

        for h in kl:
            upsdata.append(h)
			
        # get main data and parse them to a dict
        with urllib.request.urlopen(top_level_url + "main.htm") as rooturl:
            soup = BeautifulSoup(str(rooturl.read().decode()), 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                i = row.findAll(align="right")
                j = row.findAll(align="center")
                if len(i) > 0 and len(j) >0 and len(i)==len(j):
                    for k in range(0,len(i)):
                        upsdata.append([i[k].text.strip().replace(" ","").replace(":","").lower(),j[k].text.strip(), 'string', i[k].text.strip().replace(":","")])

        # get meters data and parse them to a dict
        with urllib.request.urlopen(top_level_url + "meters.htm") as rooturl:
            soup = BeautifulSoup(str(rooturl.read().decode()), 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                i = row.findAll(align="right")
                j = row.findAll(align="center")
                if len(i) > 0 and len(j) >0 and len(i)==len(j):
                    for k in range(0,len(i)):
                        upsdata.append([i[k].text.strip().replace(" ","").replace(":","").lower(),j[k].text.strip(), 'number', i[k].text.strip().replace(":","")])

        # get status data and parse them to a dict
        with urllib.request.urlopen(top_level_url + "status.htm") as rooturl:
            soup = BeautifulSoup(str(rooturl.read().decode()), 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                i = row.findAll(bgcolor=True)
                j = row.findAll("img")
                if len(i) > 0 and len(j) >0 and len(i)==len(j):
                    for k in range(0,len(i)):
                        upsdata.append([i[k].text.strip().replace(" ","").lower(),"1" if j[k]['src'] == "AlarmOn.jpg" else "0", 'contact', i[k].text.strip()])


def openHabFiles(topics): 
    broker = "Bridge mqtt:broker:" + config['broker']['bridge'] + ' "MQTT broker bridge:' + config['broker']['bridge'] + '" @ "Home" [\n'
    broker += '\thost="' + config['broker']['address'] + '",\n'
    broker += '\tport=' + config['broker']['port'] + ',\n'
    broker += '\tsecure=' + config['broker']['secure'] + ',\n'
    broker += '\tretain=' + config['broker']['retain'] + ',\n'
    broker += '\tclientID="' + config['broker']['clientID'] + '",\n'
    broker += '\tkeepalive=' + config['broker']['keepalive'] + ',\n'
    broker += '\treconnect_time=' + config['broker']['reconnect'] + ',\n'
    broker += '\tusername="' + config['broker']['user'] + '",\n'
    broker += '\tpassword="' + config['broker']['secret'] + '"\n\t]\n'
    things = "\n\tThing mqtt:topic:" + config['broker']['bridge'] + ":" + config['broker']['root_topic'] + ' "Belkin UPS" (mqtt:broker:' + config['broker']['bridge'] + ') @ "Home" {\n\t\tChannels:\n'
    for k in range(0,len(topics)): 
        #print(topic + "/" + upsdata[k][0]," ", upsdata[k][1])	
        things += "\t\t\tType " + topics[k][2] + ":" + topics[k][0].replace("-","") + ' "' +	topics[k][3].replace("-"," ")	+ '" [ stateTopic="' + topic + "/" + topics[k][0] + '" ]\n'
    things += "\t}\n"

    items = ''
    id = 0
    for k in range(0,len(topics)): 
        items += topics[k][2].capitalize() + " UPS_" + topics[k][0].replace("-","") + ' "UPS' + str(id) + '" { channel="mqtt:topic:' + config['broker']['bridge'] + ':' + config['broker']['root_topic'] + ':' + topics[k][0] + '" }\n'
        id += 1	   

    maps = 'sitemap ups label="UPS" {\n\tFrame label="' + config['broker']['root_topic'] + '" icon="poweroutlet_eu" {\n'
    for k in range(0,len(topics)): 
        maps += '\t\t'
        maps +=  "Switch" if topics[k][2] == "contact" else "Text"
        maps += " item=UPS_" + topics[k][0].replace("-","") + ' label="' + topics[k][3].replace("-"," ") + '"\n'
    maps += "\t}\n"
    maps += "}"

    try:
        f = open("ups.things", "w")
        if parsedArgs.brokerdef:
           f.write(broker)
        f.write(things)
        f.close()
        f = open("ups.items", "w")
        f.write(items)
        f.close()
        f = open("ups.sitemap", "w")
        f.write(maps)
        f.close()
    except:
        print("Error Creating openhab configuration files.",sys.exc_info())
	
	
try:
    parser = argparse.ArgumentParser(description='Belkin UPS data to MQTT topics')
    parser.add_argument('-f', action="store_true", default=False, dest="openhabfiles")
    parser.add_argument('-b', action="store_true", default=False, dest="brokerdef")
    parsedArgs = parser.parse_args()
    
    config = configparser.ConfigParser()
    config.read('upsqtt.conf')
except:
    print("Error Reading Configuration File",sys.exc_info())
else:
    try:
        # build ups url
        top_level_url = "http://" + config['server']['address'] + ":" + config['server']['port'] + "/"
        topic = config['upsqtt']['name']
        auth = {'username':config['broker']['user'], 'password':config['broker']['secret']}
        clientId = config['broker']['clientID']
        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password.
        password_mgr.add_password(None, top_level_url, config['server']['user'], config['server']['secret'])
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)	
	
        upsdata = []
        queryUPS()
		#json2topic(upsdata, topic)
        if parsedArgs.openhabfiles:
            openHabFiles(upsdata)
        else:
            while True:
                messages = []
                for k in range(0,len(upsdata)): 
                    onetopic = {
						'topic' : topic + "/" + upsdata[k][0],
						'payload' : upsdata[k][1]
					}
                    messages.append(onetopic)
                publish.multiple(messages, auth=auth, hostname=config['broker']['address'], client_id=clientId)
				# publish.single(topic + "/" + upsdata[k][0], upsdata[k][1], auth=auth, hostname=config['broker']['address'])
                time.sleep(15)
                upsdata = []
                queryUPS()
			
    except:
        print("Error Reading Server configuration",sys.exc_info())


#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  wmd_working.py
#
#  Copyright 2013 Brandon Knight <kaospunk@gmail.com>
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
import os
import glob
import re
import time
import sys
import shutil
import datetime
from threading import Thread, Event
from Queue import Queue
from EspeakDriver import EspeakDriver
import subprocess
import signal
from FrequencyGenerator import FrequencyGenerator
from Adafruit_CharLCDPlate import *

main_airo = None

def handle(signal,frm):
	print("Shutting down")
	main_airo.terminate()
	subprocess.Popen(["airmon-ng","stop", "mon0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	lcd.clear()
	lcd.stop()
	sys.exit(1)	

signal.signal(signal.SIGINT,handle)	

def start_airo():
	global main_airo
	main_airo = subprocess.Popen(["airodump-ng","-w", "main_airo", "mon0"],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))

def color_cycle():
	col = (('Red' , lcd.RED) , ('Yellow', lcd.YELLOW), ('Green' , lcd.GREEN),
           ('Teal', lcd.TEAL), ('Blue'  , lcd.BLUE)  , ('Violet', lcd.VIOLET),
           ('Off' , lcd.OFF) , ('On'    , lcd.ON))

	for color in col:
		lcd.backlight(color[1])
		sleep(0.1)


def rssi_tone(dfile):
	latest_track = 0
	latest_file = ''

	os.chdir(base_dir)
	lcd.backlight(lcd.RED)
	lcd.clear()
	lcd.message("Locking on")
	vals = dfile.split("_")
	essidtemp = vals[6:]
	essid = None
	if type(essid) == str:
		essid = essidtemp
	else:
		essid = "_".join(essidtemp)
	
	signal = True
#	tone = FrequencyGenerator()
	while True and signal:
	   if not rssi_event.is_set():
		break
	   if latest_file == '':
             for file in [f for f in glob.glob(dfile + "*.csv") if "kismet" not in f]:
                if os.path.getmtime(file) > latest_track:
                        latest_track = os.path.getmtime(file)
                        latest_file = file

           if latest_file != '':
                csv = open(base_dir + '/' + latest_file, 'r')
		count = 0
		for line in csv:
			if count == 2:
				params = line.split(",")
				(date,ltime) = params[2].strip().split(" ")
				(year,month,day) = date.strip().split("-")
				(hour,minute,second) = ltime.split(":")
				lastseen = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second))
				delta = datetime.datetime.now() - lastseen
				if delta.total_seconds() > 60:
					lcd.clear()
					lcd.message("Signal Lost")
					time.sleep(2)
					signal = False	
					return
				abs_value = abs(int(params[8]))
				freq = float(2.5/abs_value) * 10000
				lcd.clear()
				lcd.message("Target: {0}dbi\n{1}".format(params[8],essid))
			#	proc = subprocess.Popen(['/usr/bin/speaker-test', '-t', 'sine', '-f', str(freq),'-l', '1'],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))
			#	proc.wait()
				tone.sine_wave(freq)
				#tone.frequency = freq
				#time.sleep(0.1)
				break
			count += 1

def update_whitelist():
	del good_aps[:]
	try:
		source_file = open('/media/usbdevice/apwhitelist.txt','r')
		output_string = '' 
		for ap in source_file:
        		good_aps.append(ap.rstrip())
			output_string += ap
			for rogue in rogue_aps:
				if rogue[1] == ap.rstrip():
					rogue_aps.remove(rogue)
		dest_file = open(base_dir + '/apwhitelist.txt','w')
		dest_file.write(output_string)	
		return "Success"
	except Exception as e:
		return "Error occurred"

def backup_files():
	try:
		for file in glob.glob("*.csv"):
			shutil.copy(file,'/media/usbdevice/' + file)
		for file in glob.glob("*.cap"):
			shutil.copy(file,'/media/usbdevice/' + file)
		for file in glob.glob("*.netxml"):
			shutil.copy(file,'/media/usbdevice/' + file)
		return "Success"
	except Exception as e:
		return "Error occurred"

def main_menu():
	list = ['View Rogues','Update Whitelist','Backup Files','Clear Rogues']
	t_event.wait()
	current_pointer = 0
	secret_counter = 0
        while True:
                lcd.clear()
                lcd.message("Main Menu:\n{0}".format(list[current_pointer]))
                result = get_button_press(lcd)
                if result == "Up":
                        current_pointer -= 1
                        if abs(current_pointer) == len(list):
                                current_pointer = 0
                        lcd.clear()
                	lcd.message("Main Menu:\n{0}".format(list[current_pointer]))
                elif result == "Down":
                        current_pointer += 1
                        if abs(current_pointer) == len(list):
                                current_pointer = 0
                        lcd.clear()
                	lcd.message("Main Menu:\n{0}".format(list[current_pointer]))
		elif result == "Left":
			secret_counter += 1
			if secret_counter == 3:
				lcd.backlight(lcd.GREEN)
				tone.zelda_secret()
				secret_counter = 0
                elif result == "Select":
			if list[current_pointer] == 'Update Whitelist':
				result = update_whitelist()
				lcd.clear()
				lcd.message(result)
				time.sleep(2)
			if list[current_pointer] == 'Backup Files':
				result = backup_files()
				lcd.clear()
				lcd.message(result)
				time.sleep(2)
			elif list[current_pointer] == 'View Rogues': 
				t_event.set()
				return
			elif list[current_pointer] == 'Clear Rogues': 
				del parse_tracker[:]

def get_wlan(lcd):
	wireless_cards = []
	current_pointer = 0
	wlan = subprocess.Popen(["iwconfig"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while True:
		line = wlan.stdout.readline()
		if not line:
			break
		elif "wlan" in line:
			wireless_cards.append(line.split(" ")[0])
	if wireless_cards > 0:
	   while True:
		lcd.clear()
       		lcd.message("Select wlan:\n{0}".format(wireless_cards[current_pointer]))
        	result = get_button_press(lcd)
        	if result == "Up":
                	current_pointer -= 1
                	if abs(current_pointer) == len(wireless_cards):
                        	current_pointer = 0
                	lcd.clear()
       			lcd.message("Select wlan:\n{0}".format(wireless_cards[current_pointer]))
        	elif result == "Down":
                	current_pointer += 1
                	if abs(current_pointer) == len(wireless_cards):
                        	current_pointer = 0
                	lcd.clear()
       			lcd.message("Select wlan:\n{0}".format(wireless_cards[current_pointer]))
        	elif result == "Select":
			lcd.clear()
			lcd.message("Starting\nDetection")
			subprocess.Popen(["airmon-ng","start", wireless_cards[current_pointer]],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))
			time.sleep(5)
			start_airo()
			break

def locate_rogue(bssid, essid, chan,lcd):
	main_airo.terminate()
	time.sleep(1)
	buttons = ((lcd.SELECT, 'Select', lcd.ON),
           (lcd.LEFT  , 'Left'  , lcd.RED),
           (lcd.UP    , 'Up'    , lcd.BLUE),
           (lcd.DOWN  , 'Down'  , lcd.GREEN),
           (lcd.RIGHT , 'Right' , lcd.VIOLET))
          
	new_bssid = bssid.replace(":","_")
	locate = subprocess.Popen(["airodump-ng", "--bssid", bssid, "--channel", chan, "-w", "{0}_{1}".format(new_bssid, essid), "mon0"],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))
	rssi_event.set()	
	rssi = Thread(target=rssi_tone,args=("{0}_{1}".format(new_bssid, essid),))
	rssi.start()

	button_pushed = False
        while True and rssi.is_alive():
	  if button_pushed:
		break
          for b in buttons:
            if lcd.buttonPressed(b[0]):
		if b[1] == "Select":
			button_pushed = True
			rssi_event.clear()

	locate.terminate()
	lcd.backlight(lcd.BLUE)
	lcd.clear()
	return
	
def get_button_press(lcd):
	time.sleep(0.5)
	btn = ((lcd.SELECT, 'Select', lcd.ON),
           (lcd.LEFT  , 'Left'  , lcd.RED),
           (lcd.UP    , 'Up'    , lcd.BLUE),
           (lcd.DOWN  , 'Down'  , lcd.GREEN),
           (lcd.RIGHT , 'Right' , lcd.VIOLET))
    	while True:
          for b in btn:
            if lcd.buttonPressed(b[0]):
		    return b[1]

def scroll_list():
  current_pointer = 0
  while True:
   if t_event.is_set():
    if len(rogue_aps) > 0:
      lcd.clear()
      lcd.message("Potential Target\n{0}".format(rogue_aps[current_pointer][0]))
      while True:	
	result = get_button_press(lcd)
	if result == "Up":
		current_pointer -= 1
		if abs(current_pointer) == len(rogue_aps):
			current_pointer = 0
		lcd.clear()
 		lcd.message("Potential Target\n{0}".format(rogue_aps[current_pointer][0]))
	elif result == "Down":
		current_pointer += 1
		if abs(current_pointer) == len(rogue_aps):
			current_pointer = 0	
 		lcd.clear()
 		lcd.message("Potential Target\n{0}".format(rogue_aps[current_pointer][0]))
	elif result == "Left":
		main_menu()
		current_pointer = 0
 		lcd.clear()
 		lcd.message("Potential Target\n{0}".format(rogue_aps[current_pointer][0]))
	elif result == "Right":
		lcd.scrollDisplayLeft()
	elif result == "Select":
                locate_rogue(rogue_aps[current_pointer][1], rogue_aps[current_pointer][0], rogue_aps[current_pointer][2],lcd)
                start_airo()
 		lcd.clear()
 		lcd.message("Potential Target\n{0}".format(rogue_aps[current_pointer][0]))


def lcd_display(msg):
	lcd = Adafruit_CharLCDPlate()
	lcd.begin(16, 2)
	lcd.backlight(lcd.GREEN)
	lcd.message(msg)
	return


base_dir = '/home/securestate'

lcd = Adafruit_CharLCDPlate()
lcd.begin(16, 2)
time.sleep(0.5)
lcd.backlight(lcd.BLUE)
lcd.clear()

latest_track = 0
MINIMUM_SIGNAL = -110
latest_file = ''
rogue_aps = []
good_aps = []
target_processed = []
espeak_drv = EspeakDriver.EspeakDriver()

#Build list of good aps
ap_file = open(base_dir + '/apwhitelist.txt', 'r')
for ap in ap_file:
	good_aps.append(ap.rstrip())

os.chdir(base_dir)

#Cleanup
for oldfile in glob.glob("*.csv"):
	os.unlink(oldfile)
for oldfile in glob.glob("*.cap"):
	os.unlink(oldfile)
for oldfile in glob.glob("*.netxml"):
	os.unlink(oldfile)


get_wlan(lcd)
current_pointer = 0
parse_tracker = []
def parser():
    latest_file = ''
    latest_track = 0
    global parse_tracker
    #local_tracker = []
    while True:
	for file in glob.glob("main_airo*.kismet.csv"):
		if os.path.getmtime(file) > latest_track:
			latest_track = os.path.getmtime(file)
			latest_file = file

	if latest_file != '':
		csv = open(base_dir + '/' + latest_file, 'r')
		for line in csv:
			params = line.split(";")
			if params[0] != 'Network':
			  if len(params) == 39:
				if params[3] not in parse_tracker and params[3] not in good_aps and int(params[21]) > MINIMUM_SIGNAL and params[2] != '':
				#	local_tracker.append(params[3])
					parse_tracker.append(params[3])
					q.put_nowait((params[2],params[3],params[5]))
					print("New rogue AP found with name: {0}").format(params[2])
					espeak_drv.speak('New Rogue AP found with name' + params[2])
		
	time.sleep(1)


q = Queue()
t = Thread(target=parser)
t.daemon = True
t.start() 

t_event =Event()
t_event.set()
rssi_event = Event()
rssi_event.set()
scroller = Thread(target=scroll_list)
scroller.daemon = True
scroller.start()
tone = FrequencyGenerator()
main_menu()
while True:
	if q.empty() == False:	
		(essid,bssid,chan) = q.get()
		rogue_aps.append((essid,bssid,chan))

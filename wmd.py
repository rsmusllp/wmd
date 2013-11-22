#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  wmd.py
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
import time
from threading import Thread
from Queue import Queue
from EspeakDriver import EspeakDriver
import subprocess
from Adafruit_CharLCDPlate import *

main_airo = None

def start_airo():
	global main_airo
	main_airo = subprocess.Popen(["airodump-ng","-w", "main_airo", "mon0"],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))

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
			sleep(2)
			start_airo()
			break

def locate_rogue(bssid, essid, chan,lcd):
	print("Targeting: " + bssid + " " + essid + " " + chan)
	main_airo.terminate()
	time.sleep(1)
	lcd.clear()
	lcd.backlight(lcd.RED)
	lcd.message("Target Aquired:\n" + essid)
	buttons = ((lcd.SELECT, 'Select', lcd.ON),
           (lcd.LEFT  , 'Left'  , lcd.RED),
           (lcd.UP    , 'Up'    , lcd.BLUE),
           (lcd.DOWN  , 'Down'  , lcd.GREEN),
           (lcd.RIGHT , 'Right' , lcd.VIOLET))
           
	locate = subprocess.Popen(["airodump-ng", "--bssid", bssid, "--channel", chan, "-w", "{0}_{1}".format(bssid, essid), "mon0"],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))
	
	rssi = subprocess.Popen(["/usr/bin/python","wmd_airodump_csv_rssi.py","{0}_{1}".format(bssid,essid)],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))
	
	button = None
	while button != "Select":
		button = get_button_press(lcd)
	rssi.terminate()
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
		lcd.scrollDisplayRight()
	elif result == "Right":
		lcd.scrollDisplayLeft()
	elif result == "Select":
		locate_rogue(rogue_aps[current_pointer][1], rogue_aps[current_pointer][0], rogue_aps[current_pointer][2],lcd)
		start_airo()

def lcd_display(msg):
	lcd = Adafruit_CharLCDPlate()
	lcd.begin(16, 2)
	lcd.backlight(lcd.GREEN)
	lcd.message(msg)
	return
	
def parser():
    latest_file = ''
    latest_track = 0
    local_tracker = []
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
			  if len(params) > 21:
				if params[2] not in local_tracker and params[2] not in good_aps and int(params[21]) > MINIMUM_SIGNAL and params[2] != '':
					local_tracker.append(params[2])
					q.put_nowait((params[2],params[3],params[5]))
					print("New rogue AP found with name: {0}").format(params[2])
					espeak_drv.speak('New Rogue AP found with name' + params[2])
	time.sleep(1)


base_dir = '/home/securestate'

lcd = Adafruit_CharLCDPlate()
lcd.begin(16, 2)
time.sleep(0.5)
lcd.backlight(lcd.BLUE)
lcd.clear()

MINIMUM_SIGNAL = -110
rogue_aps = []
good_aps = []
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

q = Queue()
parser = Thread(target=parser)
parser.daemon = True
parser.start() 
scroller = Thread(target=scroll_list)
scroller.daemon = True
scroller.start()
while True:
	if q.empty() == False:	
		(essid,bssid,chan) = q.get()
		rogue_aps.append((essid,bssid,chan))

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  wmd_kismet_parse.py
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
from EspeakDriver import EspeakDriver
import subprocess
from Adafruit_CharLCDPlate import *

def start_airo():
	main_airo = subprocess.Popen(["airodump-ng","-w", "main_airo", "mon0"],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))
	return main_airo

def locate_rogue(bssid, essid, chan,lcd,main_airo):
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
	#RSSI audio code will go here
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
	time.sleep(1)
	btn = ((lcd.SELECT, 'Select', lcd.ON),
           (lcd.LEFT  , 'Left'  , lcd.RED),
           (lcd.UP    , 'Up'    , lcd.BLUE),
           (lcd.DOWN  , 'Down'  , lcd.GREEN),
           (lcd.RIGHT , 'Right' , lcd.VIOLET))
	prev = -1
    	while True:
          for b in btn:
            if lcd.buttonPressed(b[0]):
                if b is not prev:
		    return b[1]
                  #  prev = b
                #break

def scroll_list(lcd,current_pointer):
 	lcd.clear()
 	lcd.message("Potential Target\n{0}".format(rogue_aps[current_pointer]))
	result = get_button_press(lcd)
	if result == "Up":
		current_pointer -= 1
		if abs(current_pointer == len(rogue_aps)):
			current_pointer = 0
			return current_pointer
	elif result == "Down":
		current_pointer += 1
		if abs(current_pointer == len(rogue_aps)):
			current_pointer = 0	
			return current_pointer
	return current_pointer

def lcd_display(msg):
	lcd = Adafruit_CharLCDPlate()
	lcd.begin(16, 2)
	lcd.backlight(lcd.GREEN)
	lcd.message(msg)
	return


base_dir = '/home/securestate'

lcd = Adafruit_CharLCDPlate()
lcd.begin(16, 2)
time.sleep(1)
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

lcd.message("Press Select to\nbegin")
button = None
while button != "Select":
	button = get_button_press(lcd)

lcd.clear()
subprocess.Popen(["airmon-ng","start", "wlan1"],bufsize=0,stdout=open("/dev/null", "w"),stderr=open("/dev/null", "w"))
sleep(2)

main_airo = start_airo()
current_pointer = 0
while 1:
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
				if params[2] not in rogue_aps and params[2] not in good_aps and int(params[21]) > MINIMUM_SIGNAL and params[2] != '':
					rogue_aps.append(params[2])
					print("New rogue AP found with name: {0}").format(params[2])
					espeak_drv.speak('New Rogue AP found with name' + params[2])
					#locate = raw_input("Would you like to locate this AP? (y/n):").lower()
					# This is all to simulate a button press on the the Rpi which confirms that the AP should be located
					tgtmsg = "Target\n{0}".format(params[2])
					lcd.clear()
					lcd.message(tgtmsg)
					result = get_button_press(lcd)
					if str(result) == "Up" or str(result) == "Down":
						bssid = params[3]
						essid = params[2]
						chan = params[5]
						lcd.clear()
						lcd.message(essid)
						print(bssid + " " + essid + " " + chan )
						locate_rogue(bssid, essid, chan,lcd,main_airo)
						main_airo = start_airo()
						break
						# print("RESULTS {0}").format(results)
					elif str(result) == "Left" or str(result) == "Right":
						lcd.clear()	
					else:
						pass
#	if len(rogue_aps) > 0:
#		current_pointer = scroll_list(lcd,current_pointer)
	time.sleep(1)


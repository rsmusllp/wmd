#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wmd_launcher.py
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
import argparse
import os
import glob

class detector():
	

	def bssid_match(self, control, test, wildcards = True):
	        
	        control = control.lower().split(':')
	        test = test.lower().split(':')
	        if len(control) != 6 or len(test) != 6:
	                raise Exception('malformed MAC')
	        for i in xrange(0, 6):
	                if wildcards and control[i] == '*':
	                        continue
	                if control[i] != test[i]:
	                        return False
	        return True


	def lister(self, strength, whitelist):

		if strength == 'strong':
			minpower = int(-50)
		elif strength == 'medium':
			minpower = int(-70)
		else:
			minpower = int(-110)
		latest_track = 0
		latest_file = ''
		
		for file in glob.glob("*.kismet.csv"):
			if os.path.getmtime(file) > latest_track:
				latest_track = os.path.getmtime(file)
				latest_file = file

		
		with open(file, 'r') as infile:
			inlines = infile.readlines()
		bssids = []
		essids = []
		signals = []
		allaps = {}
			
		for line in inlines:
			line = line.split(';')
			try:
				sigstrength = int(line[21])
			except ValueError:
				continue
			if sigstrength > minpower:
				essids.append(line[2])
				bssids.append(line[3])
				signals.append(line[21])
		
		#print('Signal Strengths:\n')
		#print(signals)
		for i in range(len(bssids)):
			allaps[bssids[i]] = essids[i]
		
		with open(whitelist, 'r') as whitelist:
			whitelistedaps = whitelist.readlines()
		whitelistedaps = map(lambda x: x.strip(), whitelistedaps)
		#rogueaps = filter(lambda x: x not in whitelistedaps, allaps.keys())
		rogueaps =[]
		for bssid in allaps.keys():
			if filter(lambda b: self.bssid_match(b, bssid), whitelistedaps):
				continue
			rogueaps.append(bssid)
					
		
		if len(rogueaps) == 0:
			print("\nNo Rogue APs were detected at the specified signal strength.")
		else:	
			print("\nRogue APs Identified:\n")
			for rogue in rogueaps:
				print(rogue)
		#print("\nAll APs:\n")
		#print(allaps)
		infile.close()
		whitelist.close()

	
	#def screen_h(self, rogues):
		
		#for rogue in rogues:
			#code to print rogue to screen

parser=argparse.ArgumentParser(description='Display rogue access points that meet signal specifications.')
parser.add_argument('-s', '--strong', help='display only rogues with strongest strength signal', action='store_true')
parser.add_argument('-m', '--medium', help='display rogues with medium and stronger strength signals', action='store_true')
parser.add_argument('-e', '--everything', help='display all rogues regardless of signal strength', action='store_true')
parser.add_argument('-f', '--file', help='file containing whitelisted access points', default='apwhitelist.txt')

args=parser.parse_args()

nd = detector()
whitelist = args.file
if args.strong:
	strength = 'strong'
	nd.lister(strength, whitelist)
elif args.medium:
	strength = 'medium'
	nd.lister(strength, whitelist)
else:
	strength = 'everything'
	nd.lister(strength, whitelist)
	

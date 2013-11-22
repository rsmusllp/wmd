#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wmd_airodump_csv_rssi.py
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
import subprocess
import argparse

base_dir = '/home/securestate'

latest_track = 0
latest_file = ''

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

os.chdir(base_dir)
while 1:
        for file in [f for f in glob.glob(args.file + "*.csv") if "kismet" not in f]:
                if os.path.getmtime(file) > latest_track:
                        latest_track = os.path.getmtime(file)
                        latest_file = file

        if latest_file != '':
                csv = open(base_dir + '/' + latest_file, 'r')
		count = 0
		for line in csv:
			if count == 2:
				params = line.split(",")
				abs_value = abs(int(params[8]))
				freq = float(2.5/abs_value) * 10000
				print abs_value
				print str(freq)
				proc = subprocess.Popen(['/usr/bin/speaker-test', '-t', 'sine', '-f', str(freq),'-l', '1'],bufsize=0,stdout=None,stderr=open("/dev/null", "w"))
				proc.wait()
				break
			count += 1
#	time.sleep(1)

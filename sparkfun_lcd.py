#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  sparkfun_lcd.py
#
#  Copyright 2013 Spencer McIntyre <zeroSteiner@gmail.com>
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
#

import serial

class LCDDisplay(object):
	def __init__(self, device = '/dev/ttyAMA0'):
		self.device = device
		self.serial_h = serial.Serial(device, 9600, timeout = 0.1)
		self.clear()
		self.set_brightness(0.5)

	def clear(self):
		self.serial_h.write(chr(0xfe) + chr(0x01))

	def off(self):
		self.set_brightness(0)

	def set_brightness(self, level):
		assert(level >= 0 and level <= 1)
		level = 128 + int(level * 29)
		self.serial_h.write(chr(0x7c) + chr(level))

	def write(self, line, row = 0):
		self.set_cursor(0, row)
		self.serial_h.write(line)

	def set_blink_cursor(self, value):
		if value:
			self.serial_h.write(chr(0xfe) + chr(0x0d))
		else:
			self.set_clear_cursor()

	def set_underline_cursor(self, value):
		if value:
			self.serial_h.write(chr(0xfe) + chr(0x0e))
		else:
			self.set_clear_cursor()

	def set_clear_cursor(self):
		self.serial_h.write(chr(0xfe) + chr(0x0c))

	def set_cursor(self, column, row):
		assert(row in range(0, 2))
		assert(column in range(0, 16))
		if row == 0:
			pos = 128 + column
		elif row == 1:
			pos = 128 + 64 + column
		self.serial_h.write(chr(0xfe) + chr(pos))

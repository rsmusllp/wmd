#!/bin/bash

if [ -f /media/usbdevice/apwhitelist.txt ] 
then
      if [ ! -f /home/securestate/apwhitelist.txt ]
      then
            echo No existing whitelist file. Populating from USB
            cp /media/usbdevice/apwhitelist.txt /home/securestate/apwhitelist.txt
      else
	if [ /media/usbdevice/apwhitelist.txt -nt /home/securestate/apwhitelist.txt ]
	then
	     echo Newer file found on USB drive
	     cp /media/usbdevice/apwhitelist.txt /home/securestate/apwhitelist.txt
	fi
      fi
fi

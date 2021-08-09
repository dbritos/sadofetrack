#!/usr/bin/python
# import os, sys
import serial #Import module
import csv

ValidModes = {'USB':'2', 'LSB':'1', 'CW':'3', 'CWR':'3', 'RTTY':'6', 'RTTYR':'9', 'AM':'5', 'FM':'4', 'NFM':'4', 'AMS':'5', 'PKTLSB':'8', 'PKTUSB':'C', 'PKTFM':'A', 'ECSSUSB':'2', 'ECSSLSB':'1', 'FAX':'4', 'SAM':'5', 'SAL':'5', 'SAH':'5', 'DSB': '1','67Hz':'4','DMR':'E','':'4'}
Tone = {'74.4':'003','77.0':'004','82.5':'006','88.5':'008','94.8':'010','103.5':'013','107.2':'014','110.9':'015','118.8':'017','123.0':'018','131.8':'020','136.5':'021'}
Simplex = ["","+","-"]
P10 = ["0","1","2"]
portx="/dev/serial/by-id/usb-Silicon_Labs_CP2105_Dual_USB_to_UART_Bridge_Controller_00EA619F-if00-port0"
  #Baud rate, one of the standard values: 50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
bps=38400
#time-out,None: Always wait for the operation, 0 to return the request result immediately, and the other values are waiting time-out.(In seconds)
timex=5
# Open the serial port and get the serial object
ser=serial.Serial(portx,bps,timeout=timex)
MT = "CT01;"
result=ser.write(MT .encode("ascii"))
print("Write total bytes:",len(MT),"-----",MT,"\n")
MT = "CN00000;"
result=ser.write(MT .encode("ascii"))
print("Write total bytes:",len(MT),"-----",MT,"\n")

ser.close()#Close serial port

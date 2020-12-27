#!/usr/bin/env python
import subprocess
import pathlib
import time
from tkinter import *
from tkinter.ttk import *
import urllib.request
import sattracker3
import re
import pickle

root = Tk()
root.title("Satellite Doppler Ferequency Tracker")
root.geometry('500x250')

#get configuration file
if pathlib.Path('config.pkl').is_file():
	with open('config.pkl','rb') as f:  # Python 3: open(..., 'rb')
	    serial_port_selected,rig_selected,rig_num = pickle.load(f)
else:
	serial_port_selected="/dev/tty0"
	rig_selected="FLRig"

#get serial port
def select_serial_port(event):
	global serial_port_selected
	serial_port_selected=event.widget.get()

serial_port = Combobox(root)
status,output = subprocess.getstatusoutput("ls /dev/tty*")
serial_port_list =output.split('\n')
serial_port['values']= serial_port_list
serial_port.current(1) #set the selected item
serial_port.grid(column=0, row=0)
serial_port.bind("<<ComboboxSelected>>", select_serial_port)
serial_port.current(serial_port_list.index(serial_port_selected))

#get rig
def selectrig(event):
	global rig_selected
	rig_selected = event.widget.get()
	global rig_num
	rig_num = dic_rig[rig_selected]
rig = Combobox(root)
rig_list = list()
rig_listn = list()
dic_rig = {}
status,output = subprocess.getstatusoutput("rigctld -l | grep -v '^[1-9]'")
rigs = output.split('\n')
for r in rigs:
	if len(r) >= 70:
		name = r[28:51].rstrip().lstrip()
		number =r[0:7].rstrip().lstrip()
		rig_list.append(name)
		dic_rig[name]=number

rig['values']= rig_list
rig.current(rig_list.index(rig_selected)) #set the selected item
rig.grid(column=1, row=0)
rig.bind("<<ComboboxSelected>>", selectrig)

#get satellite
satellite_selected = False
sat_list = list()
list_tle = list()
dic_tle = {}
list_fqc = list()
dic_fqc = {}
file = urllib.request.urlopen("https://www.celestrak.com/NORAD/elements/stations.txt")
for line in file:
	list_tle.append(line.decode('utf-8').rstrip('\n\r'))

file = urllib.request.urlopen("https://www.amsat.org/tle/current/nasabare.txt")
for line in file:
	list_tle.append(line.decode('utf-8').rstrip('\n\r'))	

for itn in range(0,len(list_tle),3): 
	nserie=list_tle[itn+1].split()[1]
	item_tle = {"name": list_tle[itn].rstrip(),"tle1":list_tle[itn+1], "tle2":list_tle[itn+2]}
	dic_tle[nserie.rstrip()] = item_tle	

file = urllib.request.urlopen("http://www.ne.jp/asahi/hamradio/je9pel/satslist.csv")
for line in file:
	l1=line.decode('utf-8').rstrip('\n\r').split(";")
	list_fqc.append(l1)
nr = 0
for itn in range(0,len(list_fqc)): 
	if (list_fqc[itn][7] == "active") and (list_fqc[itn][1]+"U" in dic_tle.keys()):
		item_fqc = {"satellite": list_fqc[itn][0].rstrip(),
		"Number":list_fqc[itn][1], 
		"Uplink":list_fqc[itn][2],
		"Downlink":list_fqc[itn][3],
		"Beacon":list_fqc[itn][4], 
		"Mode":list_fqc[itn][5],
		"Callsign":list_fqc[itn][6],
		"tle": dic_tle[list_fqc[itn][1]+"U"]}
		if list_fqc[itn][0] in dic_fqc.keys():
			nr=nr+1
			dic_fqc[list_fqc[itn][0]+str(nr)] = item_fqc
		else:
			dic_fqc[list_fqc[itn][0]] = item_fqc
			nr=0
for l in dic_fqc.keys(): sat_list.append(l)	

satellite = Combobox(root)
satellite['values'] = sat_list
satellite.current(1) #set the selected item
satellite.grid(column=0, row=1)

#save configuration
def save_data():
	with open('config.pkl', 'wb') as f: 
	    pickle.dump([serial_port_selected,rig_selected,rig_num], f)

save = Button(root, text="Save", command=save_data)
save.grid(column=3, row=0)
start_es = False

#start tracking
def start_scn():
	ec1_tle = dic_fqc[satellite.get()]["tle"]
	global f0
	
	f0 = float(re.split('[-/]',dic_fqc[satellite.get()]["Downlink"])[0])*1000000
	tallinn = ("-31.319493", "-64.273951", "500")
	global tracker
	tracker = sattracker3.Tracker(satellite=ec1_tle, groundstation=tallinn)
	global start_es
	start_es = True

start = Button(root, text="Start", command=start_scn)
start.grid(column=2, row=2)

#stop tracking
def stop_scn():
	global start_es
	start_es = False
stop = Button(root, text="Stop", command=stop_scn)
stop.grid(column=3, row=2)

#get parameter and control frequency receiver
Azimut = Label(root, text="Azimut            :",font=("Arial Bold", 20))
Azimut.grid(row=3, columnspan=3,sticky=W)
Elevation = Label(root, text="Elevation         :",font=("Arial Bold", 20))
Elevation.grid(row=4, columnspan=3,sticky=W)
Range = Label(root, text="Range             :",font=("Arial Bold", 20))
Range.grid(row=5, columnspan=3,sticky=W)
FreqDownload = Label(root, text="Frequency Download:",font=("Arial Bold", 20))
FreqDownload.grid(row=6, columnspan=3,sticky=W)
def Control_freq():
	
	if start_es:
		tracker.set_epoch(time.time())
		Az = "Azimut            :"+str(int(tracker.azimuth()))
		Azimut.configure(text=Az)
		El = "Elevation         :"+str(int(tracker.elevation()))
		Elevation.configure(text=El)
		Ra = "Range             :"+str(int((tracker.range()/1000)))+" Km"
		Range.configure(text=Ra)
#		print ("range rate : %0.3f km/s" % (tracker.satellite.range_velocity/1000))
		frec = tracker.doppler(100e6)*f0/100000000+f0
		FD="Frequency Download:"+str(int(frec)) + " Hz"
		FreqDownload.configure(text=FD)
		cmd = "rigctl -m " + rig_num +" -r " + serial_port_selected +" F " + str(int(frec)) + " M " + "FM" + " " + "8000" 
		print(cmd) 
		status,output = subprocess.getstatusoutput(cmd)
	root.after(2000, Control_freq) 

quit = Button(root, text="Quit", command = root.destroy)
quit.grid(column=3, row=7)
		
root.after(2000, Control_freq) 
root.mainloop()
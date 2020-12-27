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
root.geometry('600x300')

#get configuration file
if pathlib.Path('config.pkl').is_file():
	with open('config.pkl','rb') as f:  # Python 3: open(..., 'rb')
	    serial_port_selected,rig_selected,rig_num,lat,lon = pickle.load(f)
else:
	serial_port_selected="/dev/tty0"
	rig_selected="FLRig"
	rig_num=4
	lat = -31.319493
	lon = -64.273951

#get serial port
def select_serial_port(event):
	global serial_port_selected
	serial_port_selected=event.widget.get()

serial_port = Combobox(root)
status,output = subprocess.getstatusoutput("ls /dev/tty*")
serial_port_list =output.split('\n')
serial_port['values']= serial_port_list
serial_port.current(1) #set the selected item
serial_port.grid(column=0, row=0,columnspan=2)
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
rig.grid(column=2, row=0,columnspan=2)
rig.bind("<<ComboboxSelected>>", selectrig)

#get local coordinates
lat_lb = Label(root, text="Latitude:")
lat_lb.grid(row=1, column=0,sticky=W,columnspan=2)
lat_entry= Entry(root)
lat_entry.insert(0, str(lat))
lat_entry.grid(row=1, column=2,sticky=W,columnspan=2)
lon_lb = Label(root, text="Longitude:")
lon_lb.grid(row=2, column=0,sticky=W,columnspan=2)
lon_entry= Entry(root)
lon_entry.insert(0, str(lon))
lon_entry.grid(row=2, column=2,sticky=W,columnspan=2)




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

def selec_frequency(event):
	global f0
	f0 = float(event.widget.get())*1000000

#get frequency
frequency  = Combobox(root)
frequency.grid(column=2, row=3,columnspan=2)
frequency.bind("<<ComboboxSelected>>", selec_frequency)
frequency['values'] ="437.229"
frequency.current(0)
def selec_satellite(event):
	global ec1_tle
	global f0
	global Mode_tx
	ec1_tle = dic_fqc[event.widget.get()]["tle"]
	frequencys = re.split('[\*\-/]',dic_fqc[event.widget.get()]["Downlink"])
	frequencys[:] = [item for item in frequencys if item != '']
	frequency['values'] =frequencys
	f0 = float(frequencys[0])*1000000
	Mode_tx = dic_fqc[event.widget.get()]["Mode"]


satellite = Combobox(root)
satellite['values'] = sat_list
satellite.current(1) #set the selected item
satellite.grid(column=0, row=3,columnspan=2)
satellite.bind("<<ComboboxSelected>>", selec_satellite)
#save configuration
def save_data():
	global lat
	global lon
	try:
		if (float(lat_entry.get()) >= -90) and (float(lat_entry.get())) <= 90:
			lat = lat_entry.get()
			
		else:
			lat_entry.insert(0, "ERROR")
	except: lat_entry.insert(0, "ERROR")
	try:
		if float(lon_entry.get()) >= -180 and float(lon_entry.get()) <= 180:
			lon = lon_entry.get()
		
		else:
			lon_entry.insert(0, "ERROR")
	except:	lon = lon_entry.get()

	with open('config.pkl', 'wb') as f: 
	    pickle.dump([serial_port_selected,rig_selected,rig_num,lat,lon], f)

save = Button(root, text="Save", command=save_data)
save.grid(column=5, row=0)
start_es = False

#start tracking
def start_scn():
#	ec1_tle = dic_fqc[satellite.get()]["tle"]
#	global f0

#	f0 = float(re.split('[\*\-/]',dic_fqc[satellite.get()]["Downlink"])[0])*1000000
	tallinn = (lat,lon, "500")
	global tracker
	tracker = sattracker3.Tracker(satellite=ec1_tle, groundstation=tallinn)
	global start_es
	start_es = True

start = Button(root, text="Start", command=start_scn)
start.grid(column=5, row=3)

#stop tracking
def stop_scn():
	global start_es
	start_es = False
stop = Button(root, text="Stop", command=stop_scn)
stop.grid(column=6, row=3)

#get parameter and control frequency receiver
Azimut = Label(root, text="Azimut            :",font=("Arial Bold", 20))
Azimut.grid(row=5, columnspan=7,sticky=W)
Elevation = Label(root, text="Elevation         :",font=("Arial Bold", 20))
Elevation.grid(row=6, columnspan=7,sticky=W)
Range = Label(root, text="Range             :",font=("Arial Bold", 20))
Range.grid(row=7, columnspan=7,sticky=W)
FreqDownload = Label(root, text="Frequency Download:",font=("Arial Bold", 20))
FreqDownload.grid(row=8, columnspan=7,sticky=W)
Mode = Label(root, text="Mode              :",font=("Arial Bold", 20))
Mode.grid(row=9, columnspan=7,sticky=W)


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
		Mo = "Mode              :" + Mode_tx
		Mode. configure(text=Mo)		
		cmd = "rigctl -m " + str(rig_num) +" -r " + serial_port_selected +" F " + str(int(frec)) + " M " + "FM" + " " + "8000" 
		print(cmd) 
		status,output = subprocess.getstatusoutput(cmd)

	root.after(2000, Control_freq) 

quit = Button(root, text="Quit", command = root.destroy)
quit.grid(column=6, row=10)
		
root.after(2000, Control_freq) 
root.mainloop()
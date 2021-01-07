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
def select_serial_port(event):
	global serial_port_selected
	serial_port_selected=event.widget.get()

def selectrig(event):
	global rig_selected
	rig_selected = event.widget.get()
	global rig_num
	rig_num = dic_rig[rig_selected]

def get_satellite(SatAct):

	global ec1_tle
	global Mode_tx
	global tracker
	ec1_tle = dic_fqc[SatAct]["tle"]
	tracker = sattracker3.Tracker(satellite=ec1_tle, groundstation=tallinn)
	tracker.set_epoch(time.time())
	Dfrequencys = re.split('[\*\-/]',dic_fqc[SatAct]["Downlink"])
	Dfrequencys[:] = [item for item in Dfrequencys if item != '']
	Dfrequency['values'] = Dfrequencys
	if Dfrequencys:Dfrequency.current(0)
	Ufrequencys = re.split('[\*\-/]',dic_fqc[SatAct]["Uplink"])
	Ufrequencys[:] = [item for item in Ufrequencys if item != '']
	Ufrequency['values'] = Ufrequencys
	if Ufrequencys:Ufrequency.current(0)
	Mode_tx = dic_fqc[SatAct]["Mode"]

def selec_satellite(event):
	global SatelliteAct
	event.widget.get()
	SatelliteAct = event.widget.get()
	get_satellite(SatelliteAct)

def SatNearSelected(event):
	global SatelliteAct
	selection =event.widget.curselection()
	if selection:
		index =  selection[0]
		value = event.widget.get(index)
		SatelliteAct = value[:40].strip()
		get_satellite(SatelliteAct)


def save_data():
	global tallinn

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
	tallinn = (lat,lon, "500")
	with open('config.pkl', 'wb') as f:
	    pickle.dump([serial_port_selected,rig_selected,rig_num,tallinn], f)

def start_scn():

	global start_es
	start_es = True

def stop_scn():
	global start_es
	start_es = False

def Control_freq():
	if start_es:
		tracker = sattracker3.Tracker(satellite=ec1_tle, groundstation=tallinn)
		tracker.set_epoch(time.time())
		Sa = "Satellite         :" + SatelliteAct
		SatLabel.configure(text=Sa)
		Az = "Azimut            :"+str(int(tracker.azimuth()))
		Azimut.configure(text=Az)
		El = "Elevation         :"+str(int(tracker.elevation()))
		Elevation.configure(text=El)
		Ra = "Range             :"+str(int((tracker.range()/1000)))+" Km"
		Range.configure(text=Ra)
		if Dfrequency.get():
			Df0  =float(Dfrequency.get())*1000000
			Dfrec = tracker.doppler(100e6)*Df0 /100000000+Df0
			FD="Frequency Download:"+str(int(Dfrec)) + " Hz"
			FreqDownload.configure(text=FD)
		else:Dfrec =0
		if Ufrequency.get():
			Uf0  =float(Ufrequency.get())*1000000
			Ufrec = tracker.doppler(100e6)*Uf0 /100000000+Uf0
			FU="Frequency Upload  :"+str(int(Ufrec)) + " Hz"
			FreqUpload.configure(text=FU)
		else:Ufrec =0
		Mo = "Mode              :" + Mode_tx
		Mode. configure(text=Mo)
		if str(rig_num) == "4":	cmd = "rigctl -m " + str(rig_num) + " F " + str(int(Dfrec)) + " M " + "FM" + " " + "8000"  + " V VFOA"
		else: cmd = "rigctl -m " + str(rig_num) +" -r " + serial_port_selected +" F " + str(int(Dfrec)) + " M " + "FM" + " " + "8000" + " V VFOA"
		print(cmd)
		status,output = subprocess.getstatusoutput(cmd)
	root.after(5000, Control_freq)

def calctracker(sat):
	tle = dic_fqc[sat]["tle"]
	trackers = sattracker3.Tracker(satellite=tle, groundstation=tallinn)
	trackers.set_epoch(time.time())
	return(trackers)

def SearchNear():
	global SatNearList
	for d in range(SatNear.size()):
		sat = SatNear.get(d)[:40].strip()
		if sat:trackers = calctracker(sat)
		ele = trackers.elevation()
		if int(ele) < 1 :
			SatNear.delete(d)
			SatNearList.remove(sat)
			break
	for l in dic_fqc:
		trackers = calctracker(l)
		elev = trackers.elevation()
		rang = trackers.range()
		if (elev >=1):
			if not (l in  SatNearList):
				SatNearList.append(l)
				SatNear.insert('end',str(l).ljust(40)[:40] + "  " + str(int(elev)).ljust(4)[:4] + "   " + str(int(rang/1000)).ljust(10)[:10])
			else:
				for d in range(SatNear.size()):
					sat = SatNear.get(d)[:40].strip()
					if sat ==l:
						SatNear.delete(d)
						SatNear.insert(d,str(l).ljust(40)[:40] + "  " + str(int(elev)).ljust(4)[:4] + "   " + str(int(rang/1000)).ljust(10)[:10])
	root.after(1000, SearchNear)

root = Tk()
root.title("Satellite Doppler Ferequency Tracker")
root.geometry('600x700')

#get configuration file
if pathlib.Path('config.pkl').is_file():
	with open('config.pkl','rb') as f:  # Python 3: open(..., 'rb')
	    serial_port_selected,rig_selected,rig_num,tallinn = pickle.load(f)
else:
	serial_port_selected=""
	rig_selected="FLRig"
	rig_num=4
	tallinn = (-31.319493,-64.273951, "500")
SatNearList = list()
#get serial port
lab_serial = Label(root, text="Serial Port:")
lab_serial.grid(row=0, column=0,sticky=W,columnspan=1)
serial_port = Combobox(root)
status,output = subprocess.getstatusoutput("ls /dev/tty*")
serial_port_list =output.split('\n')
serial_port['values']= serial_port_list
serial_port.current(1) #set the selected item
serial_port.grid(column=1, row=0,sticky=W,  columnspan=2)
serial_port.bind("<<ComboboxSelected>>", select_serial_port)
#serial_port.current(serial_port_list.index(serial_port_selected))

#get rig
lab_rig = Label(root, text="Transceiver:")
lab_rig.grid(row=0, column=3,sticky=W,columnspan=1)
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
rig.grid(column=4, row=0,columnspan=2)
rig.bind("<<ComboboxSelected>>", selectrig)

#get local coordinates
lat_lb = Label(root, text="Latitude:")
lat_lb.grid(row=1, column=0,sticky=W,columnspan=1)
lat_entry= Entry(root)
lat_entry.insert(0, str(tallinn[0]))
lat_entry.grid(row=1, column=1,sticky=W,columnspan=2)
lon_lb = Label(root, text="Longitude:")
lon_lb.grid(row=1, column=3,sticky=W,columnspan=1)
lon_entry= Entry(root)
lon_entry.insert(0, str(tallinn[1]))
lon_entry.grid(row=1, column=4,sticky=W,columnspan=2)

Separator(root).place(x=0, y=47, relwidth=1)

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



#get frequency
lab_frequencyD = Label(root, text="Downlad Frequency:")
lab_frequencyD.grid(column=0, row=3,columnspan=1,)
Dfrequency  = Combobox(root)
Dfrequency.grid(column=1, row=3,columnspan=2)
#Dfrequency['values'] ="437.229"
#Dfrequency.current(0)
lab_frequencyU = Label(root, text="Upload Frequency:")
lab_frequencyU.grid(column=3, row=3,columnspan=1)
Ufrequency  = Combobox(root)
Ufrequency.grid(column=4, row=3,columnspan=2)
#Ufrequency['values'] ="437.229"
#Ufrequency.current(0)

lab_satellite = Label(root, text="Satellite:")
lab_satellite.grid(column=0, row=2,columnspan=1)

satellite = Combobox(root)
satellite['values'] = sat_list
satellite.current(1) #set the selected item
satellite.grid(column=1, row=2,columnspan=2)
satellite.bind("<<ComboboxSelected>>", selec_satellite)
#save configuration


save = Button(root, text="Save", command=save_data)
save.grid(column=6, row=0)
start_es = False

#start tracking


start = Button(root, text="Start", command=start_scn)
start.grid(column=6, row=2)

#stop tracking

stop = Button(root, text="Stop", command=stop_scn)
stop.grid(column=6, row=3)

#get parameter and control frequency receiver
SatLabel = Label(root, text="Satellite         :",font=("Arial Bold", 16))
SatLabel.grid(row=6, columnspan=7,sticky=W)
Azimut = Label(root, text="Azimut            :",font=("Arial Bold", 16))
Azimut.grid(row=7, columnspan=7,sticky=W)
Elevation = Label(root, text="Elevation         :",font=("Arial Bold", 16))
Elevation.grid(row=8, columnspan=7,sticky=W)
Range = Label(root, text="Range             :",font=("Arial Bold", 16))
Range.grid(row=9, columnspan=7,sticky=W)
FreqDownload = Label(root, text="Frequency Download:",font=("Arial Bold", 16))
FreqDownload.grid(row=10, columnspan=7,sticky=W)
FreqUpload = Label(root, text="Frequency Upload  :",font=("Arial Bold", 16))
FreqUpload.grid(row=11, columnspan=7,sticky=W)
Mode = Label(root, text="Mode              :",font=("Arial Bold", 16))
Mode.grid(row=12, columnspan=7,sticky=W)

SatNear = Listbox(root, height=15, width=60,font=("TkFixedFont", 16))
SatNear.bind('<<ListboxSelect>>', SatNearSelected)
SatNear.grid(row=13, columnspan=7,sticky=W)

quit = Button(root, text="Quit", command = root.destroy)
quit.grid(column=6, row=14)

root.after(2000, SearchNear)
root.after(5000, Control_freq)
root.mainloop()

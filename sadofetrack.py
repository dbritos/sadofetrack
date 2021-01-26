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

def calctracker(sat):
	tle = dic_fqc[sat]["tle"]

	tkl = sattracker3.Tracker(satellite=tle, groundstation=tallinn)
	tkl.set_epoch(time.time())
	return(tkl)


def get_satellite(SatAct):
	global tracker
	global Dfrequency
	global Ufrequency
	global Bfrequency
	tracker = calctracker(SatAct)
	tracker.set_epoch(time.time())
	Dfrequency = dic_fqc[SatAct]["Downlink"].strip()
	Ufrequency = dic_fqc[SatAct]["Uplink"].strip()
	Bfrequency = dic_fqc[SatAct]["Beacon"].strip()

def SatNearSelected(event):
	global SatelliteAct
	selection =event.widget.curselection()
	if selection:
		index =  selection[0]
		value = event.widget.get(index)
		SatelliteAct = value[:17].strip()
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
	ModeD_rx ='FM'
	ModeB_rx ='FM'
	ModeU_tx ='FM'
	ValidModes = ['USB', 'LSB', 'CW', 'CWR', 'RTTY', 'RTTYR', 'AM', 'FM', 'WFM', 'AMS', 'PKTLSB', 'PKTUSB', 'PKTFM', 'ECSSUSB', 'ECSSLSB', 'FAX', 'SAM', 'SAL', 'SAH', 'DSB']
	if SatelliteAct !="":
		tracker = calctracker(SatelliteAct)
		Sa = "Satellite         :" + SatelliteAct
		SatLabel.configure(text=Sa)
		Az = "Azimut            :"+str(int(tracker.azimuth()))
		Azimut.configure(text=Az)
		El = "Elevation         :"+str(int(tracker.elevation()))
		Elevation.configure(text=El)
		Ra = "Range             :"+str(int((tracker.range()/1000)))+" Km"
		Range.configure(text=Ra)

		try:Df0  =float(Dfrequency)*1000
		except: Df0 = 0
		frec = tracker.doppler(100e6)*Df0 /100000000+Df0
		FD="Frequency Download:"+str(int(frec)) + " Hz"
		FreqDownload.configure(text=FD)
		if frec != 0:Dfrec = " F " + str(int(frec))
		else:Dfrec = ""

		try: Uf0  =float(Ufrequency)*1000
		except:Uf0  = 0
		frec = tracker.doppler(100e6)*Uf0 /100000000+Uf0
		FU="Frequency Upload  :"+str(int(frec)) + " Hz"
		FreqUpload.configure(text=FU)
		if frec !=0:Ufrec = " I " + str(int(frec))
		else:Ufrec = ""

		try: Bf0  =float(Bfrequency)*1000
		except:Bf0  = 0
		frec = tracker.doppler(100e6)*Bf0 /100000000+Bf0
		BF="Beacon            :"+str(int(frec)) + " Hz"
		BeaconL.configure(text=BF)
		if frec!=0:Bfrec = " F " + str(int(frec))
		else:Bfrec = ""

		Mo = dic_fqc[SatelliteAct]["ModeD"].strip()
		if Mo in ValidModes:
			ModeD_rx = Mo
			MoD = "Mode:" + ModeD_rx
			ModeDcmd = " M " + ModeD_rx + " 0 "
			ModeD.configure(text=MoD)
		else:
			MoD = "Mode:" + ''
			ModeD.configure(text=MoD)
			ModeDcmd = " "
		Mo = dic_fqc[SatelliteAct]["ModeU"].strip()
		if Mo in ValidModes:
			ModeU_tx = Mo
			MoU = "Mode:" + ModeU_tx
			ModeUcmd = " X " + ModeU_tx + " 0 "
			ModeU.configure(text=MoU)
		else:
			MoU = "Mode:" + ''
			ModeU.configure(text=MoU)
			ModeUcmd = " "
		Mo = dic_fqc[SatelliteAct]["ModeB"].strip()
		if Mo in ValidModes:
			ModeB_rx=Mo
			MoB = "Mode:" + ModeB_rx
			ModeBcmd = " M " + ModeB_rx + " 0 "
			ModeB.configure(text=MoB)
		else:
			MoB = "Mode:" + ''
			ModeB.configure(text=MoB)
			ModeBcmd = " "
		rxcmd = ""
		txcmd = ""
		if start_es:
			if checkDF.get():
				if checkDF.get()==0:
					rxcmd=""
				if checkDF.get()==1:
					rxcmd= " S 1 VFOB" + ModeDcmd + Dfrec
				if checkDF.get()==2:
					rxcmd= " S 1 VFOB" + ModeBcmd + Bfrec
				if str(rig_num) == "4":	cmd = "rigctl -m " + str(rig_num) + rxcmd
				else: cmd = "rigctl -m " + str(rig_num) +" -r " + serial_port_selected + rxcmd
				status,output = subprocess.getstatusoutput(cmd)
				print(cmd,"\n",status,output)
			if checkUF.get():
				txcmd =" S 1 VFOB" + ModeUcmd + Ufrec
				if str(rig_num) == "4":	cmd = "rigctl -m " + str(rig_num) + txcmd
				else: cmd = "rigctl -m " + str(rig_num) +" -r " + serial_port_selected + txcmd
			status,output = subprocess.getstatusoutput(cmd)
			print(cmd,"\n",status,output)
	root.after(5000, Control_freq)

def InsertSat():
	for l in dic_fqc:
		tkl = calctracker(l)
		elev = tkl.elevation()
		rang = tkl.range()
		Title = dic_fqc[l]["Title"].strip()
		sns=str(l).ljust(17)[:17] + " " + str(int(elev)).ljust(4)[:4] + " " + str(int(rang/1000)).ljust(10)[:10]+ "   " + Title.ljust(20)[:20]
		if (elev >=1):
			SatNear.insert(0,sns)
			SatNear.itemconfig(0, {'bg':'yellow'})
		else:
			SatNear.insert('end',sns)

def SearchNear():
	global SatNearList
	SS = SatNear.curselection()

	for d in range(SatNear.size()):

		l = SatNear.get(d)[:17].strip()
		Title = dic_fqc[l]["Title"].strip()
		tkl = calctracker(l)
		elev = tkl.elevation()
		rang = tkl.range()
		SatNear.delete(d)
		sns=str(l).ljust(17)[:17] + " " + str(int(elev)).ljust(4)[:4] + " " + str(int(rang/1000)).ljust(10)[:10]+ "   " + Title.ljust(20)[:20]
		if (elev >=1):
			if l in SatNearList:
				SatNear.insert(d,sns)
				SatNear.itemconfig(d, {'bg':'yellow'})
				if SS:
					if SS[0]==d:
						SatNear.selection_set(d)
			else:
				SatNear.insert(0,sns)
				SatNear.itemconfig(0, {'bg':'yellow'})
				SatNearList.append(l)
				if SS:
					if SS[0]==d:
						SatNear.selection_set(0)

		else:
			if l in SatNearList:
				SatNear.insert('end',sns)
				SatNear.itemconfig('end', {'bg':'white'})
				SatNearList.remove(l)
				if SS:
					if SS[0]==d:
						SatNear.selection_set(SatNear.size()-1)

			else:
				SatNear.insert(d,sns)
				SatNear.itemconfig(d, {'bg':'white'})
				if SS:
					if SS[0]==d:
						SatNear.selection_set(d)
	root.after(1000, SearchNear)




root = Tk()
root.title("Satellite Doppler Ferequency Tracker")
root.geometry('600x750')

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

#sat_list = list()
list_tle = list()
dic_tle = {}
list_fqc = list()
dic_fqc = {}
file = urllib.request.urlopen("http://www.celestrak.com/NORAD/elements/active.txt")
for line in file:
	list_tle.append(line.decode('utf-8').rstrip('\n\r'))

#file = urllib.request.urlopen("https://www.amsat.org/tle/current/nasabare.txt")
#for line in file:
#	list_tle.append(line.decode('utf-8').rstrip('\n\r'))

for itn in range(0,len(list_tle),3):
	nserie=list_tle[itn+1].split()[1]
	item_tle = {"name": list_tle[itn].rstrip(),"tle1":list_tle[itn+1], "tle2":list_tle[itn+2]}
	dic_tle[nserie.rstrip()] = item_tle
if pathlib.Path('frequency.pkl').is_file():
	with open('frequency.pkl','rb') as f:  # Python 3: open(..., 'rb')
	    fqc = pickle.load(f)

#else:
#	file = urllib.request.urlopen("http://www.ne.jp/asahi/hamradio/je9pel/satslist.csv")

list_fqc=fqc[0]
nr = 0
for itn in range(0,len(list_fqc)):
	if  str(list_fqc[itn][0])+"U" in dic_tle.keys():
		item_fqc = {"satellite": list_fqc[itn][1],
		"Number":list_fqc[itn][0],
		"Uplink":list_fqc[itn][2],
		"Downlink":list_fqc[itn][3],
		"Beacon":list_fqc[itn][4],
		"ModeD":list_fqc[itn][6],
		"ModeU":list_fqc[itn][5],
		"ModeB":list_fqc[itn][7],
		"Title":list_fqc[itn][11],
#		"Callsign":list_fqc[itn][11],
		"tle": dic_tle[str(list_fqc[itn][0])+"U"]}
		if list_fqc[itn][1] in dic_fqc.keys():
			nr=nr+1
			dic_fqc[str(list_fqc[itn][1])+str(nr)] = item_fqc
		else:
			dic_fqc[str(list_fqc[itn][1])] = item_fqc
			nr=0

#for l in dic_fqc.keys(): sat_list.append(l)
checkDF= IntVar()
checkUF= IntVar()

checDF = Radiobutton(root, text="Not Track Downlad Freq.",variable=checkDF, value=0)
checDF.grid(column=0, row=2,columnspan=2,sticky=W)
checDF = Radiobutton(root, text="TTrack Downlad Freq.",variable=checkDF, value=1)
checDF.grid(column=0, row=3,columnspan=2,sticky=W)
checDF = Radiobutton(root, text="Track Beacon Freq.",variable=checkDF, value=2)
checDF.grid(column=0, row=4,columnspan=2,sticky=W)
checUF = Checkbutton(root, text="Track Upload Freq.",variable=checkUF, onvalue=1, offvalue=0)
checUF.grid(column=3, row=2,columnspan=2,sticky=W)

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
Separator(root, orient='horizontal').grid(row=7,columnspan=9,sticky="ew")
#get parameter and control frequency receiver
SatLabel = Label(root, text="Satellite         :",font=("Arial Bold", 16))
SatLabel.grid(row=8, columnspan=7,sticky=W)
Azimut = Label(root, text="Azimut            :",font=("Arial Bold", 16))
Azimut.grid(row=9, columnspan=7,sticky=W)
Elevation = Label(root, text="Elevation         :",font=("Arial Bold", 16))
Elevation.grid(row=10, columnspan=7,sticky=W)
Range = Label(root, text="Range             :",font=("Arial Bold", 16))
Range.grid(row=11, columnspan=7,sticky=W)
FreqDownload = Label(root, text="Frequency Download:",font=("Arial Bold", 16))
FreqDownload.grid(row=12, columnspan=5,sticky=W)
FreqUpload = Label(root, text="Frequency Upload  :",font=("Arial Bold", 16))
FreqUpload.grid(row=13, columnspan=5,sticky=W)
BeaconL = Label(root, text="Beacon            :",font=("Arial Bold", 16))
BeaconL.grid(row=14, columnspan=5,sticky=W)
ModeD = Label(root, text="Mode:",font=("Arial Bold", 16))
ModeD.grid(row=12, column=4, columnspan=4,sticky=W)
ModeU = Label(root, text="Mode:",font=("Arial Bold", 16))
ModeU.grid(row=13,column=4, columnspan=4,sticky=W)
ModeB = Label(root, text="Mode:",font=("Arial Bold", 16))
ModeB.grid(row=14,column=4, columnspan=4,sticky=W)
Separator(root, orient='horizontal').grid(row=15,columnspan=9,sticky="ew")

Label(root, text='Satellite Name    Elev Azimut      Satellite Explanation', font=("TkFixedFont", 16)).grid(row=16,column=0, columnspan=9,sticky=W)
SatNear = Listbox(root, height=20, width=60,font=("TkFixedFont", 16))
SatNear.bind('<<ListboxSelect>>', SatNearSelected)
SatNear.grid(row=17, columnspan=7,sticky=W)

SatelliteAct = ""
InsertSat()
quit = Button(root, text="Quit", command = root.destroy)
quit.grid(column=6, row=18)

root.after(2000, SearchNear)
root.after(2000, Control_freq)
root.mainloop()

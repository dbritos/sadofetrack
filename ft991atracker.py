#!/usr/bin/env python3
import sys
import glob
import pathlib
import time
import serial
from tkinter import *
from tkinter.ttk import *
import urllib.request
import re
import pickle
import ephem
from math import *

from sympy import failing_assumptions
#constantes 
SATELLITE =0
NUMBER =1 
UPLINK =2
DOWNLINK =3
BEACON =4
MODED =5
MODEU =6
MODEB =7
ICON=8
CTCSS =9
TITLE = 10
TLE=11
ELEVACION=12
RANGE=13
SELECTED =14
NAMBER =17
NEXPT =15
NEXPE =16
ephemsat = -1
global fain
global mdin
def calctracker(sat):
	global site
	global satelite
	global tallinn
	global ephemsat
	if ephemsat != sat:
		tle = list_fqc[sat][TLE]
		satelite = ephem.readtle(tle['name'],tle['tle1'],tle['tle2'])
		site = ephem.Observer()
		site.lat,site.lon,site.elevation = tallinn
		site.name        = 'test facility'
		satelite.compute(site)
		ephemsat = sat
#	return(satelite)

def SatSelected(event):
	global SatelliteAct
	selection =event.widget.curselection()
	for i in range(len(list_fqc)):list_fqc[i][SELECTED] = False
	if selection:
		index =  selection[0]
		value = event.widget.get(index)
		event.widget.activate (index)
		list_fqc[index][SELECTED] = True
		SatelliteAct = index

def save_data():
	global tallinn
	global portx
	global porty
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
	tallinn = (lat,lon, 500)
	portx = selected.get()
	porty = selectedAE.get()
	with open('ft911a.pkl', 'wb') as f:
	    pickle.dump([portx,porty,tallinn], f)

def setport(portx):
	global ser
	global start_es
	global fain
	global mdin
	portx = selected.get()
	if portx =='':
		rig.configure(text="Select  Rig   ",foreground="black")
	else:
		bps=38400
		timex=5
		try: ser=serial.Serial(portx,bps,timeout=timex)
		except:
			rig.configure(text="Rig not exist   ",foreground="red"	)
			start_es = False
			start['state'] = DISABLED
			stop['state'] = DISABLED
		else:
			result=ser.write("FA;" .encode("ascii"))
			fain = ser.read(12)
			if len(fain)==12:			
				start['state'] = NORMAL
				rig.configure(text="Rig ok   ",foreground="green")
				result=ser.write("MD0;" .encode("ascii"))
				mdin = ser.read(5)
			else:
				if ser:ser.close()
				rig.configure(text="Rig not exist   ",foreground="red")	
				start_es = False
				start['state'] = DISABLED	
				stop['state'] = DISABLED	

def start_scn():
	global start_es
	global Mode
	start_es = True
	Mode = True
	stop['state'] = NORMAL
	start['state'] = DISABLED

def stop_scn():
	global fain
	global mdin
	global start_es	
	global ser
	result=ser.write(str(fain.decode()).encode("ascii"))
	result=ser.write(str(mdin.decode()).encode("ascii"))
	result = ser.write("FT2;".encode("ascii"))

	start_es = False
	start['state'] = NORMAL
	stop['state'] = DISABLED

def get_freq_mode():
	global site
	global satelite	
	ValidModes = {'USB':'2', 'LSB':'1', 'CW':'3', 'CWR':'3', 'RTTY':'C', 'RTTYR':'C', 'AM':'5', 'FM':'4', 'NFM':'4', 'AMS':'5', 'PKTLSB':'8', 'PKTUSB':'C', 'PKTFM':'A', 'ECSSUSB':'2', 'ECSSLSB':'1', 'FAX':'A', 'SAM':'5', 'SAL':'5', 'SAH':'5', 'DSB': '1','DMR':'E','':'4'}
	Tone = {'67':'000','74.4':'003','77.0':'004','82.5':'006','88.5':'008','94.8':'010','103.5':'013','107.2':'014','110.9':'015','118.8':'017','123.0':'018','131.8':'020','136.5':'021','210.7':'042'}

	if SatelliteAct != -1:
		calctracker(SatelliteAct)
		Dfrequency = list_fqc[SatelliteAct][DOWNLINK].strip()
		Ufrequency = list_fqc[SatelliteAct][UPLINK].strip()
		Bfrequency = list_fqc[SatelliteAct][BEACON].strip()		
		Sa = "Satellite         :" + list_fqc[SatelliteAct][SATELLITE]
		SatLabel.configure(text=Sa)
		Azim ="{:03.0f}".format(degrees(satelite.az))
		Az = "Azimut            :" + Azim + " °"
		Azimut.configure(text=Az)
		Eleva = "{:03.0f}".format(degrees(satelite.alt))
		El = "Elevation         :" + Eleva + " °"
		Elevation.configure(text=El)
		Ra = "Range             :"+str(int((satelite.range/1000)))+" Km"
		Range.configure(text=Ra)

		try:Df0  = float(Dfrequency)*1000
		except: Df0 = 0
		frec =Df0 -(satelite.range_velocity / 299792458. * 100e6)*Df0 /100000000
		FD="Frequency Download:"+str(int(frec)) + " Hz"
		FreqDownload.configure(text=FD)
		if frec != 0:Dfrec = "FA" + str(int(frec)).zfill(9) + ";"
		else:Dfrec = ""

		try: Uf0  = float(Ufrequency)*1000
		except:Uf0  = 0
		frec =Uf0 +(satelite.range_velocity / 299792458. * 100e6)*Uf0 /100000000
		FU="Frequency Upload  :" + str(int(frec)) + " Hz"
		FreqUpload.configure(text=FU)
		if frec !=0:Ufrec = "FB" + str(int(frec)).zfill(9) + ";"
		else:Ufrec = ""

		try: Bf0  =float(Bfrequency)*1000
		except:Bf0  = 0
		frec =Bf0 - (satelite.range_velocity / 299792458. * 100e6)*Bf0 /100000000
		BF="Beacon            :"+str(int(frec)) + " Hz"
		BeaconL.configure(text=BF)
		if frec!=0:Bfrec ="FA" + str(int(frec)).zfill(9) +";"
		else:Bfrec = ""

		R_freq = [Dfrec,Ufrec,Bfrec]
		ToneCTCSS = list_fqc[SatelliteAct][CTCSS].strip()
		ModeD_rx = list_fqc[SatelliteAct][MODED].strip()
		if ModeD_rx in ValidModes:
			ModeDcmd = "MD0" + ValidModes[ModeD_rx] + ";"
		else:
			ModeDcmd = ""
		ModeD.configure(text="Mode:" + ModeD_rx)

		ModeU_tx = list_fqc[SatelliteAct][MODEU].strip()
		if ModeU_tx in ValidModes:
			ModeUcmd = "MD0" + ValidModes[ModeU_tx] + ";"
		else:
			ModeUcmd = ""
		ModeU.configure(text="Mode:" + ModeU_tx)

		ModeB_rx = list_fqc[SatelliteAct][MODEB].strip()
		if ModeB_rx in ValidModes:
			ModeBcmd = "MD0" + ValidModes[ModeB_rx] + ";"
		else:
			ModeBcmd = ""
		ModeB.configure(text="Mode:" + ModeB_rx)
		if ToneCTCSS in Tone:
			CTCSST = "CN00"+Tone[ToneCTCSS]+";"
			ModeUcmd = "MD04;"
		else:
			CTCSST = ""
		R_mode = [ModeDcmd,ModeUcmd,ModeBcmd]
		rfm=[R_freq,R_mode,CTCSST]
		return(rfm)

def Control_freq():
	global Mode
	if SatelliteAct != -1:
		Rfreq,Rmode,CTCSST = get_freq_mode()
		ModeDcmd,ModeUcmd,ModeBcmd = Rmode
		Dfrec,Ufrec,Bfrec = Rfreq
		if start_es:
			if checkUF.get():
				if Mode:
#					result=ser.write("QS;" .encode("ascii"))
					result=ser.write("CT02;" .encode("ascii"))
					if ModeUcmd:result=ser.write(ModeUcmd .encode("ascii"))
					result=ser.write("AB;".encode("ascii"))
					if CTCSST: result=ser.write(CTCSST .encode("ascii"))
					if checkDF.get()==1:
						if ModeDcmd:result=ser.write(ModeDcmd .encode("ascii"))
					if checkDF.get()==2:
						if ModeBcmd:result=ser.write(ModeBcmd .encode("ascii"))
					Mode = False
				
				result=ser.write(Ufrec.encode("ascii"))
				result = ser.write("FT3;".encode("ascii"))
			if checkDF.get()==1:
				result=ser.write(Dfrec.encode("ascii"))
			if checkDF.get()==2:
				result=ser.write(Bfrec.encode("ascii"))
				
	root.after(2000, Control_freq)

def nextpass():
	global SatelliteAct
	global list_fqc
	global site
	global satelite	


	for d in range(len(list_fqc)):	
		calctracker(d)
		list_fqc[d][NEXPT] = 'never'
		list_fqc[d][NEXPE] = 'neve'	
		if str(satelite.circumpolar).find('False') ==0 and str(satelite.neverup).find('False') ==0  :
			npt = site.next_pass(satelite)
			if npt[0] != None and  npt[3] != None :
				list_fqc[d][NEXPT] = ephem.localtime(npt[0])
				list_fqc[d][NEXPE] = int(degrees(npt[3]))
	root.after(40000, nextpass)

def InsertInListBox():

	global SatelliteAct
	global list_fqc
	global site
	global satelite
	list_fqc =sorted(list_fqc,key=lambda l:l[ELEVACION], reverse=True)
	for d in range(len(list_fqc)):
		Title = list_fqc[d][TITLE].strip()
		calctracker(d)
		elev = degrees(satelite.alt)
		list_fqc[d][ELEVACION] = elev
		rang = satelite.range
		list_fqc[d][RANGE]=rang

		if SatNear.size() == len(list_fqc):SatNear.delete(d)
		sns=str(list_fqc[d][SATELLITE]).ljust(15)[:15] + " " + str(list_fqc[d][NEXPT]).ljust(17)[:17] +\
		" " + str(list_fqc[d][NEXPE]).ljust(4)[:4] + " " + str(int(elev)).ljust(4)[:4] + " " +\
		 str(int(rang/1000)).ljust(5)[:5]+ "  " + Title.ljust(30)[:30]
		SatNear.insert(d,sns)
		if list_fqc[d][SELECTED]:
			SatNear.itemconfig(d, {'bg':'lightgreen'})
			SatelliteAct  = d
		else:	
			if (elev >=1):
				SatNear.itemconfig(d, {'bg':'yellow'})
			elif  Title == "FM Voice Repeater":
				SatNear.itemconfig(d, {'bg':'lightblue'})
			else:
				SatNear.itemconfig(d, {'bg':'white'})
	
	root.after(5000, InsertInListBox)


root = Tk()
root.title("Satellite Doppler Ferequency Tracker")
root.geometry('660x700')

global portx
global porty
global site 
global satelite
global tallinn
geolist = ["35942","37809","33278",'36581',"40931","43700"]
#get configuration file
if pathlib.Path('ft911a.pkl').is_file():
	with open('ft911a.pkl','rb') as f:  # Python 3: open(..., 'rb')
	    portx,porty,tallinn = pickle.load(f)
else:
	porty=''
	portx=''
	tallinn = (-31.319336,-64.273886, 500)
site = ephem.Observer()
site.lat,site.lon,site.elevation = tallinn
#get serial port
lab_serial = Label(root, text="Serial Port Rig:")
lab_serial.grid(row=0, column=0,sticky=W,columnspan=1)

if sys.platform.startswith('win'):
	ports = ['COM%s' % (i + 1) for i in range(256)]
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
	# this excludes your current terminal "/dev/tty"
	ports = glob.glob('/dev/tty[T-U]*')
elif sys.platform.startswith('darwin'):
	ports = glob.glob('/dev/cu.*')
if not ports :ports = ['/dev/ttyUSB0']
options = ports
if options:
	selected = StringVar(root)
	if portx in options:
		selected.set(portx)
	else:
		selected.set(options[0])
	serial_port = OptionMenu(root,selected,*options, command=setport)
	serial_port.grid(column=1, row=0,sticky=W,  columnspan=3)
	serial_port.configure(style="W.TMenubutton")

# Select serial for AE tracker
lab_serialAE = Label(root, text="Serial Port AE:")
lab_serialAE.grid(row=1, column=0,sticky=W,columnspan=1)
selectedAE = StringVar(root)
selectedAE.set(options[0])
serial_portAE = OptionMenu(root,selectedAE,*options)
serial_portAE.grid(column=1, row=1,sticky=W,  columnspan=3)

#get local coordinates
lat_lb = Label(root, text="Latitude:")
lat_lb.grid(row=2, column=0,sticky=W,columnspan=1)
lat_entry= Entry(root)
lat_entry.insert(0, str(tallinn[0]))
lat_entry.grid(row=2, column=1,sticky=W,columnspan=2)
lon_lb = Label(root, text="Longitude:")
lon_lb.grid(row=2, column=3,sticky=W,columnspan=1)
lon_entry= Entry(root)
lon_entry.insert(0, str(tallinn[1]))
lon_entry.grid(row=2, column=4,sticky=W,columnspan=2)
Separator(root, orient='horizontal').grid(row=3,columnspan=9,sticky="ew")


#get satellite

#sat_list = list()
list_tle = list()
dic_tle = {}
list_fqc = list()

file = urllib.request.urlopen("http://www.celestrak.com/NORAD/elements/active.txt")
for line in file:
	list_tle.append(line.decode('utf-8').rstrip('\n\r'))

for itn in range(0,len(list_tle),3):
	nserie=list_tle[itn+1].split()[1]
	item_tle = {"name": list_tle[itn].rstrip(),"tle1":list_tle[itn+1], "tle2":list_tle[itn+2]}
	dic_tle[nserie.rstrip()] = item_tle

f = open("frec.py", "w")
file = urllib.request.urlopen("http://amsat.org.ar/freq.js")
for line in file:
	line = line.decode('utf-8').rstrip('\n\r')
	line = re.sub(r'//', '#', str(line))
	f.writelines(line + '\n')
f.close()
import frec
elev = 90
ran = 0
nextpasst ='never'
nextpasse ='neve'

sel = False
for itn in range(0,len(frec.freq )):
	if  dic_tle.get(str(frec.freq[itn][0].strip())+"U")!=None and str(frec.freq[itn][0].strip()) not in geolist:
		item_fqc = [frec.freq[itn][1].strip(), 	#S
		frec.freq[itn][0].strip(),				#N
		frec.freq[itn][2].strip(),				#UP
		frec.freq[itn][3].strip(),				#DO
		frec.freq[itn][4].strip(),				#B
		frec.freq[itn][6].strip(),				#MD
		frec.freq[itn][5].strip(),				#MU
		frec.freq[itn][7].strip(),				#MB
		frec.freq[itn][9].strip(),				#Icon
		frec.freq[itn][10].strip(),				#CTCCS
		frec.freq[itn][11].strip(),				#T
		dic_tle[str(frec.freq[itn][0].strip())+"U"],	#TLE
		elev,
		ran,
		sel,
		nextpasst,
		nextpasse]
		list_fqc.append(item_fqc)


checkDF= IntVar()
checkUF= IntVar()

checDF = Radiobutton(root, text="Not Track Downlad Freq.",variable=checkDF, value=0)
checDF.grid(column=0, row=4,columnspan=2,sticky=W)
checDF = Radiobutton(root, text="TTrack Downlad Freq.",variable=checkDF, value=1)
checDF.grid(column=0, row=5,columnspan=2,sticky=W)
checDF = Radiobutton(root, text="Track Beacon Freq.",variable=checkDF, value=2)
checDF.grid(column=0, row=6,columnspan=2,sticky=W)
checUF = Checkbutton(root, text="Track Upload Freq.",variable=checkUF, onvalue=1, offvalue=0)
checUF.grid(column=3, row=4,columnspan=2,sticky=W)
rig = Label(root, text="Select  Rig   ",font="TkFixedFont")
rig.grid(column=4,row=0,columnspan=2,sticky=W)
#save configuration
save = Button(root, text="Save", command=save_data)
save.grid(column=6, row=0)
start_es = False

#start tracking
start = Button(root, text="Start",state=DISABLED, command=start_scn)
start.grid(column=6, row=4)

#stop tracking
stop = Button(root, text="Stop",state=DISABLED, command=stop_scn)
stop.grid(column=6, row=5)
Separator(root, orient='horizontal').grid(row=9,columnspan=9,sticky="ew")
#get parameter and control frequency receiver
SatLabel = Label(root, text="Satellite         :",font="TkFixedFont")
SatLabel.grid(row=10, columnspan=7,sticky=W)
Azimut = Label(root, text="Azimut            :",font="TkFixedFont")
Azimut.grid(row=11, columnspan=7,sticky=W)
Elevation = Label(root, text="Elevation         :",font="TkFixedFont")
Elevation.grid(row=12, columnspan=7,sticky=W)
Range = Label(root, text="Range             :",font="TkFixedFont")
Range.grid(row=13, columnspan=7,sticky=W)
FreqDownload = Label(root, text="Frequency Download:",font="TkFixedFont")
FreqDownload.grid(row=14, columnspan=5,sticky=W)
FreqUpload = Label(root, text="Frequency Upload  :",font="TkFixedFont")
FreqUpload.grid(row=15, columnspan=5,sticky=W)
BeaconL = Label(root, text="Beacon            :",font="TkFixedFont")
BeaconL.grid(row=16, columnspan=5,sticky=W)
ModeD = Label(root, text="Mode:",font="TkFixedFont")
ModeD.grid(row=14, column=4, columnspan=4,sticky=W)
ModeU = Label(root, text="Mode:",font="TkFixedFont")
ModeU.grid(row=15,column=4, columnspan=4,sticky=W)
ModeB = Label(root, text="Mode:",font="TkFixedFont")
ModeB.grid(row=16,column=4, columnspan=4,sticky=W)
Separator(root, orient='horizontal').grid(row=17,columnspan=9,sticky="ew")

Label(root, text='Satellite Name  Next Pass         MaxE Elev Range  Satellite Description', font="TkFixedFont").grid(row=18,column=0, columnspan=9,sticky=W)
SatNear = Listbox(root, height=20, width=81,font="TkFixedFont",selectbackground='lightgreen',selectmode="single")
SatNear.bind('<<ListboxSelect>>', SatSelected)
SatNear.grid(row=19, columnspan=8,sticky=W)

SatelliteAct = -1
InsertInListBox()
quit = Button(root, text="Quit", command =root.destroy)
quit.grid(column=6, row=20)

root.after(2000, InsertInListBox)
root.after(2000, Control_freq)
root.after(1000, nextpass)
root.mainloop()

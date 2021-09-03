# sadofetrack
This project makes it possible to tune the emission frequency of the satellites and follow the frequency shift produced by the Doppler effect.

# ft991atracker

I\This is the version for Yaesu FT991a this program  not use hamlib the only lib to install is  ephem you can install this with:

``sudo apt-get install -y python3-ephem``

# Program requirements

Have Rigctl installed
http://manpages.ubuntu.com/manpages/focal/man1/rigctl.1.html
Have python 3 with the followin library
import subprocess
import pathlib
import time
from tkinter import *
from tkinter.ttk import *
import urllib.request
import sattracker3
import re
import pickle
The sattracker3 must be in the same directory and need the ephem library.

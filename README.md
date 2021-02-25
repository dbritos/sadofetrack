# sadofetrack
This project makes it possible to tune the emission frequency of the satellites and follow the frequency shift produced by the Doppler effect.

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

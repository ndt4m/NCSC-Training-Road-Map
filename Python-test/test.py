import os, sys, subprocess, re

def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
id = 3336
path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"exploit-db")
open_file(os.path.join(path, f"{id}.txt"))
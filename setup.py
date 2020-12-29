from distutils.core import setup
import py2exe
import sys


sys.argv.append("py2exe")

option = {"compressed":True, "optimize":2, "bundle_files":3, "excludes": ["tkinter", "PIL"]}

setup(
    options={"py2exe": option},
    windows=[{"script": "flappybird.py", "icon_resources": [(0, "flappy.ico")]}],
    zipfile="lib/libs.zip"
)

#!/bin/bash

sudo apt install libatlas-base-dev python3-pil python3-pil.imagetk -y
pip3 install pandas exifread GPSPhoto piexif pyyaml Pillow pygpsclient
pip3 install --upgrade numpy
pip3 install --upgrade pygpsclient
cp aerial-survey.yaml ~/
cp auto_capture.py ~/
cp GPS_Post_Processing.py ~/

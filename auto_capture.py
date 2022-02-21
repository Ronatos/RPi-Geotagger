import logging
import math
import os
import serial
import shutil
import subprocess
import threading
import time
import yaml

from datetime import datetime
from picamera import PiCamera

def checksum(line):
    checkString = line.partition("*")
    checksum = 0
    for c in checkString[0]:
        checksum ^= ord(c)

    try:  # Just to make sure
        inputChecksum = int(checkString[2].rstrip(), 16);
    except:
        print("Error in string")
        return False

    if checksum == inputChecksum:
        return True
    else:
        print("=====================================================================================")
        print("===================================Checksum error!===================================")
        print("=====================================================================================")
        print(hex(checksum), "!=", hex(inputChecksum))
        return False

def getLatLng(latString, lngString):
    lat = latString[:2].lstrip('0') + "." + "%.7s" % str(float(latString[2:]) * 1.0 / 60.0).lstrip("0.")
    lng = lngString[:3].lstrip('0') + "." + "%.7s" % str(float(lngString[3:]) * 1.0 / 60.0).lstrip("0.")
    return lat, lng

def getTime(string, format, returnFormat):
    return time.strftime(returnFormat, time.strptime(string, format))  # Convert date and time to a nice printable format

def get_working_drive(drivepaths):
    for drivepath in drivepaths:
        if shutil.disk_usage(drivepath).free <= 500000000:
            print("USB " + drivepath + " has insufficient space. USB Drives will not be used with less than 500MB of storage remaining.")
            logging.warning("USB " + drivepath + " has insufficient space. USB Drives will not be used with less than 500MB of storage remaining.")
            continue
        return drivepath
    print("No USB Drives were detected with sufficient space.")
    logging.error("No USB Drives were detected with sufficient space.")
    exit()

def GPSCapture(capture_folder_path, csv_file, start_time, runtime):
    print("New GPS thread created...")
    logging.info('New GPS thread created...')
    while (datetime.now() - start_time).total_seconds() < runtime:
        line = readString()
        lines = line.split(",")
        if checksum(line):
            if lines[0] == "GPRMC":
                csv_file.write(printRMC(lines) + "\n")
                csv_file.flush()
                os.system('sync')

def newPhotoCapture(capture_folder_path):
    print("New camera thread created...")
    logging.info('New camera thread created...')
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    camera.capture(capture_folder_path + timestamp +".jpg")
    os.system('sync')
    logging.info('Thread finished.')
    print("Thread finished.")

def printRMC(lines):
    date = getTime(lines[1] + lines[9], "%H%M%S.%f%d%m%y", "%Y-%m-%d_%H-%M-%S")
    status = lines[2]
    
    if lines[3] == "" or lines[5] == "":
        lat = "No Data"
        lat_ref = "No Data"
        lng = "No Data"
        lng_ref = "No Data"
        speed = "No Data"
        mode = "No Data"
    else:
        latlng = getLatLng(lines[3], lines[5])
        lat = latlng[0]
        lat_ref = lines[4]
        lng = latlng[1]
        lng_ref = lines[6]
        speed = lines[7]

        if len(lines) == 13:  # The returned string will be either 12 or 13 - it will return 13 if NMEA standard used is above 2.3
            mode = lines[12].partition("*")[0]
        else:
            #print(lines[11].partition("*")[0])
            mode = lines[11].partition("*")[0]
        
    csv_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if str(lng_ref) == "W":
        lng = "-" + str(lng)
        
    if str(lat_ref) == "S":
        lat = "-" + str(lat)
 
    csv_line = str(date)+","+str(status)+","+str(lat)+","+str(lat_ref)+","+str(lng)+","+str(lng_ref)+","+str(speed)+","+str(mode)+","+str(csv_date)
    
    print(csv_line)
    
    return csv_line

def readString():
    while 1:
        while ser.read().decode("utf-8") != '$':  # Wait for the begging of the string
            pass  # Do nothing
        line = ser.readline().decode("utf-8")  # Read the entire string
        return line

logging.basicConfig(filename='auto_capture.log', filemode='w', level=logging.INFO)

with open(os.path.abspath(os.getcwd()) + "/aerial-survey.yaml", "r") as yamlfile:
    configuration = yaml.load(yamlfile, Loader=yaml.FullLoader)

# in seconds
capture_interval = int(configuration['APP']['CAPTURE_INTERVAL'])

# in seconds
program_delay = int(configuration['APP']['PROGRAM_DELAY'])

# tuple of integers, split on x
resolution = tuple(int(x) for x in configuration['APP']['RESOLUTION'].split("x"))

# integer
rotation = int(configuration['APP']['ROTATION'])

# runtime in seconds
runtime = int(configuration['APP']['RUNTIME_MINUTES']) * 60

# number of pictures to take
num_pictures = math.floor(runtime / capture_interval)

# bool for whether or not a camera module is being used
use_camera = bool(configuration['APP']['USE_CAMERA'])

# bool for whether or not a GPS module is attached
use_gps = bool(configuration['APP']['USE_GPS'])

logging.info('Configuration file aerial-survey.yaml loaded with values CAPTURE_INTERVAL=' + str(capture_interval) + ', PROGRAM_DELAY=' + str(program_delay) + ', RESOLUTION=' + str(resolution) + ', ROTATION=' + str(rotation) + 'RUNTIME(s)=' + str(runtime) + 'USE_CAMERA=' + str(use_camera) + 'USE_GPS=' + str(use_gps))
logging.info('Sleeping for ' + str(program_delay) + ' seconds...')

# delay execution of program while OS boots
time.sleep(program_delay)

logging.info('Sleep complete. Beginning program...')

# take note of system time at beginning of program execution
# to denote experiment start time, and do mandatory setup
start_time = datetime.now()
capture_folder_name = "Captures_" + time.strftime("%Y-%m-%d_%H-%M-%S")
camera = PiCamera(resolution=resolution)
camera.rotation = rotation

logging.info("Camera initialized successfully.")

# retrieve the list of USBs connected to the Pi, and exit the program
# if none are detected - will not store captures on the SD card,
# because failure to manually clean out those files could cause the Pi
# to stop functioning
dest_drives = [os.path.join('/media/pi/', x) for x in os.listdir('/media/pi/')]
if(len(dest_drives) == 0):
    logging.error("No USB Drive detected.")
    exit()

# Select a USB with enough space. Goes through connected USBs
# alphabetically, and picks the first one that has > 500MB left
working_drive = get_working_drive(dest_drives)

logging.info("USB Drive " + working_drive + " was selected.")

# set up the directories and the modules for capturing photos
# and GPS data
capture_folder_path = working_drive + '/' + capture_folder_name + '/'
os.mkdir(capture_folder_path)

logging.info('Capture folder created at ' + capture_folder_path)

if use_gps == True and use_camera == True:
    os.system('cp GPS_Post_Processing.py ' + capture_folder_path.replace(" ", "\ "))
    logging.info('Post-processing script was copied to ' + capture_folder_path)

    csv_header = "GPS_Date(UTC),Status,Lat,Lat_Ref,Long,Long_Ref,Speed(knots),Mode,Pi_Date"
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    csv_file = open(capture_folder_path + "GPS_Data.csv", 'a')
    csv_file.write(csv_header + "\n")
    logging.info('.csv file was created for GPS data.')

    gpsthread = threading.Thread(target=GPSCapture, args=(capture_folder_path,csv_file,start_time,runtime))

    try:
        gpsthread.start()
        for i in range(num_pictures):
            camerathread = threading.Thread(target=newPhotoCapture, args=(capture_folder_path,))
            camerathread.start()
            time.sleep(capture_interval)
    except KeyboardInterrupt:
        csv_file.close()
        gpsthread.join()
        logging.warning("GPS thread terminated unexpectedly. Cleaned up securely.")
        camera.close()
        logging.warning('Camera script terminated unexpectedly. Cleaned up securely.')
        exit()

    csv_file.close()
    logging.info("GPS thread finished.")
    camera.close()
    logging.info("Finished.")

elif use_gps == False and use_camera == True:
    for i in range(num_pictures):
        camerathread = threading.Thread(target=newPhotoCapture, args=(capture_folder_path,))
        camerathread.start()
        time.sleep(capture_interval)
    camera.close()
    logging.info("Finished.")

elif use_gps == True and use_camera == False:
    os.system('cp GPS_Post_Processing.py ' + capture_folder_path.replace(" ", "\ "))
    logging.info('Post-processing script was copied to ' + capture_folder_path)

    csv_header = "GPS_Date(UTC),Status,Lat,Lat_Ref,Long,Long_Ref,Speed(knots),Mode,Pi_Date"
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    csv_file = open(capture_folder_path + "GPS_Data.csv", 'a')
    csv_file.write(csv_header + "\n")
    logging.info('.csv file was created for GPS data.')

    gpsthread = threading.Thread(target=GPSCapture, args=(capture_folder_path,csv_file,start_time,runtime))

    try:
        gpsthread.start()
        time.sleep(runtime)
    except KeyboardInterrupt:
        csv_file.close()
        gpsthread.join()
        logging.warning("GPS thread terminated unexpectedly. Cleaned up securely.")
        exit()

    csv_file.close()
    logging.info("GPS thread finished.")
    logging.info("Finished.")

else:
    logging.info("Finished.")
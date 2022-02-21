#Dependencies - installed via command line
###pip install GPSPhoto exifread

#This script only works if located in a folder that contains images produced by 
#the auto_camera.py script & the accompanying CSV file produced by auto_gps.py script

#This script automatically pulls the GPS information from the CSV file and adds the EXIF data to a new image
#It does this by matching the date/time of the image to the CSV file entry
#The new image will have the same name as the orginal but with the GPS tag added to the beginning 


from GPSPhoto import gpsphoto
import glob
import logging
import os
import pandas as pd


def dataLoad(local_directory, file_type):
    
    data_files = glob.glob(local_directory + "*." + file_type)
    
    return data_files


def matchGPS(image_date, gps_dates):
    
    image_date = image_date.split(".")
    
    image_date = image_date[0]
    
    image_gps_data = pd.DataFrame()
    
    for x in range(len(gps_dates)):
        
        if image_date == gps_dates['Pi_Date'][x]:
            
            image_gps_data = gps_dates.iloc[[x]]
            
            break
    
    return image_gps_data

logging.basicConfig(filename='GPS_Post_Processing.log', filemode='w', level=logging.INFO)

image_files = dataLoad("", "jpg")

csv_file = dataLoad("", "csv")

#Check for more than one csv

gps_data = pd.read_csv(csv_file[0])

os.system('mkdir Combined_Data/')


for image_file in image_files:

    logging.info("Combining file " + image_file + "...")
    print("Combining file " + image_file + "...")
    
    photo = gpsphoto.GPSPhoto(image_file)
    
    image_data = matchGPS(image_file, gps_data)
    
    if image_data.empty:
       
        logging.warning("No GPS data was received when this image was taken. Image could not be combined.")
        print("No GPS data was received when this image was taken. Image could not be combined.")

    else:
        
        if image_data['Lat'].item() == "No Data":
            
            logging.warning("GPS data for this image was malformed when you received it. Image could not be combined.")
            print("GPS data for this image was malformed when you received it. Image could not be combined.")
            
            continue;
        
        info = gpsphoto.GPSInfo((float(image_data['Lat']), float(image_data['Long'])))
    
        photo.modGPSData(info, "GPS_" + image_file)
        os.system('mv ' + 'GPS_' + image_file + ' Combined_Data/')
        logging.info("File combined successfully.")
        print("File combined successfully.")

logging.info("Done.")
print("Done.")
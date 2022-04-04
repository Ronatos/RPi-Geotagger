# RPi-Geotagger
A program written for Dr. Christopher Baynard of the University of North Florida to facilitate taking photos and attaching GPS data on a budget for his students of course code GEO4930.

## Potential Improvements
* The logging could be better, but it helped me while coding everything out, and can help get to the bottom of issues in the field.
* Exits aren't clean. The program ends when you want it to end, but usually via an error, not gracefully. Since the program is generally ended by ending the pi's power supply, this doesn't really matter too much, but isn't ideal.
* I've seen certain picameras show up in /dev/ being named differently than the expected hardcoded value, leading to errors. More testing should be done to reduce the frequency of this issue.

## Raspberry Pi Setup
1. Imaging the Raspberry Pi
  1. You need to install Raspberry Pi Imager on your computer. Raspberry Pi Imager is a quick and easy way to install Raspberry Pi OS and other operating systems to a microSD card, ready to use with your Raspberry Pi. Navigate to the following link, and download the correct version for your operating system: https://www.raspberrypi.com/software/
![image](https://user-images.githubusercontent.com/28655198/161562256-2ec62ec4-99f6-4050-80ea-3a3061e56af7.png)
  2. Collect the microSD card you will be using to run your Raspberry Pi, and plug it in to your computer that now has the Raspberry Pi Imager installed. You may need to use an SD card adapter if your computer does not have a microSD card slot.
  3. Launch the Raspberry Pi Imager program, and choose the operating system you want to use for your Raspberry Pi by clicking "CHOOSE OS". For the purpose of this course, we will be using Raspberry Pi OS (32-bit). Note that you will need to run the program with sudo if you intend to run the imager on Ubuntu.
![image](https://user-images.githubusercontent.com/28655198/161562452-67ff60a2-3ceb-4eaf-bf58-e3dbe604898c.png)
  4. Make sure your microSD card is plugged in to your computer, and select "CHOOSE STORAGE". Select your microSD card from the list to tell the Raspberry Pi Imager which device you want to apply the selected image to. A warning will be displayed stating that all data on the microSD card will be deleted. This is normal. Just be sure you don't need any data on that storage device before continuing.
  5. Select "WRITE", and the Raspberry Pi Imager will image the selected microSD card with the selected image. This process may take a while.
  6. Once this process completes, you will be presented with a message indicating that your microSD card was imaged successfully. At this time, you may plug in the card to your Raspberry Pi and boot to it. You will go through a short initial setup that sets your keyboard layout, time zone, and prompts you to connect to the internet. I do **not** recommend connecting to the internet during this.
2. Connecting to the Wi-Fi
  1. First, we will need the MAC address of the wireless interface for the Raspberry Pi we want to add to ClearPass. On your Pi, open a terminal and run the command ```ifconfig```. We need the MAC address of your wireless adapter. You should see some output that looks like this:
![image](https://user-images.githubusercontent.com/28655198/161558452-f29c2830-3bb7-40a8-95c4-d00c15b09c14.png)
  2. On another device, navigate to https://unf.edu/mydevices/ and sign in. Click on “Devices” on the left side of the page, and then click “Create New Device”.
![image](https://user-images.githubusercontent.com/28655198/161562573-1fbf6f85-2406-43c3-998d-38ffa6a343ab.png)
  3. From here, you will need to add the MAC address of the Raspberry Pi to the “MAC Address” field (Note, use dashes “-“ instead of colons “:”), and then provide your device with a name. Copy the additional options from the image below and click “Create”.
![image](https://user-images.githubusercontent.com/28655198/161562696-f7becd02-f067-4ed2-ab96-7b05104b3e95.png)
  4. Back on the Pi, connect to UNF-Visitor. This will only work after adding the device to ClearPass.
3. Update the Pi
  1. Open a terminal by pressing "Ctrl + Alt + T" or by opening it from the taskbar at the top of the screen.
  2. Type ```sudo apt update && sudo apt upgrade -y```.
  3. This process will likely take some time.
4. Editing /boot/config.txt
  1. Headless mode must be enabled because you will not be booting the Raspberry Pi with a monitor attached in the field. Open a terminal and enter ```sudo nano /boot/config.txt```
  2.  In this configuration file, the "#" symbol is used to comment out a line - meaning that if present, everything on that line after the "#" will not be used. We need remove the comment on a line in this file to allow headless mode to run. Find "#hdmi_force_hotplug=1", and change it to "hdmi_force_hotplug=1" by deleting the "#".
![image](https://user-images.githubusercontent.com/28655198/161562876-6ba55abc-bdb5-4c14-8a32-06b6eebcd8a0.png)
  3.  Additionally, if you are using a high definition camera, you will need to modify another line in this file to allocate more GPU memory. The value is called "gpu_mem", and is located near the bottom of the file. The default value should be 128. Adjust this to 176.
  4.  Use the Ctrl+O keybind to write the current file with all changes to disk. I like to remember it as "CONTROL write OUT". You may be prompted if you're sure you'd like to make changes. Confirm by pressing the enter key to verify the name of the file. Once you've saved your changes, use the Ctrl+X (for exit) keybind to exit the file.
5. Enabling the Raspberry Pi Camera and the GPS module
  1. Open a terminal by pressing "Ctrl + Alt + T" or by opening it from the taskbar at the top of the screen.
  2. Type ```sudo raspi-config```, omitting the quotation marks.
  3. Use the arrow keys to highlight "Interface Options", and press the enter key to select it.
![image](https://user-images.githubusercontent.com/28655198/161563082-e48e048c-0f17-45e6-9994-206277725e41.png)
  4. Select "Camera" from the list. It may be listed as legacy. This is fine.
![image](https://user-images.githubusercontent.com/28655198/161563133-b49d2d85-8bcf-430f-b176-3e7cf50f849e.png)
  5. You will then be prompted to enable the camera. Select "Yes".
  6. Use the arrow keys or tab key to return to the "Interface Options" menu, where we will then select "Serial Port".
  7.  You will then be prompted to allow a login shell to be accessible over serial. Select "Yes".
  8.  Use the arrow keys or tab key to return to the main menu and select "Finish". Reboot if prompted to do so.

## Installation
1. Open a new terminal and type "git clone https://github.com/Ronatos/rpi-geotagger.git"
2. A new folder will be created in your home folder called rpi-geotagger. In the same terminal, type ```cd rpi-geotagger/```.
3. Now type ```./install.sh``` to install the required packages. This may take a few moments.
4. Once the installation is complete, type "crontab -e". If prompted to select an editor, nano is the easiest to use.
![image](https://user-images.githubusercontent.com/28655198/161564503-0180fdd5-a817-406a-a704-166cf384181a.png)
5. Navigate to the bottom of the file and add the following line: ```@reboot /usr/bin/python3 /home/pi/auto_capture.py```
6. Save and exit the file.

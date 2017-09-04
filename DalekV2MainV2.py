#!/usr/bin/env python

#======================================================================
# Main Imports and setup constants

# Module Imports
import RPi.GPIO as GPIO  # Import GPIO divers
import time              # Import the Time library
import DalekV2Drive      # Import my 4 Motor controller
import cwiid             # Import WiiMote code
import argparse          # Import Argument Parser
import scrollphat        # Import Scroll pHat code
import numpy as np       # Import NumPy Array manipulation
import cv2               # Import OpenCV Vision code

#PiCamera imports
from picamera.array import PiRGBArray
from picamera import PiCamera
import picamera

# End PiCamera Imports

# Main Imports and setup constants
speed = 50               # 0 is stopped, 100 is fastest
rightspeed = 50          # 0 is stopped, 100 is fastest
leftspeed = 50           # 0 is stopped, 100 is fastest
maxspeed = 100           # Set full Power
minspeed = 0             # Set min power  
innerturnspeed = 40      # Speed for Inner Wheels in a turn
outerturnspeed = 80      # Speed for Outer Wheels in a turn
hRes = 640               # PiCam Horizontal Resolution
vRes = 480               # PiCam Virtical Resolution
camera = 0               # Create PiCamera Object
video_capture = 0        # Create WebCam Object
 
#TRIG = 40  # Set the Trigger pin
#ECHO = 38  # Set the Echo pin

# End of single character reading
#======================================================================

#======================================================================
# Reading single character by forcing stdin to raw mode
import sys
import tty
import termios

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
        raise KeyboardInterrupt
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)  # 16=Up, 17=Down, 18=Right, 19=Left arrows

# End of single character reading
#======================================================================

#======================================================================
# Initialisation procedures

def setup():                   # Setup GPIO and Initalise Imports
    connected = False
    while connected == False:
        connected = setupwii() # Setup and connect to WiiMote
    #GPIO.setmode(GPIO.BOARD)  # Set the GPIO pins as numbering - Set in DalekV2Drive.py
    GPIO.setwarnings(False)    # Turn GPIO warnings off - CAN ALSO BE Set in DalekV2Drive.py
    #GPIO.setup(TRIG,GPIO.OUT) # Set the Trigger pin to output
    #GPIO.setup(ECHO,GPIO.IN)  # Set the Echo pin to input
    DalekV2Drive.init()        # Initialise my software to control the motors
 
    # Setup PiCam
    # initialize the camera and grab a reference to the raw camera capture
    global hRes                # Allow Access to PiCam Horizontal Resolution
    global vRes                # Allow Access to PiCam Vertical Resolution
    global camera              # Allow Access to PiCamera Object

    camera = picamera.PiCamera()
    print "default resolution = " + str(camera.resolution) 
    camera.resolution = (hRes,vRes)
    print "updated resolution = " + str(camera.resolution) 
    #camera.framerate = 32
    camera.framerate = 60
    #camera.hflip = True
    camera.rotation = 180
 
    # Setup WebCam
    global video_capture       # Allow Access to WebCam Object
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, hRes)
    video_capture.set(4, vRes)

    print '\nPress some buttons!\n'
    print 'Press PLUS and MINUS together to disconnect and quit.\n'

  
def setupwii():
    # Connect Wiimote
    print '\n\nPress & hold 1 + 2 on your Wii Remote now ...\n\n'
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string("1+2")

    # Connect to the Wii Remote. If it times out
    # then quit.
    global wii

    try:
        wii=cwiid.Wiimote()
    except RuntimeError:
        print 'Error opening wiimote connection'
        scrollphat.clear()         # Shutdown Scroll pHat
        scrollphat.write_string("Err")
        time.sleep(0.5)
        return False

    print 'Wii Remote connected...\n'
    wii.rumble = 1
    time.sleep(0.1)
    wii.rumble = 0
    
    wii.led = 1
    time.sleep(0.75) 
    wii.led = 2
    time.sleep(0.75)
    wii.led = 4
    time.sleep(0.75)
    wii.led = 8
    time.sleep(0.75)
    battery = int(wii.state['battery']/25)
    
    if battery == 4:
        wii.led = 8
    elif battery == 3:
        wii.led = 4
    elif battery == 2:
        wii.led = 2
    else: 
        wii.led = 1
    
    wii.rumble = 1
    time.sleep(0.1)
    wii.rumble = 0
    
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string("Gd")

    print '\nPress some buttons!\n'
    print 'Press PLUS and MINUS together to disconnect and quit.\n'
    
    return True
  
# End of Initialisation procedures
#======================================================================

#======================================================================
# Service Procedures
   
def getdistance(distance):
    GPIO.output(TRIG, False)
    print "Waiting For Sensor To Settle"
    time.sleep(0.05)
    pulse_end = 0

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
        # print 'start', GPIO.input(ECHO)
        pulse_start = time.time()
  
    while GPIO.input(ECHO)==1:
        # print 'stop', GPIO.input(ECHO)
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print "Distance:",distance,"cm"
    return distance
    
# ---- Function definition for converting scales ------
def remap(unscaled, to_min, to_max, from_min, from_max):
    return (to_max-to_min)*(unscaled-from_min)/(from_max-from_min)+to_min
    
# End of Service Procedures    
#======================================================================

#======================================================================
# Clean-up Procedures  
    
def destroy():                 # Shutdown GPIO and Cleanup modules
    print "\n... Shutting Down...\n"
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string("Ext")
    DalekV2Drive.stop()        # Make sure Bot is not moving when program exits
    DalekV2Drive.cleanup()     # Shutdown all motor control
    global camera              # Allow Access to PiCamera Object 
    if camera._check_camera_open() == True:
        camera.close()             # Shutdown Pi Camera
    global wii
    wii.rumble = 1
    time.sleep(0.5)
    wii.rumble = 0
    scrollphat.clear()         # Clear Scroll pHat
    GPIO.cleanup()             # Release GPIO resource
    
# End of Clean-up Procedures  
#======================================================================

#======================================================================    
# Task Procedures  

def ObstacleCourse():

    global speed               # Allow access to 'speed' constant
    global rightspeed          # Allow access to 'rightspeed' constant
    global leftspeed           # Allow access to 'leftspeed' constant
    global maxspeed            # Allow access to 'maxspeed' constant
    global minspeed            # Allow access to 'minspeed' constant
    global innerturnspeed      # Speed for Inner Wheels in a turn
    global outerturnspeed      # Speed for Outer Wheels in a turn
    global wii                 # Allow access to 'Wii' constants

    wii.rpt_mode = cwiid.RPT_BTN
    
    time.sleep(2)
    
    boost = 0                                   # Turn boost off

    while True:
        buttons = wii.state['buttons']          # Get WiiMote Button Pressed
        # Choose which task to do
        #keyp = readkey()                       # For Keyboard control
        keyp = '0'                              # Dummy to stop errors
        
        # If Plus and Minus buttons pressed
        # together then rumble and quit.
        if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):  
           break  

        print speed
        scrollphat.clear()         # Shutdown Scroll pHat
        scrollphat.write_string(str(speed))
        
        if boost == 0 and (buttons & cwiid.BTN_B):
            print 'Boost', maxspeed
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Max")
            savespeed = speed
            speed = maxspeed
            boost = 1
            time.sleep(.25)
        elif boost == 1 and (buttons & cwiid.BTN_B):
            speed = savespeed
            boost = 0
            print 'Normal', speed
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Nor")
            time.sleep(.25)
        
        if keyp == 'w' or ord(keyp) == 16 or (buttons & cwiid.BTN_UP):
            print 'Forward', speed
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Fw")
            DalekV2Drive.forward(speed)
            time.sleep(.25)
        elif keyp == 'z' or ord(keyp) == 17 or (buttons & cwiid.BTN_DOWN):
            print 'Backward', speed
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Bw")
            DalekV2Drive.backward(speed)
            time.sleep(.25)
        elif keyp == 'n' or ord(keyp) == 19 or (buttons & cwiid.BTN_LEFT):
            print 'Spin Left', speed
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("SL")
            DalekV2Drive.spinLeft(maxspeed)
            time.sleep(.25)
        elif keyp == 'm' or ord(keyp) == 19 or (buttons & cwiid.BTN_RIGHT):
            print 'Spin Right', speed
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("SR")
            DalekV2Drive.spinRight(maxspeed)
            time.sleep(.25)
        elif keyp == 's' or ord(keyp) == 18 or (buttons & cwiid.BTN_1):
            print 'Turn Right'
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("TrR")
            DalekV2Drive.turnForwardRight(outerturnspeed, innerturnspeed)
            time.sleep(.25)
        elif keyp == 'a' or ord(keyp) == 19 or (buttons & cwiid.BTN_2):
            print 'Turn Left'
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("TrL")
            DalekV2Drive.turnForwardLeft(innerturnspeed, outerturnspeed)
            time.sleep(.25)
        elif keyp == '.' or keyp == '>' or (buttons & cwiid.BTN_PLUS):
            print 'Speed Up 1'
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("+1")
            if speed < 100:
                speed = speed + 1
                time.sleep(0.5)
        elif keyp == ',' or keyp == '<' or (buttons & cwiid.BTN_MINUS):
            print 'Speed Down 1'
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("-1")
            if speed > 0:
                speed = speed - 1
                time.sleep(0.5)
        elif keyp == ' ' or (buttons & cwiid.BTN_A):
            print 'Stop'
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Stp")
            DalekV2Drive.stop()
            time.sleep(.25)
        elif keyp == ' ' or (buttons & cwiid.BTN_HOME):
            DalekV2Drive.stop()
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Hm")
            print "\n\nReturning to Main Menu\n\n"
            time.sleep(1)
            print "Main Menu"               # Show we are on main menu
            print '\nUp    - ObstacleCourse'
            print 'Down  - StreightLine'
            print 'Left  - MinimaMaze'
            print 'Right - Golf'
            print '1     - Line Follow WebCam'
            print '2     - Line Follow PiCam'
            print 'Home  - Exit\n'
            print "Ready"
            break
    
#def StreightLine():
    
#def MinimuMaze():

#def Golf():

def LineFollowWebCam(showcam):

    global speed               # Allow access to 'speed' constant
    global rightspeed          # Allow access to 'rightspeed' constant
    global leftspeed           # Allow access to 'leftspeed' constant
    global maxspeed            # Allow access to 'maxspeed' constant
    global minspeed            # Allow access to 'minspeed' constant
    global innerturnspeed      # Speed for Inner Wheels in a turn
    global outerturnspeed      # Speed for Outer Wheels in a turn
    global wii                 # Allow access to 'Wii' constants
    global hRes                # Allow Access to Cam Horizontal Resolution
    global vRes                # Allow Access to Cam Vertical Resolution
    global video_capture       # Allow Access to WebCam Object
    
    cx = 300                   # Go Streight
    turnspeed = 95
    speed = 30
    
    print'\nPress "A" to start Line following'
    print'Press "Hm" to return to main menu\n'
        
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string('"A"')
    time.sleep(.25)

    while True:
    
        buttons = wii.state['buttons']          # Get WiiMote Button Pressed
        # Choose which task to do
        #keyp = readkey()                       # For Keyboard control
        keyp = '0'                              # Dummy to stop errors

        if (buttons & cwiid.BTN_A):
            print 'Start Line Following'
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string('LiF')
            time.sleep(.25)
            cx = 300                   # Go Streight
            
            while True:
            
                buttons = wii.state['buttons']          # Get WiiMote Button Pressed
                # Choose which task to do
                #keyp = readkey()                       # For Keyboard control
                keyp = '0'                              # Dummy to stop errors
            
                if (buttons & cwiid.BTN_HOME):
                    DalekV2Drive.stop()
                    print'\nPress "A" to start Line following'
                    print'Press "Hm" to return to main menu\n'
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string('"A"')
                    time.sleep(.25)
                    break
            
                # Capture from camera
                ret, frame = video_capture.read()
     
                # Crop, select part of image to work with
                crop_img = frame[380:480, 0:640]

                # Make the image greyscale
                gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

                # uncomment next line to view greyscale image
                #cv2.imshow('Gray',gray) 
 
                # Apply a Gaussian blur
                blur = cv2.GaussianBlur(gray,(5,5),0)

                # uncomment next line to view Blurred image
                #cv2.imshow('Blur',blur)
 
                # Apply Color thresholding
                ret,thresh = cv2.threshold(blur,100,255,cv2.THRESH_BINARY_INV)

                # uncomment next line to view Threshholded image    
                #cv2.imshow('Thresh',thresh)
 
                # Find the contours in the cropped image part
                img, contours, hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

                # ---------------- Find the biggest contour = line -----------------
    
                if len(contours) > 0:
                    c = max(contours, key=cv2.contourArea)
                    M = cv2.moments(c)
 
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
 
                    cv2.line(crop_img,(cx,0),(cx,720),(255,255,0),2)
                    cv2.line(crop_img,(0,cy),(1280,cy),(0,255,0),2)
                    cv2.drawContours(crop_img, contours, -1, (0,255,255), 2)

                    # ---- Draw centre boundry lines (Steer straight)
                    cv2.line(crop_img,(270,0),(270,480),(0,0,255),2)
                    cv2.line(crop_img,(370,0),(370,480),(0,0,255),2)

                # --------- Steer Right Routine ----------
                if cx >= 370:
                    RSteer = cx - 370
                    SteerRight = remap(RSteer, 0, 45, 1, 270)
                    print "Turn Right: ", SteerRight, cx
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string("TrR")
                    DalekV2Drive.spinRight(turnspeed)

                # --------- On Track Routine ----------
                if cx < 370 and cx > 270:
                    print "On Track", cx
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string("Fw")
                    DalekV2Drive.forward(speed)

                # --------- Steer Left Routine ----------
                if cx <= 270:
                    LSteer = 270 - cx
                    SteerLeft = remap(LSteer, 0, 45, 1, 270)
                    print "Turn Left: ", SteerLeft, cx
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string("TrL")
                    DalekV2Drive.spinLeft(turnspeed)
 
                # ------ Show the resulting cropped image
                if showcam == True:
                    cv2.imshow('frame',crop_img)
                # ------ Exit if Q pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                                
        elif (buttons & cwiid.BTN_HOME):
            DalekV2Drive.stop()
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Hm")
            print "\n\nReturning to Main Menu\n\n"
            time.sleep(1)
            print "Main Menu"               # Show we are on main menu
            print '\nUp    - ObstacleCourse'
            print 'Down  - StreightLine'
            print 'Left  - MinimaMaze'
            print 'Right - Golf'
            print '1     - Line Follow WebCam'
            print '2     - Line Follow PiCam'
            print 'Home  - Exit\n'
            print "Ready"
            break

def LineFollowPiCam(showcam):

    global speed               # Allow access to 'speed' constant
    global rightspeed          # Allow access to 'rightspeed' constant
    global leftspeed           # Allow access to 'leftspeed' constant
    global maxspeed            # Allow access to 'maxspeed' constant
    global minspeed            # Allow access to 'minspeed' constant
    global innerturnspeed      # Speed for Inner Wheels in a turn
    global outerturnspeed      # Speed for Outer Wheels in a turn
    global wii                 # Allow access to 'Wii' constants
    global hRes                # Allow Access to PiCam Horizontal Resolution
    global vRes                # Allow Access to PiCam Vertical Resolution
    global camera              # Allow Access to PiCamera Object
    
    cx = 300                   # Go Streight
    turnspeed = 95
    speed = 30
    
    rawCapture = PiRGBArray(camera, size=(hRes, vRes))
    #camera.capture(video_capture,format="bgr")
    time.sleep(0.1)
    
    if camera._check_camera_open() == False:                            # check if VideoCapture object was associated to webcam successfully
        print "error: capWebcam not accessed successfully\n\n"              # if not, print error message to std out
        os.system("pause")                                                  # pause until user presses a key so user can see error message
        #return                                                             # and exit function (which exits program)
        exit()
        # end if
    
    print'\nPress "A" to start Line following'
    print'Press "Hm" to return to main menu\n'
        
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string('"A"')
    time.sleep(.25)

    while True:
    
        buttons = wii.state['buttons']          # Get WiiMote Button Pressed
        # Choose which task to do
        #keyp = readkey()                       # For Keyboard control
        keyp = '0'                              # Dummy to stop errors

        if (buttons & cwiid.BTN_A):
            print 'Start Line Following'
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string('LiF')
            time.sleep(.25)
            cx = 300                   # Go Streight
            # capture frames from the camera
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
                         
                imgOriginal = frame.array
                # print 'Wait...'
                # clear the stream in preparation for the next frame
                rawCapture.truncate(0)
 
                # Crop, select part of image to work with
                crop_img = imgOriginal[380:480, 0:640]

                # Make the image greyscale
                gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

                # uncomment next line to view greyscale image
                #cv2.imshow('Gray',gray) 
 
                # Apply a Gaussian blur
                blur = cv2.GaussianBlur(gray,(5,5),0)

                # uncomment next line to view Blurred image
                #cv2.imshow('Blur',blur)
 
                # Apply Color thresholding
                ret,thresh = cv2.threshold(blur,100,255,cv2.THRESH_BINARY_INV)

                # uncomment next line to view Threshholded image    
                #cv2.imshow('Thresh',thresh)

                # Find the contours in the cropped image part
                img, contours, hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

                # ---------------- Find the biggest contour = line -----------------
    
                if len(contours) > 0:
                    c = max(contours, key=cv2.contourArea)
                    M = cv2.moments(c)
 
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
 
                    cv2.line(crop_img,(cx,0),(cx,720),(255,255,0),2)
                    cv2.line(crop_img,(0,cy),(1280,cy),(0,255,0),2)
                    cv2.drawContours(crop_img, contours, -1, (0,255,255), 2)

                    # ---- Draw centre boundry lines (Steer straight)
                    cv2.line(crop_img,(270,0),(270,480),(0,0,255),2)
                    cv2.line(crop_img,(370,0),(370,480),(0,0,255),2)

                if cx >= 370:
                    RSteer = cx - 370
                    SteerRight = remap(RSteer, 0, 45, 1, 270)
                    print "Turn Right: ", SteerRight, cx
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string("TrR")
                    DalekV2Drive.spinRight(turnspeed)

                # --------- On Track Routine ----------
                if cx < 370 and cx > 270:
                    print "On Track", cx
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string("Fw")
                    DalekV2Drive.forward(speed)

                # --------- Steer Left Routine ----------
                if cx <= 270:
                    LSteer = 270 - cx
                    SteerLeft = remap(LSteer, 0, 45, 1, 270)
                    print "Turn Left: ", SteerLeft, cx
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string("TrL")
                    DalekV2Drive.spinLeft(turnspeed)
                    
                # ------ Show the resulting cropped image
                if showcam == True:
                    cv2.imshow('frame',crop_img)
                # ------ Exit if Q pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                buttons = wii.state['buttons']          # Get WiiMote Button Pressed
                
                if (buttons & cwiid.BTN_HOME):
                    DalekV2Drive.stop()
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string("Hm")
                    print "\n\nReturning to Main Menu\n\n"
                    time.sleep(1)
                    print'\nPress "A" to start Line following'
                    print'Press "Hm" to return to main menu\n'
                    scrollphat.clear()         # Shutdown Scroll pHat
                    scrollphat.write_string('"A"')
                    time.sleep(.25)
                    break
                                
        elif (buttons & cwiid.BTN_HOME):
            DalekV2Drive.stop()
            #camera.close()             # Shutdown PiCam
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Hm")
            print "\n\nReturning to Main Menu\n\n"
            time.sleep(1)
            print '\nUp    - ObstacleCourse'
            print 'Down  - StreightLine'
            print 'Left  - MinimaMaze'
            print 'Right - Golf'
            print '1     - Line Follow WebCam'
            print '2     - Line Follow PiCam'
            print 'Home  - Exit\n'
            print "Ready"
            break
            
# End of Task Procedures  
#======================================================================    

#======================================================================    
# Main Control Procedure
    
def maincontrol(showcam):                  # Main Control Loop

    global wii                      # Allow access to 'Wii' constants

    scrollphat.clear()              # Clear Scroll pHat
    scrollphat.write_string("Mn")   # Show we are on main menu
    print "Main Menu"               # Show we are on main menu

    print '\nUp    - ObstacleCourse'
    print 'Down  - StreightLine'
    print 'Left  - MinimaMaze'
    print 'Right - Golf'
    print '1     - Line Follow WebCam'
    print '2     - Line Follow PiCam'
    print 'Home  - Exit\n'
    
    wii.rpt_mode = cwiid.RPT_BTN

    print "Ready"
    
    while True:
        buttons = wii.state['buttons']          # Get WiiMote Button Pressed
        # Choose which task to do
        #keyp = readkey()                       # For Keyboard control
        keyp = '0'                              # Dummy to stop errors

     
        # If Plus and Minus buttons pressed
        # together then rumble and quit.
        if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):  
            break  
 
        if keyp == 'w' or ord(keyp) == 16 or (buttons & cwiid.BTN_UP):
            print 'ObstacleCourse'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("OC")
            ObstacleCourse()
        elif keyp == 'z' or ord(keyp) == 17 or (buttons & cwiid.BTN_DOWN):
            print 'StreightLine'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("StL")
            #StreightLine()
        elif keyp == 'n' or ord(keyp) == 19 or (buttons & cwiid.BTN_LEFT):
            print 'MinimalMaze'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("MM")
            #MinimalMaze()
        elif keyp == 'm' or ord(keyp) == 19 or (buttons & cwiid.BTN_RIGHT):
            print 'Golf'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("Golf")
            #ObstacleCourse()
        elif keyp == 's' or ord(keyp) == 18 or (buttons & cwiid.BTN_1):
            print 'Line Follow WebCam'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("LiF")
            LineFollowWebCam(showcam)
        elif keyp == 'a' or ord(keyp) == 19 or (buttons & cwiid.BTN_2):
            print 'Line Follow PiCam'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("LiF")
            LineFollowPiCam(showcam)
        elif keyp == '.' or keyp == '>' or (buttons & cwiid.BTN_PLUS):
            print '+'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("+")
            #NotAssigned()
        elif keyp == ',' or keyp == '<' or (buttons & cwiid.BTN_MINUS):
            print '-'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("-")
            #NotAssigned()
        elif keyp == ' ' or (buttons & cwiid.BTN_HOME): #or (buttons & cwiid.BTN_A):
            break

        DalekV2Drive.stop()

# End of Main Control Procedure        
#======================================================================            

#======================================================================            
# __Main__ Startup Loop        
       
if __name__ == '__main__': # The Program will start from here
        
    # Get and parse Arguments
    parser = argparse.ArgumentParser(description='Dalek Motor Control Test Program')
    parser.add_argument('-r',dest='RightSpeed', type=float, help='Initial speed of Right motors (0 - 100)')       # Initial speed of Right Motors
    parser.add_argument('-l',dest='LeftSpeed', type=float, help='Initial speed of Left Motors (0 - 100)')         # Initial speed of Left Motors
    parser.add_argument('-s',dest='Speed', type=float, help='Initial General speed of Motors (0 - 100)')          # Initial General speed of Motors
    parser.add_argument('-b',dest='Brightness', type=float, help='Brightness of scrollpHat (0 - 5)')              # Brightness of scrollpHat
    parser.add_argument('-i',dest='InnerTurnSpeed', type=float, help='Speed of Inner wheels in a turn (0 - 100)') # Speed of Inner wheels in a turn
    parser.add_argument('-o',dest='OuterTurnSpeed', type=float, help='Speed of Inner wheels in a turn (0 - 100)') # Speed of Outer wheels in a turn
    parser.add_argument('-c',dest='ShowCam', type=bool, help='Show Image from Active Cam (True/False)')           # Show Image from Active Cam
    args = parser.parse_args()
    
    if ((str(args.RightSpeed)) != 'None'):
        print '\nRight Speed - ',(str(args.RightSpeed))
        rightspeed = args.RightSpeed

    if ((str(args.LeftSpeed)) != 'None'):
        print 'Left Speed - ',(str(args.LeftSpeed))
        leftspeed = args.LeftSpeed

    if ((str(args.Speed)) != 'None'):
        print '\nGeneral Speed - ',(str(args.Speed))
        speed = args.Speed
    
    if ((str(args.Brightness)) != 'None'):
        print '\nscrollpHat Brightness - ',(str(args.Brightness))
        scrollphat.set_brightness(int(args.Brightness))

    if ((str(args.InnerTurnSpeed)) != 'None'):
        print '\nInner Turn Speed - ',(str(args.InnerTurnSpeed))
        innerturnspeed = args.InnerTurnSpeed
    
    if ((str(args.OuterTurnSpeed)) != 'None'):
        print '\nOuter Turn Speed - ',(str(args.OuterTurnSpeed))
        outerturnspeed = args.OuterTurnSpeed
 
    if ((str(args.ShowCam)) != 'None'):
        print '\nShow Cam Image - ',(str(args.ShowCam))
        showcam = args.ShowCam
    else:
        showcam = False
  
    print '\n\nSetting Up ...\n'
    scrollphat.clear()         # Clear Scroll pHat
    scrollphat.write_string("Set")

    setup()           # Setup all motors and Wii

    print '\nGo ...\n\n'
    scrollphat.clear()         # Clear Scroll pHat
    scrollphat.write_string("Go")
	
    try:
        maincontrol(showcam)    # Call main loop
        destroy()     # Shutdown
        print "\n\n................... Exit .......................\n\n"
        exit(0) # Exit Cleanly
    except KeyboardInterrupt:
        destroy()
        print "\n\n................... Exit .......................\n\n"
        exit(0) # Exit Cleanly
        
# End of __Main__ Startup Loop 
#======================================================================

#!/usr/bin/python

# Module Imports
import RPi.GPIO as GPIO
import time              # Import the Time library
import DalekV2Drive      # Import my 4 Motor controller
import cwiid             # Import WiiMote code
import argparse

# Define Constants (Global Variables)
speed = 50 # 0 is stopped, 100 is fastest
rightspeed = 50 # 0 is stopped, 100 is fastest
leftspeed = 50 # 0 is stopped, 100 is fastest
#TRIG = 40  # Set the Trigger pin
#ECHO = 38  # Set the Echo pin
#buttons = 0 # Button state

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

def setup():                  # Setup GPIO and Initalise Imports
    #GPIO.setmode(GPIO.BOARD) # Set the GPIO pins as numbering - Set in DalekV2Drive.py
    GPIO.setwarnings(False)   # Turn GPIO warnings off - CAN ALSO BE Set in DalekV2Drive.py
    #GPIO.setup(TRIG,GPIO.OUT)# Set the Trigger pin to output
    #GPIO.setup(ECHO,GPIO.IN) # Set the Echo pin to input
    DalekV2Drive.init()       # Initialise my software to control the motors
    connected = False
    while connected == False:
        connected = setupwii()                # Setup and connect to WiiMote
   
def setupwii():
    # Connect Wiimote
    print '\n\nPress & hold 1 + 2 on your Wii Remote now ...\n\n'

    # Connect to the Wii Remote. If it times out
    # then quit.
    global wii

    try:
        wii=cwiid.Wiimote()
    except RuntimeError:
        print 'Error opening wiimote connection'
        return False

    print 'Wii Remote connected...\n'
    wii.rumble = 1
    time.sleep(0.1)
    wii.rumble = 0
    print '\nPress some buttons!\n'
    print 'Press PLUS and MINUS together to disconnect and quit.\n'
    
    #print '\nControl the motors by using the arrow keys'
    #print 'Use , or < to slow down'
    #print 'Use . or > to speed up'
    #print 'Speed changes take effect when the next arrow key is pressed'
    print 'Press Ctrl-C to end\n'

    return True
    
def destroy():    # Shutdown GPIO and Cleanup modules
    print "\n... Shutting Down...\n"
    DalekV2Drive.stop()  # Make sure Bot is not moving when program exits
    DalekV2Drive.cleanup()
    GPIO.cleanup() # Release resource
    
# Service Subroutines    
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

def ObstacleCourse():

    global speed               # Allow access to 'speed' constants
    global rightspeed          # Allow access to 'rightspeed' constants
    global leftspeed           # Allow access to 'leftspeed' constants
    global wii                 # Allow access to 'Wii' constants

    wii.rpt_mode = cwiid.RPT_BTN
    
    time.sleep(2)

    while True:
        buttons = wii.state['buttons']          # Get WiiMote Button Pressed
        # Choose which task to do
        #keyp = readkey()  # For Keyboard control
        keyp = '0'         # Dummy to stop errors
        
        # If Plus and Minus buttons pressed
        # together then rumble and quit.
        if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):  
            print '\nClosing connection ...'
            wii.rumble = 1
            time.sleep(1)
            wii.rumble = 0
            exit(wii)  

        print speed
            
        if keyp == 'w' or ord(keyp) == 16 or (buttons & cwiid.BTN_UP):
            print 'Forward', speed
            DalekV2Drive.forward(speed)
        elif keyp == 'z' or ord(keyp) == 17 or (buttons & cwiid.BTN_DOWN):
            print 'Backward', speed
            DalekV2Drive.backward(speed)
        elif keyp == 'n' or ord(keyp) == 19 or (buttons & cwiid.BTN_LEFT):
            print 'Spin Left', speed
            DalekV2Drive.spinLeft(speed)
        elif keyp == 'm' or ord(keyp) == 19 or (buttons & cwiid.BTN_RIGHT):
            print 'Spin Right', speed
            DalekV2Drive.spinRight(speed)
        elif keyp == 's' or ord(keyp) == 18 or (buttons & cwiid.BTN_1):
            print '1'
            #Fight()
        elif keyp == 'a' or ord(keyp) == 19 or (buttons & cwiid.BTN_2):
            print '2'
            #NotAssigned()
        elif keyp == '.' or keyp == '>' or (buttons & cwiid.BTN_PLUS):
            print 'Speed Up 1'
            if speed < 100:
                speed = speed + 1
                time.sleep(0.5)
        elif keyp == ',' or keyp == '<' or (buttons & cwiid.BTN_MINUS):
            print 'Speed Down 1'
            if speed > 0:
                speed = speed - 1
                time.sleep(0.5)
        elif keyp == ' ' or (buttons & cwiid.BTN_A):
            print 'Stop'
            DalekV2Drive.stop()
        elif keyp == ' ' or (buttons & cwiid.BTN_HOME):
            print "\n\nReturning to Main Menu\n\n"
            time.sleep(2)
            break

    
#def StreightLine():
    
#def MinimuMaze():

#def Golf():

#def Fight():
    
def mainloop():            # Main Program Loop

    global speed               # Allow access to 'speed' constants
    global rightspeed          # Allow access to 'rightspeed' constants
    global leftspeed           # Allow access to 'leftspeed' constants
    global wii                 # Allow access to 'Wii' constants

    #print 'Speed...' + str(speed) + '...LeftSpeed...' + str(leftspeed) + '...Right Speed...' + str(rightspeed)

    print '\nUp    - ObstacleCourse'
    print 'Down  - StreightLine'
    print 'Left  - MinimaMaze'
    print 'Right - Golf'
    print '1     - Fight\n'
    
    wii.rpt_mode = cwiid.RPT_BTN

    time.sleep(2)
    
    while True:
        buttons = wii.state['buttons']          # Get WiiMote Button Pressed
        # Choose which task to do
        #keyp = readkey()  # For Keyboard control
        keyp = '0'         # Dummy to stop errors
        
        # If Plus and Minus buttons pressed
        # together then rumble and quit.
        if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):  
            print '\nClosing connection ...'
            wii.rumble = 1
            time.sleep(1)
            wii.rumble = 0
            exit(wii)  
          
        if keyp == 'w' or ord(keyp) == 16 or (buttons & cwiid.BTN_UP):
            print 'ObstacleCourse'
            ObstacleCourse()
        elif keyp == 'z' or ord(keyp) == 17 or (buttons & cwiid.BTN_DOWN):
            print 'StreightLine'
            #StreightLine()
        elif keyp == 'n' or ord(keyp) == 19 or (buttons & cwiid.BTN_LEFT):
            print 'MinimalMaze'
            #MinimalMaze()
        elif keyp == 'm' or ord(keyp) == 19 or (buttons & cwiid.BTN_RIGHT):
            print 'Golf'
            #ObstacleCourse()
        elif keyp == 's' or ord(keyp) == 18 or (buttons & cwiid.BTN_1):
            print 'Fight'
            #Fight()
        elif keyp == 'a' or ord(keyp) == 19 or (buttons & cwiid.BTN_2):
            print 'Not Assigned'
            #NotAssigned()
        elif keyp == '.' or keyp == '>' or (buttons & cwiid.BTN_PLUS):
            print 'Not Assigned'
            #NotAssigned()
        elif keyp == ',' or keyp == '<' or (buttons & cwiid.BTN_MINUS):
            print 'Not Assigned'
            #NotAssigned()
        elif keyp == ' ' or (buttons & cwiid.BTN_HOME) or (buttons & cwiid.BTN_A):
            print 'Not Assigned'
            #NotAssigned()
        elif ord(keyp) == 3:
            break

        DalekV2Drive.stop()
        
       
if __name__ == '__main__': # The Program will start from here
        
    # Get and parse Arguments
    parser = argparse.ArgumentParser(description='Dalek Motor Control Test Program')
    parser.add_argument('-r',dest='RightSpeed', type=float, help='Initial speed of Right motors')   # Initial speed of Right Motors
    parser.add_argument('-l',dest='LeftSpeed', type=float, help='Initial speed of Left Motors')     # Initial speed of Left Motors
    parser.add_argument('-s',dest='Speed', type=float, help='Initial General speed of Motors')      # Initial General speed of Motors
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
        
    
    print '\n\nSetting Up ...\n'
    setup()

    print '\nGo ...\n\n'
	
    try:
        mainloop()    # Call main loop
        destroy()     # Shutdown
        sys.exit(-1) # Exit Cleanly
    except KeyboardInterrupt:
        destroy()
        sys.exit(-1) # Exit Cleanly

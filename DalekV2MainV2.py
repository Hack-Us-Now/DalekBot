#!/usr/bin/python

# Module Imports
import RPi.GPIO as GPIO
import time              # Import the Time library
import DalekV2Drive      # Import my 4 Motor controller
import argparse

# Define Constants (Global Variables)
speed = 50 # 0 is stopped, 100 is fastest
rightspeed = 50 # 0 is stopped, 100 is fastest
leftspeed = 50 # 0 is stopped, 100 is fastest
#TRIG = 40  # Set the Trigger pin
#ECHO = 38  # Set the Echo pin

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

def setup():   # Setup GPIO and Initalise Imports
    #GPIO.setmode(GPIO.BOARD) # Set the GPIO pins as numbering - Set in DalekV2Drive.py
    GPIO.setwarnings(False)   # Turn GPIO warnings off - CAN ALSO BE Set in DalekV2Drive.py
    #GPIO.setup(TRIG,GPIO.OUT)# Set the Trigger pin to output
    #GPIO.setup(ECHO,GPIO.IN) # Set the Echo pin to input
    DalekV2Drive.init()       # Initialise my software to control the motors
    
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

#def StreightLine():
    
#def MinimumMaze():

#def Golf():

#def ObstacleCourse():

#def Fight():
    
def mainloop():            # Main Program Loop

    global speed               # Allow access to 'speed' constants
    global rightspeed          # Allow access to 'rightspeed' constants
    global leftspeed           # Allow access to 'leftspeed' constants
    
    while True:
        
        # Insert code to connect to WiiMote and choose which task to do
        print 'Forward ...'
        DalekV2Drive.forward(speed)
        time.sleep(2)
        DalekV2Drive.stop()
        
       
if __name__ == '__main__': # The Program will start from here
    
    # Streight line
    # Minimum Maze
    # Golf
    # Obstacle course
    # Fight
        
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

    #time.sleep(2)

    print '\nGo ...\n\n'
	
    try:
        mainloop()    # Call main loop
        #DalekV2Drive.BRB(70)
        #time.sleep(1)
        destroy()     # Shutdown
    except KeyboardInterrupt:
        destroy()

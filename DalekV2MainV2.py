#!/usr/bin/python

# Module Imports
import RPi.GPIO as GPIO
import time              # Import the Time library
import DalekV2Drive      # Import my 4 Motor controller
import cwiid             # Import WiiMote code
import argparse          # Import Argument Parser
import scrollphat        # Import Scroll pHat code

# Define Constants (Global Variables)
speed = 50               # 0 is stopped, 100 is fastest
rightspeed = 50          # 0 is stopped, 100 is fastest
leftspeed = 50           # 0 is stopped, 100 is fastest
maxspeed = 100           # Set full Power
minspeed = 0             # Set min power  
innerturnspeed = 40      # Speed for Inner Wheels in a turn
outerturnspeed = 80      # Speed for Outer Wheels in a turn
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
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string("1+2")

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
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string("Gd")

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
    scrollphat.clear()         # Shutdown Scroll pHat
    scrollphat.write_string("Cls")
    DalekV2Drive.stop()        # Make sure Bot is not moving when program exits
    scrollphat.clear()         # Shutdown Scroll pHat    
    DalekV2Drive.cleanup()     # Shutdown all motor control
    GPIO.cleanup()             # Release GPIO resource
    
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

    global speed               # Allow access to 'speed' constant
    global rightspeed          # Allow access to 'rightspeed' constant
    global leftspeed           # Allow access to 'leftspeed' constant
    global maxspeed            # Allow access to 'maxspeed' constant
    global minspeed            # Allow access to 'minspeed' constant
    global wii                 # Allow access to 'Wii' constants
    global innerturnspeed      # Speed for Inner Wheels in a turn
    global outerturnspeed      # Speed for Outer Wheels in a turn

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
        scrollphat.clear()         # Shutdown Scroll pHat
        scrollphat.write_string(str(speed))
            
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
            scrollphat.clear()         # Shutdown Scroll pHat
            scrollphat.write_string("Hm")
            print "\n\nReturning to Main Menu\n\n"
            time.sleep(2)
            print "Main Menu"               # Show we are on main menu
            print '\nUp    - ObstacleCourse'
            print 'Down  - StreightLine'
            print 'Left  - MinimaMaze'
            print 'Right - Golf'
            print '1     - Fight\n'
            print "Ready"
            break
    
#def StreightLine():
    
#def MinimuMaze():

#def Golf():

#def Fight():
    
def mainloop():            # Main Program Loop

    #global speed               # Allow access to 'speed' constants
    #global rightspeed          # Allow access to 'rightspeed' constants
    #global leftspeed           # Allow access to 'leftspeed' constants
    global wii                 # Allow access to 'Wii' constants

    #print 'Speed...' + str(speed) + '...LeftSpeed...' + str(leftspeed) + '...Right Speed...' + str(rightspeed)
    
    scrollphat.clear()              # Clear Scroll pHat
    scrollphat.write_string("Mn")   # Show we are on main menu
    print "Main Menu"               # Show we are on main menu

    print '\nUp    - ObstacleCourse'
    print 'Down  - StreightLine'
    print 'Left  - MinimaMaze'
    print 'Right - Golf'
    print '1     - Fight\n'
    
    wii.rpt_mode = cwiid.RPT_BTN

    time.sleep(2)
    
    print "Ready"
    
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
            print 'Fight'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("Fit")
            #Fight()
        elif keyp == 'a' or ord(keyp) == 19 or (buttons & cwiid.BTN_2):
            print '2'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("2")
            #NotAssigned()
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
            print 'Exit'
            scrollphat.clear()         # Clear Scroll pHat
            scrollphat.write_string("Ext")
            #NotAssigned()
            break

        DalekV2Drive.stop()
       
       
if __name__ == '__main__': # The Program will start from here
        
    # Get and parse Arguments
    parser = argparse.ArgumentParser(description='Dalek Motor Control Test Program')
    parser.add_argument('-r',dest='RightSpeed', type=float, help='Initial speed of Right motors')       # Initial speed of Right Motors
    parser.add_argument('-l',dest='LeftSpeed', type=float, help='Initial speed of Left Motors')         # Initial speed of Left Motors
    parser.add_argument('-s',dest='Speed', type=float, help='Initial General speed of Motors')          # Initial General speed of Motors
    parser.add_argument('-b',dest='Bright', type=float, help='Brightness of scrollpHat')                # Brightness of scrollpHat
    parser.add_argument('-i',dest='InnerTurnSpeed', type=float, help='Speed of Inner wheels in a turn') # Speed of Inner wheels in a turn
    parser.add_argument('-o',dest='OuterTurnSpeed', type=float, help='Speed of Inner wheels in a turn') # Speed of Outer wheels in a turn
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
    
    if ((str(args.Bright)) != 'None'):
        print '\nscrollpHat Brightness - ',(str(args.Bright))
        scrollphat.set_brightness(int(args.Bright))

    if ((str(args.InnerTurnSpeed)) != 'None'):
        print '\nInner Turn Speed - ',(str(args.InnerTurnSpeed))
        innerturnspeed = args.InnerTurnSpeed
    
    if ((str(args.OuterTurnSpeed)) != 'None'):
        print '\nOuter Turn Speed - ',(str(args.OuterTurnSpeed))
        outerturnspeed = args.OuterTurnSpeed
        
    print '\n\nSetting Up ...\n'
    scrollphat.clear()         # Clear Scroll pHat
    scrollphat.write_string("Set")

    setup()           # Setup all motors and Wii

    print '\nGo ...\n\n'
    scrollphat.clear()         # Clear Scroll pHat
    scrollphat.write_string("Go")
	
    try:
        mainloop()    # Call main loop
        destroy()     # Shutdown
        print "\n\n................... Exit .......................\n\n"
        sys.exit(0) # Exit Cleanly
    except KeyboardInterrupt:
        destroy()
        print "\n\n................... Exit .......................\n\n"
        sys.exit(0) # Exit Cleanly

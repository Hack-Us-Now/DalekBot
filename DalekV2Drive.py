#!/usr/bin/env python

import RPi.GPIO as GPIO # Import the GPIO Library

# Set variables for the GPIO motor pins
# print '\n\nSet variables for the GPIO motor pins'
pinMotorFRSpeed=11
pinMotorFRForwards=15
pinMotorFRBackwards=13

pinMotorFLSpeed=22
pinMotorFLForwards=26
pinMotorFLBackwards=24

pinMotorBRSpeed = 8
pinMotorBRForwards = 10
pinMotorBRBackwards = 12

pinMotorBLSpeed = 19
pinMotorBLForwards = 23
pinMotorBLBackwards = 21

#======================================================================
# General Functions
#

# init(). Initialises GPIO pins, switches motors and LEDs Off, etc
def init():
    global pwmMotorFRSpeed, pwmMotorFLSpeed, pwmMotorBRSpeed, pwmMotorBLSpeed, Stop

    # How many times to turn the pin on and off each second
    print 'Set Frequency'
    Frequency = 20
    # How long the pin stays on each cycle, as a percent (here, it's 50%) - AKA Speed
    print 'Set DutyCycle'	
    DutyCycle = 50
	# Settng the duty cycle to 0 means the motors will not turn
    print 'Set Stop'
    Stop = 0

    # Set the GPIO modes
    print 'Set the GPIO mode'
    # Use physical pin numbering
    GPIO.setmode(GPIO.BOARD)
    # Turn GPIO Warnings off
    # GPIO.setwarnings(False)

    # Use PWM on motor outputs so motors can be controlled

    # Setup Motor FR
    print '\nSet the GPIO Pin mode to be Output - Motor FR'
    GPIO.setup(pinMotorFRSpeed, GPIO.OUT)
    GPIO.setup(pinMotorFRForwards, GPIO.OUT)
    GPIO.setup(pinMotorFRBackwards, GPIO.OUT)

    print 'Set the GPIO to software PWM at ' + str(Frequency) + ' Hertz - Motor FR'
    pwmMotorFRSpeed = GPIO.PWM(pinMotorFRSpeed, Frequency)

    print 'Start the software PWM with a duty cycle of 0 (i.e. not moving) - Moter FR'
    pwmMotorFRSpeed.start(Stop)
    
    # Setup Motor FL
    print '\nSet the GPIO Pin mode to be Output - Motor FL'
    GPIO.setup(pinMotorFLSpeed, GPIO.OUT)
    GPIO.setup(pinMotorFLForwards, GPIO.OUT)
    GPIO.setup(pinMotorFLBackwards, GPIO.OUT)

    print 'Set the GPIO to software PWM at ' + str(Frequency) + ' Hertz - Motor FL'
    pwmMotorFLSpeed = GPIO.PWM(pinMotorFLSpeed, Frequency)

    print 'Start the software PWM with a duty cycle of 0 (i.e. not moving) - Moter FL'
    pwmMotorFLSpeed.start(Stop)
    
    # Setup Motor BR
    print '\nSet the GPIO Pin mode to be Output - Motor BR'
    GPIO.setup(pinMotorBRSpeed, GPIO.OUT)
    GPIO.setup(pinMotorBRForwards, GPIO.OUT)
    GPIO.setup(pinMotorBRBackwards, GPIO.OUT)

    print 'Set the GPIO to software PWM at ' + str(Frequency) + ' Hertz - Motor BR'
    pwmMotorBRSpeed = GPIO.PWM(pinMotorBRSpeed, Frequency)

    print 'Start the software PWM with a duty cycle of 0 (i.e. not moving) - Moter BR'
    pwmMotorBRSpeed.start(Stop)

    # Setup Motor BL
    print '\nSet the GPIO Pin mode to be Output - Motor BL'
    GPIO.setup(pinMotorBLSpeed, GPIO.OUT)
    GPIO.setup(pinMotorBLForwards, GPIO.OUT)
    GPIO.setup(pinMotorBLBackwards, GPIO.OUT)

    print 'Set the GPIO to software PWM at ' + str(Frequency) + ' Hertz - Motor BL'
    pwmMotorBLSpeed = GPIO.PWM(pinMotorBLSpeed, Frequency)

    print 'Start the software PWM with a duty cycle of 0 (i.e. not moving) - Moter BL\n'
    pwmMotorBLSpeed.start(Stop)
    
# cleanup(). Sets all motors off and sets GPIO to standard values
def cleanup():
        stop()
        GPIO.cleanup()

# End of General Functions
#======================================================================


#======================================================================
# Motor Functions

# Turn all motors off
def stop():
    pwmMotorFRSpeed.ChangeDutyCycle(Stop)
    pwmMotorFLSpeed.ChangeDutyCycle(Stop)
    pwmMotorBRSpeed.ChangeDutyCycle(Stop)
    pwmMotorBLSpeed.ChangeDutyCycle(Stop)

# forward(speed): Sets all 4 motors to move forward at speed. 0 <= speed <= 100
def forward(Speed):
    pwmMotorFRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFRForwards, GPIO.HIGH)
    GPIO.output(pinMotorFRBackwards, GPIO.LOW)
    
    pwmMotorFLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFLForwards, GPIO.HIGH)
    GPIO.output(pinMotorFLBackwards, GPIO.LOW)
	
    pwmMotorBRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBRForwards, GPIO.HIGH)
    GPIO.output(pinMotorBRBackwards, GPIO.LOW)
    
    pwmMotorBLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBLForwards, GPIO.HIGH)
    GPIO.output(pinMotorBLBackwards, GPIO.LOW)

# backward(speed): Sets all 4 motors to reverse at speed. 0 <= speed <= 100
def backward(Speed):
    pwmMotorFRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFRForwards, GPIO.LOW)
    GPIO.output(pinMotorFRBackwards, GPIO.HIGH)
    
    pwmMotorFLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFLForwards, GPIO.LOW)
    GPIO.output(pinMotorFLBackwards, GPIO.HIGH)

    pwmMotorBRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBRForwards, GPIO.LOW)
    GPIO.output(pinMotorBRBackwards, GPIO.HIGH)
    
    pwmMotorBLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBLForwards, GPIO.LOW)
    GPIO.output(pinMotorBLBackwards, GPIO.HIGH)

# The theory for the next 4 is that by setting the inside wheels backward and putting a small value there it will 
# act like a braake and cause the Bot to turn rather than just spinning.
    
# turnForwardRight(leftSpeed, rightSpeed): Moves forwards in an arc by setting Left forward and Right backward
def turnForwardRight(leftSpeed, rightSpeed):
    pwmMotorFRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorFRForwards, GPIO.LOW)
    GPIO.output(pinMotorFRBackwards, GPIO.HIGH)

    pwmMotorBRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorBRForwards, GPIO.LOW)
    GPIO.output(pinMotorBRBackwards, GPIO.HIGH)
    
    pwmMotorFLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorFLForwards, GPIO.HIGH)
    GPIO.output(pinMotorFLBackwards, GPIO.LOW)
   
    pwmMotorBLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorBLForwards, GPIO.HIGH)
    GPIO.output(pinMotorBLBackwards, GPIO.LOW)
    
# turnForwardLeft(leftSpeed, rightSpeed): Moves forwards in an arc by setting Left backward and Right forward
def turnForwardLeft(leftSpeed, rightSpeed):
    pwmMotorFRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorFRForwards, GPIO.HIGH)
    GPIO.output(pinMotorFRBackwards, GPIO.LOW)

    pwmMotorBRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorBRForwards, GPIO.HIGH)
    GPIO.output(pinMotorBRBackwards, GPIO.LOW)

    pwmMotorFLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorFLForwards, GPIO.LOW)
    GPIO.output(pinMotorFLBackwards, GPIO.HIGH)
    
    pwmMotorBLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorBLForwards, GPIO.LOW)
    GPIO.output(pinMotorBLBackwards, GPIO.HIGH)
	
# turnBackwardRight(leftSpeed, rightSpeed): Moves backward in an arc by setting Right forward and left backward
def turnBackwardRight(leftSpeed, rightSpeed):
    pwmMotorFRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorFRForwards, GPIO.LOW)
    GPIO.output(pinMotorFRBackwards, GPIO.HIGH)

    pwmMotorBRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorBRForwards, GPIO.LOW)
    GPIO.output(pinMotorBRBackwards, GPIO.HIGH)
    
    pwmMotorFLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorFLForwards, GPIO.HIGH)
    GPIO.output(pinMotorFLBackwards, GPIO.LOW)
   
    pwmMotorBLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorBLForwards, GPIO.HIGH)
    GPIO.output(pinMotorBLBackwards, GPIO.LOW)
    
# turnBackwardLeft(leftSpeed, rightSpeed): Moves backward in an arc by setting Right backward and left forward
def turnBackwardLeft(leftSpeed, rightSpeed):
    pwmMotorFRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorFRForwards, GPIO.LOW)
    GPIO.output(pinMotorFRBackwards, GPIO.HIGH)

    pwmMotorBRSpeed.ChangeDutyCycle(rightSpeed)
    GPIO.output(pinMotorBRForwards, GPIO.LOW)
    GPIO.output(pinMotorBRBackwards, GPIO.HIGH)

    pwmMotorFLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorFLForwards, GPIO.HIGH)
    GPIO.output(pinMotorFLBackwards, GPIO.LOW)
    
    pwmMotorBLSpeed.ChangeDutyCycle(leftSpeed)
    GPIO.output(pinMotorBLForwards, GPIO.HIGH)
    GPIO.output(pinMotorBLBackwards, GPIO.LOW)

# spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spinLeft(Speed):
    pwmMotorFRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFRForwards, GPIO.HIGH)
    GPIO.output(pinMotorFRBackwards, GPIO.LOW)

    pwmMotorBRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBRForwards, GPIO.HIGH)
    GPIO.output(pinMotorBRBackwards, GPIO.LOW)
    
    pwmMotorFLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFLForwards, GPIO.LOW)
    GPIO.output(pinMotorFLBackwards, GPIO.HIGH)
   
    pwmMotorBLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBLForwards, GPIO.LOW)
    GPIO.output(pinMotorBLBackwards, GPIO.HIGH)

# spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spinRight(Speed):
    pwmMotorFLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFLForwards, GPIO.HIGH)
    GPIO.output(pinMotorFLBackwards, GPIO.LOW)

    pwmMotorBLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBLForwards, GPIO.HIGH)
    GPIO.output(pinMotorBLBackwards, GPIO.LOW)

    pwmMotorFRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFRForwards, GPIO.LOW)
    GPIO.output(pinMotorFRBackwards, GPIO.HIGH)
	
    pwmMotorBRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBRForwards, GPIO.LOW)
    GPIO.output(pinMotorBRBackwards, GPIO.HIGH)
    
    
# End of Motor Functions
#======================================================================	

#======================================================================	
# Test Functions
#======================================================================	

def FRF(Speed):
    pwmMotorFRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFRForwards, GPIO.HIGH)
    GPIO.output(pinMotorFRBackwards, GPIO.LOW)
    
def FLF(Speed):
    pwmMotorFLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFLForwards, GPIO.HIGH)
    GPIO.output(pinMotorFLBackwards, GPIO.LOW)
    
def BRF(Speed):
    pwmMotorBRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBRForwards, GPIO.HIGH)
    GPIO.output(pinMotorBRBackwards, GPIO.LOW)
   
def BLF(Speed):
    pwmMotorBLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBLForwards, GPIO.HIGH)
    GPIO.output(pinMotorBLBackwards, GPIO.LOW)
    
def FRB(Speed):
    pwmMotorFRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFRForwards, GPIO.LOW)
    GPIO.output(pinMotorFRBackwards, GPIO.HIGH)
    
def FLB(Speed):
    pwmMotorFLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorFLForwards, GPIO.LOW)
    GPIO.output(pinMotorFLBackwards, GPIO.HIGH)

def BRB(Speed):
    pwmMotorBRSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBRForwards, GPIO.LOW)
    GPIO.output(pinMotorBRBackwards, GPIO.HIGH)
   
def BLB(Speed):
    pwmMotorBLSpeed.ChangeDutyCycle(Speed)
    GPIO.output(pinMotorBLForwards, GPIO.LOW)
    GPIO.output(pinMotorBLBackwards, GPIO.HIGH)
   
# End of Test Functions
#======================================================================	

#======================================================================	
# __main__ Code
#======================================================================	   
    
if __name__ == "__main__":
    print("\n\nThis file cannot be run directly. It is intended to be imported\n\n")
else:
    print("\n\nImporting DalekV2Drive.py")
    
# End of __main__ Code
#======================================================================
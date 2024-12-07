#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.media.ev3dev import Font

# Create your objects here.
ev3 = EV3Brick()    #ev3
obstacle_sensor = UltrasonicSensor(Port.S4)     #MotionSensor
line_sensor = ColorSensor(Port.S1)
touch_sensor = TouchSensor(Port.S2)

# Initialize the motors
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

#variables
dis = 0

def drive():
  robot.drive_time(-100, 0, 1000)


def obstacle_avoidance():
 wait(2)
 ev3.speaker.beep()
 #robot.drive_time(0,0,1000)
  # robot.turn(117)
   #if obstacle_sensor.distance() < 100:
    # robot.turn(-234)
     #robot.drive_time(-100,0,10000)
     #ev3.speaker.say("right")
   #else:
    # robot.drive_time(-100,0,10000)
     #robot.turn(-117)
     #robot.drive_time(-100,0,10000)
     #robot.turn(-117)
     #robot.drive_time(-100,0,10000)
     #robot.turn(117)
     #robot.drive_time(-100,0,10000)
     #ev3.speaker.say("left")  

#Startup
#robot.drive_time(-100,0,1000)

ev3.speaker.say("Place medicine")
wait(5)

while dis < 4:
  drive()
  dis = dis + 1
  ev3.speaker.say("One")
  while obstacle_sensor.distance() < 200:
      obstacle_avoidance()

robot.turn(117)

while dis < 6:
  drive()
  dis = dis + 1
  ev3.speaker.say("One")
  while obstacle_sensor.distance() < 200:
      obstacle_avoidance()

robot.turn(-117)

while dis < 5:
  drive()
  dis = dis + 1
  ev3.speaker.say("One")
  while obstacle_sensor.distance() < 200:
      obstacle_avoidance()

ev3.speaker.say("Done")

#while dis < 8:
#  robot.drive_time(-100,0,1000)
#  dis = dis + 1
#  ev3.speaker.say("Two")

#robot.turn(117)
#while dis < 10:
#  robot.drive_time(-100,0,1000)
#  dis = dis + 1
#  ev3.speaker.say("Three")
#while obstacle_sensor.distance() < 1000:
 # obstacle_avoidance()

#robot.drive_time(-100,0,10000)
#ev3.speaker.say("Hallo")

#def func1():
 # robot.straight(-100)
#def func2():
  #robot.drive_time(0, 0, 2000)
  #ev3.speaker.say("Obstacle")

#if obstacle_sensor.distance() < 1000:
  #func1
  #ev3.speaker.say("Obstacle")      

#if obstacle_sensor.distance() > 1000:   
 # func1() 
#else obstacle_sensor.distance() <= 1000:
  #  func2()      

 #while touch_sensor.pressed(True):
 #       robot.stop(stop.BRAKE)
  #      ev3.speaker.say("Ralf stopped")
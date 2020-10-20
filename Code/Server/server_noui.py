import io
import os
import socket
import struct
import time
import threading
import picamera
import sys, getopt
import random
import RPi.GPIO as GPIO
from threading import Thread
from Thread import *
from server import Server
from evdev import InputDevice, categorize, ecodes
from rpi_ws281x import *
from select import select
from Motor import *
from Buzzer import *
from Ultrasonic import *
from ADC import *
from servo import *
from gpiozero import LED
from Led import Led
from TailLight import TailLight
from SevenSegDisplay import SevenSegDisplay

ARM = '2'
HAND = '3'
SPACE = 57
OK = 28
LEFT = 105
RIGHT = 106
UP = 103
DOWN = 108
VUP = 115
VDOWN = 114
PLAY = 164
PREV = 165
NEXT = 163
CONFIG = 171
ESCAPE = 1
DANCE = 32
STARTAUTO = 22
STARTLINE = 23
STARTLIGHT = 38

ARMSTART = 150 
ARMEND = 35
HANDSTART = 25 
HANDEND = 100

HEADLIGHTPIN = 16
LEFTGREENPIN = 21
RIGHTGREENPIN = 21
LEFTREDPIN = 26
RIGHTREDPIN = 20

# # Dance moves
DLEFT = 101
DRIGHT = 102
DSPIN = 103
DFORWARD = 104
DBACK = 105
DARMUP = 106
DARMDOWN = 107
DCLAP = 108
DTOOT = 109
DSPEED = 1  # speed of each move in seconds


class myapp():
    
    def __init__(self, motor=None, headlight=None, taillight=None, buzzer=None):
        self.PWM = motor
        self.serverup = False
        self.automode = False
        self.taillight = taillight
        self.TCP_Server = Server(motor, headlight, taillight, buzzer)
        self.adc = Adc()
        self.led = Led()
        self.buzzer = buzzer
        self.myservo = Servo()
        print "Initializing..."
        self.on_pushButton()
                        
    def close(self):
        print "Closing down..."
        try:
           stop_thread(self.SendVideo)
           stop_thread(self.ReadData)
           stop_thread(self.power)
        except:
            pass
        try:
            self.TCP_Server.server_socket.shutdown(2)
            self.TCP_Server.server_socket1.shutdown(2)
            self.TCP_Server.StopTcpServer()
        except:
            pass
        self.serverup = False
        print "Close TCP" 
        os._exit(0)
    
    def on_pushButton(self):
        if self.serverup == False:
            self.TCP_Server.tcp_Flag = True
            print "Open TCP"
            self.TCP_Server.StartTcpServer()
            self.SendVideo = Thread(target=self.TCP_Server.sendvideo)
            self.ReadData = Thread(target=self.TCP_Server.readdata)
            self.power = Thread(target=self.TCP_Server.Power)
            self.SendVideo.start()
            self.ReadData.start()
            self.power.start()
            self.serverup = True
            
        elif self.serverup == True:
            self.TCP_Server.tcp_Flag = False
            try:
                stop_thread(self.ReadData)
                stop_thread(self.power)
                stop_thread(self.SendVideo)
            except:
                pass
            
            self.TCP_Server.StopTcpServer()
            self.serverup = False
            print "Close TCP"
 
    def run_light_thread(self):
        self.automode = True
        threading.Thread(target=self.run_light).start()
            
    def run_line_thread(self):
        self.automode = True
        threading.Thread(target=self.run_line).start()
        
    def run_ultrasonic_thread(self):
        self.automode = True
        threading.Thread(target=self.run_ultrasonic).start()
        
    def run_dance_thread(self):
        self.automode = True
        threading.Thread(target=self.run_dance).start()    
    
    # Event types
    # 0 - d < x
    # 1 - d >= x
    # 2 - l > r   - for future enhancement not using in first try
    # 3 - l <= r  - ditto
    def run_ultrasonic(self):
        ttable = [[1, 0], [2, 4], [3, 5], [1, 1], [0, 0], [0, 0]]
        x = 40
        ultra = Ultrasonic()
        print "Auto drive Start!"
        
        cur_state = 0
        
        while self.automode:
            if cur_state == 0:
                self.PWM.slowforward()
                ultra.look_forward()
            elif cur_state == 1:
                self.PWM.stopMotor()
                ultra.look_left()
            elif cur_state == 2:
                self.PWM.stopMotor()
                ultra.look_right()
            elif cur_state == 3:
                self.PWM.backup()
            elif cur_state == 4:
                self.PWM.turnLeft()
                time.sleep(0.2)
            elif cur_state == 5:
                self.PWM.turnRight()
                time.sleep(0.2)
            else:
                print "Wrong state?"
                cur_state = 0

            time.sleep(0.3)
            d = ultra.get_distance()
            
            e = 0 if d < x else 1
            cur_state = ttable[cur_state][e]
            
        print "Auto drive End!"
            
    def run_line(self):
        IR01 = 14
        IR02 = 15
        IR03 = 23
        print "Line Follow Start!"
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IR01, GPIO.IN)
        GPIO.setup(IR02, GPIO.IN)
        GPIO.setup(IR03, GPIO.IN)
        while self.automode:
            self.LMR = 0x00
            if GPIO.input(IR01) == True:
                self.LMR = (self.LMR | 4)
            if GPIO.input(IR02) == True:
                self.LMR = (self.LMR | 2)
            if GPIO.input(IR03) == True:
                self.LMR = (self.LMR | 1)
            if self.LMR == 2:
                self.PWM.setMotorModel(800, 800, 800, 800)
            elif self.LMR == 4:
                self.PWM.setMotorModel(-1500, -1500, 2500, 2500)
            elif self.LMR == 6:
                self.PWM.setMotorModel(-2000, -2000, 4000, 4000)
            elif self.LMR == 1:
                self.PWM.setMotorModel(2500, 2500, -1500, -1500)
            elif self.LMR == 3:
                self.PWM.setMotorModel(4000, 4000, -2000, -2000)
            elif self.LMR == 7:
                pass
        print "Line Follow End!"
            
    def run_light(self):
        print "Light follow start!"
        self.PWM.setMotorModel(0, 0, 0, 0)
        while self.automode:
            L = self.adc.recvADC(0)
            R = self.adc.recvADC(1)
            if L < 2.99 and R < 2.99 :
                self.PWM.setMotorModel(600, 600, 600, 600)
                
            elif abs(L - R) < 0.15:
                self.PWM.setMotorModel(0, 0, 0, 0)
                
            elif L > 3 or R > 3:
                if L > R :
                    self.PWM.setMotorModel(-1200, -1200, 1400, 1400)
                    
                elif R > L :
                    self.PWM.setMotorModel(1400, 1400, -1200, -1200)
        print "Light follow finished!"
    
    def dancemove(self, *args):
        for move in args:
	    if not self.automode:
		break
            if move == DLEFT:
                self.PWM.turnLeft()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
            elif move == DRIGHT:
                self.PWM.turnRight()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
            elif move == DSPIN:
                self.PWM.spin()
                time.sleep(DSPEED * 2)
                self.PWM.stopMotor()
            elif move == DFORWARD:
                self.PWM.slowforward()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
            elif move == DBACK:
                self.PWM.slowBackup()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
            elif move == DTOOT:
                self.buzzer.run('1')
                time.sleep(DSPEED/2)
                self.buzzer.run('0')
                time.sleep(DSPEED/2)
            elif move == DARMUP:
                self.myservo.setServoPwm(ARM, (ARMSTART + ARMEND) * 2 / 3)
                time.sleep(DSPEED)
            elif move == DARMDOWN:
                self.myservo.setServoPwm(ARM, (ARMSTART + ARMEND) * 1 / 3)
                time.sleep(DSPEED)
            elif move == DCLAP:
                self.myservo.setServoPwm(HAND, HANDEND)
                time.sleep(DSPEED)
                self.myservo.setServoPwm(HAND, HANDSTART)
		time.sleep(DSPEED)
            else:
                print "Invalid dance move?"
            
    def run_dance(self):
        print "Dance moves"
        self.PWM.setMotorModel(0, 0, 0, 0)
        # start light show
        mode = str(random.randint(1, 4))
        ledthread = Thread(target=self.led.ledMode, args=(mode,))
        ledthread.start()
        while self.automode:
            self.dancemove(DLEFT, DFORWARD, DBACK, DRIGHT, DRIGHT, DFORWARD, DBACK, DLEFT, DARMDOWN, DARMUP, DCLAP, DSPIN, DTOOT, DTOOT)
	    #self.dancemove(DARMUP, DARMDOWN, DCLAP)
        # stop light show when done
        stop_thread(ledthread)
	self.led.colorWipe(self.led, Color(0,0,0),10)
        print "Dance moves finished"


if __name__ == '__main__':
    devices = map(InputDevice, ('/dev/input/event0', '/dev/input/event3'))
    devices = {dev.fd: dev for dev in devices}
    for dev in devices.values(): 
         print(dev)
    buzzer = Buzzer()
    curarmangle = ARMSTART
    curhandangle = HANDSTART
    headlight = LED(HEADLIGHTPIN)
    taillight = TailLight(LEFTREDPIN, LEFTGREENPIN, RIGHTREDPIN, RIGHTGREENPIN)
    display = SevenSegDisplay()
    display.show(0, "Ishani's robot")
    
    PWM = Motor(taillight)
    myshow = myapp(PWM, headlight, taillight, buzzer)
    
    myshow.myservo.setServoPwm(ARM, curarmangle)
    myshow.myservo.setServoPwm(HAND, curhandangle)
    sdcount = 0
    try:
        while True:
           r, w, x = select(devices, [], [])
           for fd in r:
              for event in devices[fd].read():
                if event.type == ecodes.EV_KEY:
                    if event.value == 0:  # release stop
                        if event.code != 57:
                            if PWM.moving and not(myshow.automode):
			    	PWM.stopMotor()  # This will turn on the taillight
                            	display.show(1, "Stop")
                            buzzer.run('0')
                            sdcount = 0
                    elif event.value == 1:  # press - start
                        if event.code == UP:
                            PWM.forward()
                            display.show(1, "Forward")
                        elif event.code == DOWN:
                            PWM.backup()
                            display.show(1, "Backward")
                        elif event.code == LEFT:
                            PWM.turnLeft()
                            display.show(1, "LEFT")
                        elif event.code == RIGHT:
                            PWM.turnRight()
                            display.show(1, "RIGHT")
                        elif event.code == SPACE:
                            myshow.on_pushButton()
                            display.show(1, "Server start-stop")
                        elif event.code == OK:
                            buzzer.run('1') 
                            display.show(1, "Horn!")
                        elif event.code == VUP:
                            display.show(1, "Arm up")
                            if curarmangle <= ARMSTART - 5:
                                curarmangle = curarmangle + 5
                                myshow.myservo.setServoPwm(ARM, curarmangle)
                        elif event.code == VDOWN:
                            display.show(1, "Arm down")
                            if curarmangle >= ARMEND + 5:
                                curarmangle = curarmangle - 5
                                myshow.myservo.setServoPwm(ARM, curarmangle)
                        elif event.code == PLAY:
                            display.show(1, "Arm rest")
                            curarmangle = (ARMSTART + ARMEND) / 2
                            myshow.myservo.setServoPwm(ARM, curarmangle)
                        elif event.code == PREV:
                            display.show(1, "OPEN")
                            myshow.myservo.setServoPwm(HAND, HANDSTART)
                        elif event.code == NEXT:
                            display.show(1, "CLOSE")
                            myshow.myservo.setServoPwm(HAND, HANDEND)
                        elif event.code == CONFIG:
                            display.show(1, "LIGHT on-off")
                            headlight.toggle()
                        elif event.code == ESCAPE:
                            display.show(1, "AUTO END")
                            myshow.automode = False
                        elif event.code == STARTAUTO:
                            display.show(1, "AUTO START")
                            myshow.run_ultrasonic_thread()
                        elif event.code == STARTLINE:
                            display.show(1, "LINE START")
                            myshow.run_line_thread()
                        elif event.code == STARTLIGHT:
                            display.show(1, "LIGHT START")
                            myshow.run_light_thread()
                        elif event.code == DANCE:
                            display.show(1, "DANCE!")
                            myshow.run_dance_thread()
                        else:
                            display.show(1, "UNKNOWN KEY")
                            print(categorize(event))
                    elif event.value == 2:  # Holding - long press processing
                        if event.code == 57:  # long press play/pause button
                            sdcount = sdcount + 1
    		if sdcount > 30:
                    display.show(1, "POWER OFF")
                    os.system("sudo poweroff")
    except KeyboardInterrupt:
        myshow.close()

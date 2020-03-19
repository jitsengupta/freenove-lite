import io
import os
import socket
import struct
import time
import threading
import picamera
import sys,getopt
import RPi.GPIO as GPIO
from threading import Thread
from Thread import *
from server import Server
from evdev import InputDevice, categorize, ecodes
from select import select
from Motor import *
from Buzzer import *
from Ultrasonic import *
from ADC import *
from servo import *
from gpiozero import LED
from TailLight import TailLight
from Display import Display

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
STARTAUTO = 22
STARTLINE = 23
STARTLIGHT = 38


ARMSTART = 40 
ARMEND = 155
HANDSTART = 25 
HANDEND = 100

HEADLIGHTPIN = 16
LEFTGREENPIN = 21
RIGHTGREENPIN = 21
LEFTREDPIN = 26
RIGHTREDPIN = 20

class myapp():
    
    def __init__(self, motor=None, headlight=None, taillight = None, buzzer = None):
        self.PWM=motor
        self.serverup=False
        self.automode=False
        self.taillight = taillight
        self.TCP_Server=Server(motor, headlight, taillight, buzzer)
        self.adc = Adc()
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
        if self.serverup==False:
            self.TCP_Server.tcp_Flag = True
            print "Open TCP"
            self.TCP_Server.StartTcpServer()
            self.SendVideo=Thread(target=self.TCP_Server.sendvideo)
            self.ReadData=Thread(target=self.TCP_Server.readdata)
            self.power=Thread(target=self.TCP_Server.Power)
            self.SendVideo.start()
            self.ReadData.start()
            self.power.start()
            self.serverup = True
            
        elif self.serverup==True:
            self.TCP_Server.tcp_Flag = False
            try:
                stop_thread(self.ReadData)
                stop_thread(self.power)
                stop_thread(self.SendVideo)
            except:
                pass
            
            self.TCP_Server.StopTcpServer()
            self.serverup=False
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
        GPIO.setup(IR01,GPIO.IN)
        GPIO.setup(IR02,GPIO.IN)
        GPIO.setup(IR03,GPIO.IN)
        while self.automode:
            self.LMR=0x00
            if GPIO.input(IR01)==True:
                self.LMR=(self.LMR | 4)
            if GPIO.input(IR02)==True:
                self.LMR=(self.LMR | 2)
            if GPIO.input(IR03)==True:
                self.LMR=(self.LMR | 1)
            if self.LMR==2:
                self.PWM.setMotorModel(800,800,800,800)
            elif self.LMR==4:
                self.PWM.setMotorModel(-1500,-1500,2500,2500)
            elif self.LMR==6:
                self.PWM.setMotorModel(-2000,-2000,4000,4000)
            elif self.LMR==1:
                self.PWM.setMotorModel(2500,2500,-1500,-1500)
            elif self.LMR==3:
                self.PWM.setMotorModel(4000,4000,-2000,-2000)
            elif self.LMR==7:
                pass
        print "Line Follow End!"
            
    def run_light(self):
        print "Light follow start!"
        self.PWM.setMotorModel(0,0,0,0)
        while self.automode:
            L = self.adc.recvADC(0)
            R = self.adc.recvADC(1)
            if L < 2.99 and R < 2.99 :
                self.PWM.setMotorModel(600,600,600,600)
                
            elif abs(L-R)<0.15:
                self.PWM.setMotorModel(0,0,0,0)
                
            elif L > 3 or R > 3:
                if L > R :
                    self.PWM.setMotorModel(-1200,-1200,1400,1400)
                    
                elif R > L :
                    self.PWM.setMotorModel(1400,1400,-1200,-1200)
        print "Light follow finished!"
            
if __name__ == '__main__':
    devices = map(InputDevice, ('/dev/input/event0','/dev/input/event3'))
    devices = {dev.fd: dev for dev in devices}
    for dev in devices.values(): 
         print(dev)
    buzzer = Buzzer()
    myservo=Servo()
    curarmangle = ARMSTART
    curhandangle = (HANDSTART + HANDEND) / 2
    myservo.setServoPwm('3',curarmangle)
    myservo.setServoPwm('4',curhandangle)
    headlight=LED(HEADLIGHTPIN)
    taillight = TailLight(LEFTREDPIN, LEFTGREENPIN, RIGHTREDPIN, RIGHTGREENPIN)
    display = Display()
    display.show(0,"Ishani's robot")
    
    PWM=Motor(taillight)
    myshow=myapp(PWM, headlight, taillight, buzzer)
    
    sdcount = 0
    try:
        while True:
           r, w, x = select(devices, [], [])
           for fd in r:
              for event in devices[fd].read():
                if event.type == ecodes.EV_KEY:
                    if event.value == 0: # release stop
                        if event.code != 57:
                            if PWM.moving and not(myshow.automode):
			    	PWM.stopMotor() # This will turn on the taillight
                            	display.show(1,"Stop")
                            buzzer.run('0')
                            sdcount = 0
                    elif event.value == 1: # press - start
                        if event.code == UP:
                            PWM.forward()
                            display.show(1,"Going forward")
                        elif event.code == DOWN:
                            PWM.backup()
                            display.show(1,"Backing up")
                        elif event.code == LEFT:
                            PWM.turnLeft()
                            display.show(1,"Turning left")
                        elif event.code == RIGHT:
                            PWM.turnRight()
                            display.show(1,"Turning right")
                        elif event.code == SPACE:
                            myshow.on_pushButton()
                            display.show(1,"Server start/stop")
                        elif event.code == OK:
                            buzzer.run('1') 
                            display.show(1,"Horn!")
                        elif event.code == VUP:
                            display.show(1,"Arm up")
                            if curarmangle >= ARMSTART + 5:
                                curarmangle = curarmangle - 5
                                myservo.setServoPwm('3', curarmangle)
                        elif event.code == VDOWN:
                            display.show(1,"Arm down")
                            if curarmangle <= ARMEND - 5:
                                curarmangle = curarmangle + 5
                                myservo.setServoPwm('3', curarmangle)
                        elif event.code == PLAY:
                            display.show(1,"Claw release")
                            curhandangle = HANDEND
                            myservo.setServoPwm('4',curhandangle)
                        elif event.code == PREV:
                            display.show(1,"Claw close")
                            if curhandangle >= HANDSTART + 5:
                                curhandangle = curhandangle - 5
                                myservo.setServoPwm('4', curhandangle)
                        elif event.code == NEXT:
                            display.show(1,"Claw open")
                            if curhandangle <= HANDEND - 5:
                                curhandangle = curhandangle + 5
                                myservo.setServoPwm('4', curhandangle)
                        elif event.code == CONFIG:
                            display.show(1,"Headlight on/off")
                            headlight.toggle()
                        elif event.code == ESCAPE:
                            display.show(1,"Auto end")
                            myshow.automode = False
                        elif event.code == STARTAUTO:
                            display.show(1,"Starting automode")
                            myshow.run_ultrasonic_thread()
                        elif event.code == STARTLINE:
                            display.show(1,"Starting line follow")
                            myshow.run_line_thread()
                        elif event.code == STARTLIGHT:
                            display.show(1,"Starting light follow")
                            myshow.run_light_thread()
                        else:
                            display.show(1,"Unknown key")
                            print(categorize(event))
                    elif event.value == 2: # Holding - long press processing
                        if event.code == 57: # long press play/pause button
                            sdcount = sdcount + 1
    		if sdcount > 30:
                    display.show(1,"Powering off!")
                    os.system("sudo poweroff")
    except KeyboardInterrupt:
        myshow.close()

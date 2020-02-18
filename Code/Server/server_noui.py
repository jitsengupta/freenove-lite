import io
import os
import socket
import struct
import time
import picamera
import sys,getopt
from threading import Thread
from Thread import *
from server import Server
from evdev import InputDevice, categorize, ecodes
from select import select
from Motor import *
from Buzzer import *
from servo import *

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

ARMSTART = 10
ARMEND = 150
HANDSTART = 10
HANDEND = 90

class myapp():
    
    def __init__(self):
        self.serverup=False
        self.TCP_Server=Server()
        print "Initializing..."
        print "Open TCP"
        self.TCP_Server.StartTcpServer()
        self.ReadData=Thread(target=self.TCP_Server.readdata)
        self.SendVideo=Thread(target=self.TCP_Server.sendvideo)
        self.power=Thread(target=self.TCP_Server.Power)
        self.SendVideo.start()
        self.ReadData.start()
        self.power.start()
        self.serverup = True
                        
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
            
if __name__ == '__main__':
    devices = map(InputDevice, ('/dev/input/event0','/dev/input/event3'))
    devices = {dev.fd: dev for dev in devices}
    for dev in devices.values(): 
         print(dev)
    PWM=Motor()
    buzzer = Buzzer()
    myshow=myapp()
    myservo=Servo()
    curarmangle = ARMSTART
    curhandangle = (HANDSTART + HANDEND) / 2
    myservo.setServoPwm('3',curarmangle)
    myservo.setServoPwm('4',curhandangle)
    sdcount = 0
    try:
        while True:
           r, w, x = select(devices, [], [])
           for fd in r:
              for event in devices[fd].read():
                if event.type == ecodes.EV_KEY:
                    if event.value == 0: # release stop
                        PWM.setMotorModel(0,0,0,0)
                        buzzer.run('0')
                        sdcount = 0
                    elif event.value == 1: # press - start
                        if event.code == UP:
                            PWM.setMotorModel(1000,1000,1000,1000)      
                        elif event.code == DOWN:
                            PWM.setMotorModel(-1000,-1000,-1000,-1000)
                        elif event.code == LEFT:
                            PWM.setMotorModel(-1500,-1500,2000,2000)
                        elif event.code == RIGHT:
                            PWM.setMotorModel(2000,2000,-1500,-1500)
                        elif event.code == SPACE:
                            myshow.on_pushButton()
                        elif event.code == OK:
                            buzzer.run('1')
                        elif event.code == VUP:
                            if curarmangle >= ARMSTART + 5:
                                curarmangle = curarmangle - 5
                                myservo.setServoPwm('3', curarmangle)
                        elif event.code == VDOWN:
                            if curarmangle <= ARMEND - 5:
                                curarmangle = curarmangle + 5
                                myservo.setServoPwm('3', curarmangle)
                        elif event.code == PLAY:
                            curarmangle = ARMSTART
                            curhandangle = (HANDSTART + HANDEND) / 2
                            myservo.setServoPwm('3',curarmangle)
                            myservo.setServoPwm('4',curhandangle)
                        elif event.code == PREV:
                            if curhandangle >= HANDSTART + 5:
                                curhandangle = curhandangle - 5
                                myservo.setServoPwm('4', curhandangle)
                        elif event.code == NEXT:
                            if curhandangle <= HANDEND - 5:
                                curhandangle = curhandangle + 5
                                myservo.setServoPwm('4', curhandangle)
                        elif event.code == CONFIG:
                            print("Headlights?")
                        else:
                            print(categorize(event))
                    elif event.value == 2: # Holding - long press processing
                        if event.code == 57: # long press play/pause button
                            sdcount = sdcount + 1
    			if sdcount > 30:
    			   os.system("sudo poweroff")
    except KeyboardInterrupt:
        myshow.close()

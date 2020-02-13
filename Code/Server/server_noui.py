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
from Motor import *
from Buzzer import *

class myapp():
    
    def __init__(self):
        self.serverup=False
        self.TCP_Server=Server()
        self.parseOpt()
        
    def parseOpt(self):
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
        print "Close TCP" 
        os._exit(0)
    
    def on_pushButton(self):
        if self.serverup==False:
            self.serverup = True
            self.TCP_Server.tcp_Flag = True
            print "Open TCP"
            self.TCP_Server.StartTcpServer()
            self.SendVideo=Thread(target=self.TCP_Server.sendvideo)
            self.ReadData=Thread(target=self.TCP_Server.readdata)
            self.power=Thread(target=self.TCP_Server.Power)
            self.SendVideo.start()
            self.ReadData.start()
            self.power.start()
            
        elif self.serverup==True:
            self.serverup=False
            self.TCP_Server.tcp_Flag = False
            try:
                stop_thread(self.ReadData)
                stop_thread(self.power)
                stop_thread(self.SendVideo)
            except:
                pass
            
            self.TCP_Server.StopTcpServer()
            print "Close TCP" 
            
if __name__ == '__main__':
    dev = InputDevice('/dev/input/event0');
    print(dev);
    PWM=Motor()
    buzzer = Buzzer()
    myshow=myapp()
    sdcount = 0
    try:
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.value == 0: # release stop
                    PWM.setMotorModel(0,0,0,0)
                    buzzer.run('0')
                    sdcount = 0
                elif event.value == 1: # press - start
                    if event.code == 103:
                        PWM.setMotorModel(1000,1000,1000,1000)      
                    elif event.code == 108:
                        PWM.setMotorModel(-1000,-1000,-1000,-1000)
                    elif event.code == 105:
                        PWM.setMotorModel(-1500,-1500,2000,2000)
                    elif event.code == 106:
                        PWM.setMotorModel(2000,2000,-1500,-1500)
                    elif event.code == 57:
                        myshow.on_pushButton()
                    elif event.code == 28:
                        buzzer.run('1')
                    else:
                        print(categorize(event))
                elif event.value == 2: # Holding - long press processing
                    if event.code == 57: # long press play/pause button
                        sdcount = sdcount + 1
			if sdcount > 30:
			   os.system("sudo poweroff")
    except KeyboardInterrupt:
        myshow.close()

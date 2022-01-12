import time
from threading import Thread
from Thread import *
from servo import Servo

CLAWMIN = 50
CLAWMAX = 90
TURNMIN = 30
TURNMAX = 170
REACHMIN = 30
REACHMAX = 150
ARMMIN = 50
ARMMAX = 120

TURNSERVO = '4'
ARMSERVO = '5'
REACHSERVO = '6'
CLAWSERVO = '7'

DEFCLAWPOS = 50
DEFREACHPOS = 90
DEFARMPOS = 85
DEFTURNPOS = 100

defaultangles = {TURNSERVO:DEFTURNPOS, ARMSERVO:DEFARMPOS, REACHSERVO:DEFREACHPOS, CLAWSERVO:DEFCLAWPOS}
currentangles = {TURNSERVO:DEFTURNPOS, ARMSERVO:DEFARMPOS, REACHSERVO:DEFREACHPOS, CLAWSERVO:DEFCLAWPOS}
minangles = {TURNSERVO:TURNMIN, ARMSERVO:ARMMIN, REACHSERVO:REACHMIN, CLAWSERVO:CLAWMIN}
maxangles = {TURNSERVO:TURNMAX, ARMSERVO:ARMMAX, REACHSERVO:REACHMAX, CLAWSERVO:CLAWMAX}

class Robotarm:
    def __init__(self, servo):
        self.servo = servo
        for x in currentangles.keys():
            self.servo.setServoPwm(x, currentangles.get(x))
        self.moving = False
	self.servo_thread = None
        
    def up(self, by=2, delay=0.1):
        self.start_servo_thread(ARMSERVO, by, delay)
        pass
    
    def down(self, by=2, delay=0.1):
        self.start_servo_thread(ARMSERVO, by * -1, delay)
        pass
    
    def left(self, by=2, delay=0.1):
        self.start_servo_thread(TURNSERVO, by * -1, delay)
        pass
    
    def right(self, by=2, delay=0.1):
        self.start_servo_thread(TURNSERVO, by, delay)
        pass
    
    def front(self, by=2, delay=0.1):
        self.start_servo_thread(REACHSERVO, by, delay)
        pass
    
    def back(self, by=2, delay=0.1):
        self.start_servo_thread(REACHSERVO, by * -1, delay)
        pass
    
    def open(self, by=5, delay=0.05):
        self.start_servo_thread(CLAWSERVO, by, delay)        
        pass
    
    def close(self, by=5, delay=0.05):
        self.start_servo_thread(CLAWSERVO, by * -1, delay)
        pass
        
    def stop(self):
        self.stop_servo_thread()
        
    def start_servo_thread(self, channel, inc, delay):
        if self.servo_thread or self.moving:
            self.stop_servo_thread()
        self.moving = True    
        self.servo_thread = Thread(target=self.run_servo_thread, args=(channel, inc, delay))
        self.servo_thread.start()   

    def stop_servo_thread(self):
        self.moving = False
        if self.servo_thread:
            stop_thread(self.servo_thread)
            self.servo_thread = None   
        
    def run_servo_thread(self, channel, inc, delay):
        curpos = currentangles.get(channel)
        minpos = minangles.get(channel)
        maxpos = maxangles.get(channel) 
        while(self.moving and curpos >= minpos and curpos <= maxpos):
		print("Channel:" + channel + " curpos " + str(curpos)) 
                curpos = curpos + inc
                curpos = curpos if curpos <= maxpos else maxpos
                curpos = curpos if curpos >= minpos else minpos
                
                self.servo.setServoPwm(channel, curpos)
                currentangles[channel] = curpos               
                time.sleep(delay)
	self.servo_thread = None
	self.moving = False
                
        
# Main program logic follows:
# For full robot this will open and close the claw 4 times
# Main program logic follows:
# For full robot this will open and close the claw 4 times
if __name__ == '__main__':
    servo = Servo()
    myarm=Robotarm(servo)
    myarm.up()
    time.sleep(4)
    myarm.stop()
    
    myarm.open()
    time.sleep(1)
    myarm.close()

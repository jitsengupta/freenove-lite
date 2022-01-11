import time
from builtins import dict
from servo import Servo
from scipy.weave.examples.vtk_example import inc_dirs
from Carbon.Aliases import false

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

defaultangles = dict(TURNSERVO=DEFTURNPOS, ARMSERVO=DEFARMPOS, REACHSERVO=DEFREACHPOS, CLAWSERVO=DEFCLAWPOS)
currentangles = defaultangles
minangles = dict(TURNSERVO=TURNMIN, ARMSERVO=ARMMIN, REACHSERVO=REACHMIN, CLAWSERVO=CLAWMIN)
maxangles = dict(TURNSERVO=TURNMAX, ARMSERVO=ARMMAX, REACHSERVO=REACHMAX, CLAWSERVO=CLAWMAX)

class Robotarm:
    def __init__(self, servo):
        self.servo = servo
        for x in currentangles.keys():
            self.servo.setServoPwm(x, currentangles.get(x))
        self.moving = false
        
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
            
        self.servo_thread = Thread(target=self.run_servo_thread, args=(channel, inc, delay))
        self.scroll_thread.start()   

    def stop_servo_thread(self):
        self.moving = false
        if self.servo_thread:
            stop_thread(self.servo_thread)
            self.servo_thread = None   
        
    def run_servo_thread(self, channel, inc, delay):
        curpos = currentangles[channel]
        minpos = minangles[channel]
        maxpos = maxangles[channel] 
        while(self.moving and curpos >= minpos and curpos <= maxpos):
                curpos = curpos + inc
                self.servo.setServoPwm(channel, curpos)
                currentangles[channel] = curpos               
                time.sleep(delay)
                
        
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

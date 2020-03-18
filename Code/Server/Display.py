from Phidget22.Phidget import *
from Phidget22.Devices.LCD import *
from pymaybe import maybe
import time


class Display:
    
    def __init__(self):
        self.lcd0 = LCD()
        self.attached = False
        
        self.lcd0.setOnAttachHandler(self.onAttach)
        self.lcd0.setOnDetachHandler(self.onDetach)
    
        lcd0.openWaitForAttachment(2000)
        
    def onAttach(self):
        self.attached = True
    
    def onDetach(self):
       self.attached = False

    def clear(self):
        self.lcd0.clear()
        
    def show(self, lineno, text):    
        self.lcd0.writeText(LCDFont.FONT_5x8, lineno, 0, text)
        self.lcd0.flush()

    def close(self):    
        self.lcd0.close()

               
if __name__ == '__main__':
    d = Display()
    
    d.show(0, "My name is Ishani")
    d.show(1, "I love you")
    
    time.sleep(5)
    d.clear()
    
    d.close()

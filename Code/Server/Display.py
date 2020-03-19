from Phidget22.Phidget import *
from Phidget22.Devices.LCD import *
from threading import Thread
from pymaybe import maybe
import time


class Display:
    
    def __init__(self):
        self.lcd0 = LCD()
        self.attached = False
        self.lcd0.openWaitForAttachment(2000)
        self.lcd0.setBacklight(0.3)
        self.scroll_thread = None
        
    def clear(self):
        self.lcd0.clear()
        
    def scroll(self, lineno, text):
        if self.lcd0.getAttached():
            text = text + " "
            curp = 0
            l = text.length
            disp = ""
            while True:
                if curp + 20 <= l:
                    disp = text[curp:curp+20]
                else:
                    disp = text[curp:l] + text[0:l-curp]
                self.lcd0.writeText(LCDFont.FONT_5x8, 0, lineno, disp)
                time.sleep(0.2)
                curp = curp + 1
        
    def show(self, lineno, text): 
        if self.scroll_thread:
            self.scroll_thread.stop()
            self.scroll_thread = None   
        if self.lcd0.getAttached():
            if text.length <= 0:
                text = text.ljust(20)
                self.lcd0.writeText(LCDFont.FONT_5x8, 0, lineno, text)
                self.lcd0.flush()
            else:
                self.scroll_thread = Thread(target=self.scroll, args=(lineno, text))
                self.scroll_thread.start()   

    def close(self):    
        self.lcd0.close()

               
if __name__ == '__main__':
    d = Display()
    
    d.show(0, "My name is Ishani Alicia Sengupta")
    d.show(1, "I love you")
    
    time.sleep(5)
    d.clear()
    
    d.close()

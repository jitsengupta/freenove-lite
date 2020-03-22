from Phidget22.Phidget import *
from Phidget22.Devices.LCD import *
from threading import Thread
from Thread import *
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
            l = len(text)
            disp = ""
            while True:
                if curp + 20 <= l:
                    disp = text[curp:curp+20]
                else:
                    disp = text[curp:l] + text[0:20-l+curp]
		try:
                    self.lcd0.writeText(LCDFont.FONT_5x8, 0, lineno, disp)
		    self.lcd0.flush()
		except:
		    err = sys.exc_info()
    		    print "Unexpected error:", err[0]
		    if len(err) > 1:
			print err[1]
                time.sleep(0.2)
                curp = (curp + 1)%l
        
    def show(self, lineno, text, scroll=False): 
        if self.scroll_thread:
            stop_thread(self.scroll_thread)
            self.scroll_thread = None   
	if not(scroll) and len(text) > 0:
		text = text[0:20]
        if self.lcd0.getAttached():
            if len(text) <= 20:
                text = text.ljust(20)
                try:
		    self.lcd0.writeText(LCDFont.FONT_5x8, 0, lineno, text)
                    self.lcd0.flush()
		except:
		    err = sys.exc_info()
    		    print "Unexpected error:", err[0]
		    if len(err) > 1:
			print err[1]
            else:
                self.scroll_thread = Thread(target=self.scroll, args=(lineno, text))
                self.scroll_thread.start()   

    def close(self):    
	if self.scroll_thread:
		stop_thread(self.scroll_thread)

        self.lcd0.close()

               
if __name__ == '__main__':
    d = Display()
    
    d.show(0, "My name is Ishani Alicia Sengupta")
    time.sleep(5)
    d.show(1, "Hello world")
    time.sleep(2)
    d.clear()
    
    d.close()

from threading import Thread
from Thread import *
from pymaybe import maybe
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment

import time

class SevenSegDisplay:
    
    def __init__(self):
        # create seven segment device
        self.serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(self.serial, cascaded=1)
        self.seg = sevensegment(self.device)
        self.scroll_thread = None        
        
    def clear(self):
        self.seg.text = ""
        
    def show_message_vp(self, msg, delay=0.1):
        # Implemented with virtual viewport
        width = self.device.width
        padding = " " * width
        msg = padding + msg + padding
        n = len(msg)
    
        virtual = viewport(self.device, width=n, height=8)
        sevensegment(virtual).text = msg
        for i in reversed(list(range(n - width))):
            virtual.set_position((i, 0))
            time.sleep(delay)
    
    def show_message_alt(self, msg, delay=0.1):
        # Does same as above but does string slicing itself
        width = self.device.width
        padding = " " * width
        msg = padding + msg + padding
    
        for i in range(len(msg)):
            self.seg.text = msg[i:i + width]
            time.sleep(delay)
            
    def scroll(self, text, speed):
	while(True):
            self.show_message_alt(text, speed)

    def show(self, lineno, text, scroll=True):
        if self.scroll_thread:
            stop_thread(self.scroll_thread)
            self.scroll_thread = None   

    	if not(scroll) and len(text) > 0:
            text = text[0:self.device.width]
            self.seg.text = text
        else:
            if (len(text)) <= self.device.width:
                self.seg.text = text
            else:
                self.scroll_thread = Thread(target=self.scroll, args=(text,0.1))
                self.scroll_thread.start()   

    def close(self):    
        if self.scroll_thread:
            stop_thread(self.scroll_thread)

               
if __name__ == '__main__':
    d = SevenSegDisplay()
    
    d.show(0, "My name is Ishani Alicia Sengupta", True)
    time.sleep(30)
    d.show(1, "HELLO!", True)
    time.sleep(20)
    d.clear()
    
    d.close()

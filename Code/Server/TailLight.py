import time
from pymaybe import maybe
from gpiozero import LED


class TailLight:
    
    def __init__(self, leftredpin, leftgreenpin, rightredpin, rightgreenpin):
        self.red = LED(leftredpin)
        self.green = LED(leftgreenpin)
        self.rightgreen = LED(rightgreenpin) if rightgreenpin != leftgreenpin else None
        self.rightred = LED(rightredpin) if rightredpin != leftredpin else None
        self.saveValues()
        
    def bothred(self):
	#traceback.print_stack(file=sys.stdout)
        self.green.off()
        maybe(self.rightgreen).off()
        self.red.on()
        maybe(self.rightred).on()    
    
    def bothgreen(self):
        self.red.off()
        maybe(self.rightred).off()
        self.green.on()
        maybe(self.rightgreen).on()    
    
    def saveValues(self):
        self.lgv = self.green.value
        self.rgv = maybe(self.rightgreen).value
        self.lrv = self.red.value
        self.rrv = maybe(self.rightred).value

    def loadValues(self):
        self.green.value = self.lgv 
        if self.rightgreen is not None:
            self.rightgreen.value = self.rgv
        self.red.value = self.lrv
        if self.rightred is not None:
            self.rightred.value = self.rrv 
                
    def rightblink3(self):
        # Let's save the current stage to local values
        # Then blink the left red and leave the right red on
        # Maybe just blink 3 times then put things back how
        # they were?
        self.saveValues()
        self.bothred()
        maybe(self.rightred).blink(0.5, 0.5, 3, False)
        self.loadValues()

    def leftblink3(self):
        self.saveValues()
        self.bothred()
        self.red.blink(0.5, 0.5, 3, False)
        self.loadValues()
    
    def leftblink(self):
        self.bothred()
        self.red.blink(0.25, 0.25)
    
    def rightblink(self):
        self.bothred()
        maybe(self.rightred).blink(0.25, 0.25)

    def flash(self):
        self.bothred()
        self.red.blink(0.25, 0.25)
        maybe(self.rightred).blink(0.25, 0.25)
    
    def off(self):
        self.green.off()
        self.red.off()
        maybe(self.rightgreen).off()
        maybe(self.rightred).off()

            
if __name__ == '__main__':
    tl = TailLight(26, 21, 20, 21)
    print("Red on")
    tl.bothred()
    time.sleep(3)
    print("Off")
    tl.off()
    time.sleep(2)
    print("Green on")
    tl.bothgreen()
    time.sleep(3)
    print("Left blink")
    tl.leftblink()
    time.sleep(3)
    print("Right blink")
    tl.rightblink()
    time.sleep(3)

    print("Flash")
    tl.flash()
    time.sleep(4)

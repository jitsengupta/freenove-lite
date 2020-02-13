from evdev import InputDevice, categorize, ecodes
from Motor import *
from Buzzer import *
dev = InputDevice('/dev/input/event0');
print(dev);
PWM=Motor()
buzzer = Buzzer()
for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
	if event.value == 0:
            PWM.setMotorModel(0,0,0,0)
	    buzzer.run('0')
        elif event.value == 1:
            if event.code == 103:
                PWM.setMotorModel(1000,1000,1000,1000)      
            elif event.code == 108:
                PWM.setMotorModel(-1000,-1000,-1000,-1000)
            elif event.code == 105:
                PWM.setMotorModel(-1500,-1500,2000,2000)
            elif event.code == 106:
                PWM.setMotorModel(2000,2000,-1500,-1500)
	    elif event.code == 28:
		buzzer.run('1')
                

from evdev import InputDevice, categorize, ecodes
from select import select

devices = map(InputDevice, ('/dev/input/event0','/dev/input/event3'))
devices = {dev.fd: dev for dev in devices}
for dev in devices.values(): 
     print(dev)
while True:
   r, w, x = select(devices, [], [])
   for fd in r:
      for event in devices[fd].read():
         if event.type == ecodes.EV_KEY:
             print(categorize(event)) 

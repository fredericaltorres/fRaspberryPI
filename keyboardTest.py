import sys

Off          = False
On           = True
lightOn      = Off # always start by turnin on the light

def HandleMotionDetected():
    if lightOn == Off: # Turn light on if no activity and light are on
    	print("Lights are off")

print("Start")
HandleMotionDetected()
while True:
    print("Wait")
    char = sys.stdin.read(1)
    print 'You pressed %s' % char
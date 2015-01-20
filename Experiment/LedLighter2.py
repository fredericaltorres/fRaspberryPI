import RPi.GPIO as GPIO
import time

class Board(object):

	def Trace(self, m):
		print(m)

	def __init__(self):
		self.Trace("Init board")
		GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
		
	def SetPinOut(self, pin):
		self.Trace("Set pin:%d" % (pin))
		GPIO.setup(pin, GPIO.OUT) # Setup GPIO Pin x to OUT

	def Done(self):
		self.Trace("Done board")
		GPIO.cleanup()

	def SendCurrent(self, pin, onOff):
		self.Trace("SendCurrent(%d) = %s" % (pin, onOff))
		GPIO.output(pin, onOff)

	def Wait(self, seconds):
		self.Trace("Wait:%f" % (seconds))
		time.sleep(seconds)

def DemoPin7Only():
    pin = 7
    board = Board()
    board.SetPinOut(pin)

    for i in range(1, 32):
            board.Trace("Loop:%d" % (i))
            board.SendCurrent(pin, True)
            board.Wait(i/100.0)
            board.SendCurrent(pin, False)
            board.Wait(i/100.0)

    board.Done()

def DemoMultiplePins():
    pins = [7, 11, 13]
    board = Board()
    for pin in pins:
        board.SetPinOut(pin)
        
    for i in range(1, 32):
        board.Trace("Loop:%d" % (i))
        for pin in pins:
            board.SendCurrent(pin, True)
        board.Wait(i/100.0)
        for pin in pins:
            board.SendCurrent(pin, False)
        board.Wait(i/100.0)

    board.Done()


# Init global board 
board = Board()

# ---------------------------------------------
# Turn on/off all pins and wait after each pin
# if requested
def AllPins(pins, state, wait = 0):
    for pin in pins:
        board.SendCurrent(pin, state)
        board.Wait(wait)

# ---------------------------------------------
# 
def DemoChristmasTree():
    pins  = [7, 11, 13]
    pinRs = list(pins)
    pinRs.reverse()
    wait  = 0.5
  
    for pin in pins:
        board.SetPinOut(pin)
        
    for i in range(1, 20):
        board.Trace("Loop:%d" % (i))
        AllPins(pins, True)
        board.Wait(wait)
        if(i % 2 == 0):
            AllPins(pins, False, wait/2)
        else:
            AllPins(pinRs, False, wait/2)

    AllPins(pins, False)
    board.Done()

DemoChristmasTree()

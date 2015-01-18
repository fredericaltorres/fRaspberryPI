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

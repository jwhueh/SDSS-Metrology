#! /usr/bin/python
"""edited for SDSS metrology"""
import serial
import time
import re

"""Make it so that the temp sensors are read from file but at the same time the file can be updated with routine"""

class Metrology(object):
	def __init__(self):
		pass
		self.ser = None
		self.serial = '/dev/ttyUSB0'
		#self.serial = '/dev/ttymxc4'
		self.sensors=[] 
		self.delay = 0.2
		self.connect()
		self.findTempSensors()
		#self.readTempConfig()
		#self.setupSensors()
		#self.run()
		self.powerDown()

	def run(self):
		while True:
			fout = open(time.strftime("%Y%m%d.temp"),'a')
			output=time.strftime("%Y%m%dT%H%M%SZ")
			for s in self.sensors:
				output = output+','	
				temp = self.readTemp(s)
				output = output+str(temp)
			fout.write(output+'\n')
			print output
			fout.close()
			
			time.sleep(30)	


	def setupSensors(self):
		for s in self.sensors:
			self.setResolution(s)
			self.readTemp(s)
		return

	def powerDown(self):
		self.serWrite('P')
		return
			

	def findTempSensors(self):
		"""
		This routine just polls the connected sensors and prints out 
		their addresses.
		"""
		print self.serWrite('S')
		time.sleep(1)
		while True:
			out = self.serWrite('s')
			time.sleep(self.delay)
			if len(out) <=3:
                                break
			print out
		return

	def readTempConfig(self):
		fin = open('sensors.conf','r')
		for line in fin:
			if not re.search('#', line):
				self.sensors.append(line.rstrip('\n'))
		print self.sensors
		return


	def setResolution(self,dev):
		self.deviceSelect(dev)
		self.serWrite('W044E4B467F')
		self.serWrite('R')

	def connect(self):
		self.ser = serial.Serial(self.serial,9600,bytesize=8, timeout=.5, stopbits = 1)
		return

	def readTemp(self, dev):
		self.deviceSelect(dev)
		self.serWrite('M')
		self.serWrite('W0144')
		self.serWrite('M')
		time.sleep(1)
		output = self.serWrite('W0ABEFFFFFFFFFFFFFFFFFF')
		t = self.convert(output)
		print 'Convert', output, t
		return t

	def deviceSelect(self, dev):
		self.serWrite('A%s' % str(dev))
		return

	def serWrite(self, text1 = None, text2 = None):
		if text2 == None:
			cmd = '%s\r' % text1
		self.ser.write(cmd)
		time.sleep(1) #this delay is necessary
		out = self.ser.readline()
		x = 0
		"""while x<5:
			out = self.ser.readline()
			print 'HA7E: ', repr(out)
			x = x+1"""
		print 'HA7E: ', repr(out)
		return out.rstrip('\r')

	def convert(self, sig):
		lsb = sig[2:4]
		msb = sig[4:6]
		lm = msb+lsb
		temp = int('0x%s' % lm,0)/16.
		return temp

if __name__ == "__main__":
	m = Metrology()
	#m.readTemp('0FFCDBE0000F2FBA')
	#m.run()

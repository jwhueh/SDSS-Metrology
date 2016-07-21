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
		self.sensors=[] 
		self.delay = 0.1
		self.connect()
		self.findTempSensors()
		self.readTempConfig()
		self.setupSensors()
		self.run()
		#self.powerDown()

	def run(self):
		while True:
			fout = open(time.strftime("%Y%m%d.temp"),'a')
			output=time.strftime("%Y%m%dT%H%M%SZ")
			for s in self.sensors:
				output = output+','	
				start = time.time()
				temp = self.readTemp(s)
				print "temp timing", time.time() - start
				output = output+str(temp)
			fout.write(output+'\n')
			print output
			fout.close()


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
		time.sleep(.2)
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
		#self.serWrite('W044E4B467F') #12 bit resolution -- 0.0625 increments
		self.serWrite('W044E4B465F') #11 bit resolution -- 0.125 increments
		#self.serWrite('W044E4B463F') #10 bit resolution -- 0.25 increments
		self.serWrite('R')

	def connect(self):
		self.ser = serial.Serial(self.serial,9600,bytesize=8, timeout=.5, stopbits = 1)
		return

	def readTemp(self, dev):
		self.deviceSelect(dev)
		#self.serWrite('M')
		self.serWrite('W0144')
		time.sleep(self.delay)
		self.serWrite('M')
		output = self.serWrite('W0ABEFFFFFFFFFFFFFFFFFF')
		t = self.convert(output)
		#print 'Convert', output, t  #Use to print hex value and numerical value of temperature
		print time.strftime("%Y%m%dT%H%M%S"),str(dev), str(t)  #Use to print only numerical value of temperature
		return t

	def deviceSelect(self, dev):
		self.serWrite('A%s' % str(dev))
		return

	def serWrite(self, text1 = None, text2 = None):
		if text2 == None:
			cmd = '%s\r' % text1
		self.ser.write(cmd)
		out = self.ser.readline()
		return out.rstrip('\r')

	def convert(self, sig):
		lsb = sig[2:4]
		msb = sig[4:6]
		lm = msb+lsb
		#temp = int('0x%s' % lm,0)/16.
		neg = sig[4:5]
                count_remain = sig[14:16]
                count_c = sig[16:18]
                #print lsb, msb, neg, count_remain, count_c
                #make into binary
                binary = bin(int(lm, 16))[2:].zfill(16)

                if neg == 'F':
                        print binary
                        outbin = ""
                        for b in binary:
                                if b == '1':
                                        outbin = outbin + '0'
                                else:
                                        outbin = outbin + '1'

                        outhex = (int(outbin, 2))
                        #print outhex
                        temp = -int('%s' % outhex,0)/16.
                        return temp


                else:
                        #print lm
                        temp = int('0x%s' % str(lm),0)/16.
                        return temp
                return


if __name__ == "__main__":
	m = Metrology()
	#m.readTemp('0FFCDBE0000F2FBA')
	#m.run()

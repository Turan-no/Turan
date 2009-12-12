import xml.sax.handler

"""Class for parsing xml-files from polarpersonaltrainer.com, strips out planned trips, and only parses <results>
"""

class TripHandler(xml.sax.handler.ContentHandler):
	def __init__(self):
		self.inTime = 0
		self.inDistance = 0
		self.inName = 0
		self.inCalories = 0
		self.inDuration = 0
		self.inLap = 0
		self.inUserSettings = 0
		self.inHeartrate = 0
		self.inHeartrateAverage = 0
		self.inHeartrateMax = 0
		self.inSpeed = 0
		self.inCyclingspeed = 0
		self.inCyclingspeedAvg = 0
		self.inCyclingspeedMax = 0
		self.inCadence = 0
		self.inCadenceAvg = 0
		self.inCadenceMax = 0
		self.realExercise = 0
		self.namePresent = 0
		self.mapper = {}

	def startElement(self, name, attributes):
		if name == "exercise":
			self.namebuffer = ""
			self.distancebuffer = ""
			self.timebuffer = ""
			self.caloriesbuffer = ""
			self.durationbuffer = ""
			self.heartratebuffer = ""
			self.heartratemaxbuffer = ""
			self.speedavgbuffer = ""
			self.speedmaxbuffer = ""
			self.cadenceavgbuffer = ""
			self.cadencemaxbuffer = ""
		if name == "time":
			self.inTime = 1
		if name == "name":
			self.inName = 1
			self.namePresent = 0
		if name == "result":
			self.realExercise = 1
		if name == "heart-rate":
			self.inHeartrate = 1
		if name == "user-settings":
			self.inUserSettings = 1
		if not self.inUserSettings and self.inHeartrate and name == "average":
			self.inHeartrateAverage = 1
		if not self.inUserSettings and self.inHeartrate and name == "maximum":
			self.inHeartrateMax= 1
		if name == "calories":
			self.inCalories = 1
		if name == "duration":
			self.inDuration = 1
		if name == "lap":
			self.inLap = 1
		if name == "speed" and self.inSpeed:
			self.inCyclingspeed = 1
		if name == "average" and self.inCyclingspeed:
			self.inCyclingspeedAvg = 1
		if name == "maximum" and self.inCyclingspeed:
			self.inCyclingspeedMax = 1
		if name == "average" and self.inCadence:
			self.inCadenceAvg = 1
		if name == "maximum" and self.inCadence:
			self.inCadenceMax = 1
		if name == "speed" and not self.inCyclingspeed and not self.inLap:
			self.inSpeed = 1
		if self.inSpeed and name == "cadence":
			self.inCadence = 1
		if self.realExercise and name == "distance":
			self.inDistance = 1
	
	def characters(self, data):
		if self.inName:
			self.namebuffer += data
		if not self.inLap and self.inDistance:
			self.distancebuffer += data
		if not self.inLap and self.inDuration:
			self.durationbuffer += data
		if self.inHeartrate and self.inHeartrateAverage and not self.inLap:
			self.heartratebuffer += data
		if self.inHeartrateMax and self.inHeartrate and not self.inLap:
			self.heartratemaxbuffer += data
		if self.inTime:
			self.timebuffer += data
		if self.inCalories:
			self.caloriesbuffer += data
		if self.inCyclingspeedAvg:
			self.speedavgbuffer += data
		if self.inCyclingspeedMax:
			self.speedmaxbuffer += data
		if self.inCadenceAvg:
			self.cadenceavgbuffer += data
		if self.inCadenceMax:
			self.cadencemaxbuffer += data

	def endElement(self, name):
		if name == "name":
			self.inName = 0
		if name == "distance":
			self.inDistance = 0
		if name == "time":
			self.inTime = 0
		if name == "duration":
			self.inDuration = 0
		if name == "lap":
			self.inLap = 0
		if name == "calories":
			self.inCalories = 0
		if not self.inUserSettings and self.inHeartrate and name == "average":
			self.inHeartrateAverage = 0
		if not self.inUserSettings and self.inHeartrate and name == "maximum":
			self.inHeartrateMax= 0
		if name == "heart-rate":
			self.inHeartrate = 0
		if name == "user-settings":
			self.inUserSettings = 0
		if name == "speed" and not self.inCyclingspeed:
			self.inSpeed = 0
		if name == "speed" and self.inSpeed:
			self.inCyclingspeed = 0
		if name == "average" and self.inCyclingspeed:
			self.inCyclingspeedAvg = 0
		if name == "maximum" and self.inCyclingspeed:
			self.inCyclingspeedMax = 0
		if name == "average" and self.inCadence:
			self.inCadenceAvg = 0
		if name == "maximum" and self.inCadence:
			self.inCadenceMax = 0
		if name == "cadence" and self.inSpeed:
			self.inCadence = 0
		if name == "result":
			if not self.inName and not self.inDistance and not self.inTime and self.realExercise:
				self.mapper[self.timebuffer[0:10]] = { }
				if len(self.namebuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["name"] = self.namebuffer
				else:
					self.mapper[self.timebuffer[0:10]]["name"] = "NoName"
				self.mapper[self.timebuffer[0:10]]["timeofday"] = self.timebuffer[11:]
				if len(self.caloriesbuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["calories"] = float(self.caloriesbuffer)
				if len(self.distancebuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["distance"] = float(self.distancebuffer)
				if len(self.durationbuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["duration"] = self.durationbuffer
				if len(self.heartratebuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["hrAvg"] = float(self.heartratebuffer)
				if len(self.heartratemaxbuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["hrMax"] = float(self.heartratemaxbuffer)
				if len(self.speedavgbuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["avgSpeed"] = float(self.speedavgbuffer)
				if len(self.speedmaxbuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["maxSpeed"] = float(self.speedmaxbuffer)
				if len(self.cadenceavgbuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["avgCadence"] = float(self.cadenceavgbuffer)
				if len(self.cadencemaxbuffer) > 0:
					self.mapper[self.timebuffer[0:10]]["maxCadence"] = float(self.cadencemaxbuffer)
			self.realExercise = 0
		
		


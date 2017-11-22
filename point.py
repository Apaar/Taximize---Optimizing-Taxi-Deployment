class Point:
	def __init__(self, latit_, longit_):
		#self.id = id_   #an id which uniquely identifies a point
		self.latit = latit_
		self.longit = longit_
		self.nreviews = None
		self.cpop = None
	def set_nreviews(self, nreviews):
		self.nreviews = nreviews

	def set_cpop(self, cpop):
		self.cpop = cpop
	def __str__(self):
		return "(" + str(self.nreviews) + ',' + str(self.cpop) + ', ' + str(self.latit) + ", " + str(self.longit) + ")"
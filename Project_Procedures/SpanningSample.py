from Core import Procedure
import Project_Procedures.InitialImages
import Project_Procedures.FinalImages
from Procedures import Toolpath_Generate
from Procedures import Toolpath_Print
from copy import deepcopy

class SpanningSample(Procedure):
	def Prepare(self):
		self.name = 'SpanningSample'
		self.requirements['trayaddress'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the sample tray'}
		self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'material printed for sample'}
		self.requirements['yGap'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'y gap for span'}
		self.requirements['zGap'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'z gap for span'}
		self.iImages = Project_Procedures.InitialImages(self.apparatus, self.executor)
		self.fImages = Project_Procedures.FinalImages(self.apparatus, self.executor)
		self.TPgen = Toolpath_Generate(self.apparatus, self.executor)
		self.TPprint = Toolpath_Print(self.apparatus, self.executor)
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters', 'material'])
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters', 'yGap'])
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters', 'zGap'])
		self.apparatus.createAppEntry(['information', 'trays', 'original_alignments'])
		
	def Plan(self):
		# Renaming information from requirements
		material = self.requirements['material']['value']
		yGap = self.requirements['yGap']['value']
		zGap = self.requirements['zGap']['value']
		trayaddress = self.requirements['trayaddress']['value']
		# Get relevant devices
		nozzlename = self.apparatus.findDevice({'descriptors':[material, 'nozzle']})

		samplename = self.apparatus.getValue(['information','ProcedureData','SpanningSample','cur_parameters', 'samplename'])
		self.apparatus.setValue(['information', 'ProcedureData', 'SpanningSample', 'cur_parameters', 'yGap'], yGap)
		self.apparatus.setValue(['information', 'ProcedureData', 'SpanningSample', 'cur_parameters', 'zGap'], zGap)
		self.apparatus.setValue(['information', 'ProcedureData', 'SpanningSample', 'cur_parameters', 'material'], material)
		temp_tray = self.apparatus.getValue(trayaddress)
		tray = deepcopy(temp_tray)
		
		# Find the appropriate entry in sample tray and feed the toolpath
		# generator the right values
		foundTarget = False
		for place in tray:
			if not foundTarget:
				place_yGap = place['fpoint']['Y'] - place['bpoint']['Y']
				place_zGap = place['fpoint']['Z'] - place['bpoint']['Z']
				if not place['used']:
					tp_fpoint = {'Y':place['fpoint']['Y'], 'Z':place['fpoint']['Z']}
					tp_bpoint = {'Y':place['bpoint']['Y'], 'Z':place['bpoint']['Z']}
					if place_yGap == yGap and place_zGap == zGap:
						foundTarget = True
						self.apparatus.setValue(['information', 'toolpaths', 'parameters', 'point1'], tp_fpoint)
						self.apparatus.setValue(['information', 'toolpaths', 'parameters', 'point2'], tp_bpoint)
						newstart = place['fpoint']
						place['used'] = True
					elif place_yGap == -yGap and place_zGap == -zGap:
						foundTarget = True
						self.apparatus.setValue(['information', 'toolpaths', 'parameters', 'point1'], tp_bpoint)
						self.apparatus.setValue(['information', 'toolpaths', 'parameters', 'point2'], tp_fpoint)
						newstart = place['bpoint']
						place['used'] = True
		self.apparatus.setValue(self.requirements['trayaddress']['value'], tray)
		# Store original alignments
		alignments = self.apparatus.getValue(['information', 'alignments'])
		for alignment in alignments:
			if '@start' in alignment:
				calignment = deepcopy(alignments[alignment])
				self.apparatus.createAppEntry(['information', 'trays', 'original_alignments', alignment])
				self.apparatus.setValue(['information', 'trays', 'original_alignments', alignment], calignment)
		# Update the X for each alignment that needs to be updated
		oalignments = self.apparatus.getValue(['information', 'trays', 'original_alignments'])
		for alignment in alignments:
			# Only change alignments that are toolname@start
			# This keeps the XY shifting between samples from impacting the calibrations/cleaning procedures
			if '@start' in alignment:
				alignments[alignment]['X'] = oalignments[alignment]['X'] + newstart['X']
		self.iImages.Do({'samplename': samplename, 'zOffset': 0.5, 'nozzlename': nozzlename})
		self.TPgen.Do()
		self.TPprint.requirements['toolpath']['address'] = ['information', 'toolpaths', 'toolpath']
		self.TPprint.Do()
		self.fImages.Do({'samplename': samplename, 'nozzlename': nozzlename})
		# Return Alignments to original state
		for alignment in alignments:
			if '@start' in alignment:
				oalignment = deepcopy(oalignments[alignment])
				self.apparatus.setValue(['information','alignments',alignment], oalignment)
		
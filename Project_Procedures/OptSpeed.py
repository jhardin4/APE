from Core import Procedure
import Project_Procedures.InitialImages
import Project_Procedures.FinalImages
from Procedures import Toolpath_Generate
from Procedures import Toolpath_Print

class OptSpeed(Procedure):
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
		
		self.ImgPred = Project_Procedures.ImPredict(self.appartus, self.executor)
		self.ParamAdjust = Project_Procedures.Suggest(self.appartus, self.executor)
		
		
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
		tray = self.apparatus.getValue(trayaddress)
		
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
						place['used'] = True
					elif place_yGap == -yGap and place_zGap == -zGap:
						foundTarget = True
						self.apparatus.setValue(['information', 'toolpaths', 'parameters', 'point1'], tp_bpoint)
						self.apparatus.setValue(['information', 'toolpaths', 'parameters', 'point2'], tp_fpoint)
						place['used'] = True
		self.apparatus.setValue(self.requirements['trayaddress']['value'], tray)
		
		self.iImages.Do({'samplename': samplename, 'zOffset': 0.5, 'nozzlename': nozzlename})
		self.TPgen.Do()
		self.TPprint.requirements['toolpath']['address'] = ['information', 'toolpaths', 'toolpath']
		self.TPprint.Do()
		self.fImages.Do({'samplename': samplename, 'nozzlename': nozzlename})
		
		
		self.ImgPred.Do()
		self.ParamAdjust.Do()
		
import Core
import Procedures
import time


class FinalImages(Core.Procedure):
	def Prepare(self):
		self.name = 'FinalImage'
		self.requirements['samplename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of this sample for logging purposes'}
		self.requirements['nozzlename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the nozzle'}
		self.requirements['zOffset'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'z offset of nozzle during alignment pictures'}
		self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
		self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
		self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
		self.image = Procedures.Camera_Capture_Image(self.apparatus, self. executor)
		self.getPos = Procedures.Aerotech_A3200_getPosition(self.apparatus, self. executor)
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters', 'FinalFile'])
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters', 'FinalPosition'])
		
	def Plan(self):
		# Renaming information from requirements
		samplename = self.requirements['samplename']['value']
		nozzlename = self.requirements['nozzlename']['value']
		offset = self.requirements['zOffset']['value']

		# Gathering required information
		cameraname = self.apparatus.findDevice({'descriptors': ['camera']})
		motionname = self.apparatus.findDevice({'descriptors': 'motion'})
		noz_axismask = self.apparatus.getValue(['devices', motionname, nozzlename, 'axismask'])
		cam_axismask = self.apparatus.getValue(['devices', motionname, cameraname, 'axismask'])
		noz_refpoint = self.apparatus.getValue(['information', 'alignments', nozzlename+'@start'])
		cam_refpoint = self.apparatus.getValue(['information', 'alignments', cameraname+'@start'])
		axislist = ['X', 'Y', noz_axismask['Z'], cam_axismask['Z']]
		
		# Assign addresses to procedures
		self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
		self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']

		# Get image for acessing alignment at center of pillars
		# Get the values relvant to the sample from the toolpath parameters
		leadin = self.apparatus.getValue(['information', 'toolpaths', 'parameters', 'leadin'])
		point1 = self.apparatus.getValue(['information', 'toolpaths', 'parameters', 'point1'])
		point2 = self.apparatus.getValue(['information', 'toolpaths', 'parameters', 'point2'])
		
		# Set the motion behavior
		self.motionset.Do({'Type': 'default'})
		
		#Get image at center of range
		relpoint = {}
		for dim in point1:
			relpoint[dim] = (point1[dim] + point2[dim])/2
		priority = [['Z']]
		self.move.Do({'refpoint': cam_refpoint, 'relpoint': relpoint, 'priority': priority, 'axismask':cam_axismask})
		self.DoEproc(motionname, 'Run', {})
		filename = 'Data\\' + str(round(time.time())) + samplename + '_final' + '.tif'
		self.image.Do({'file': filename, 'camera_name': cameraname, 'settle_time': 1})
		self.apparatus.setValue(['information','ProcedureData','SpanningSample','cur_parameters', 'FinalFile'], filename)
		temp = [0]
		self.getPos.Do({'axisList':axislist, 'target':temp})
		self.apparatus.setValue(['information','ProcedureData','SpanningSample','cur_parameters', 'FinalPosition'], temp[0])

		refpoint = self.apparatus.getValue(['information', 'alignments', 'safe'+cam_axismask['Z']])
		self.move.Do({'refpoint': refpoint, 'axismask':cam_axismask})
		self.DoEproc(motionname, 'Run', {})
 
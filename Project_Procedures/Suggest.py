import Core
import Procedures
from Project_Procedures import SpanningSample
from Project_Procedures import ImPredict

class Suggest(Core.Procedure):
	# prepare collects the needed things as well as defines the structure of the data (createAppEntry)
	def Prepare(self):
		self.name = "Suggest"
		self.requirements['prevSample'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'information about previous sample'}
		self.requirements['prevSample']['address'] = ['information','ProcedureData','SpanningSample','cur_parameters']
		self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'material printed for sample'}
		self.requirements['yGap'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'y gap for span'}
		self.requirements['zGap'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'z gap for span'}
		# provide necessary structure
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters'])
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters','speed'])
		self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters','Class'])
		self.newsample = SpanningSample(self.apparatus, self.executor)
		self.classify = ImPredict(self.apparatus, self.executor)
		self.recordData = Procedures.Data_JSON_Store(self.apparatus, self.executor)

	def Plan(self):
		prevSample = self.requirements['prevSample']['value']
		material = self.requirements['material']['value']
		zGap = self.requirements['zGap']['value']
		yGap = self.requirements['yGap']['value']
		prevSpeed = prevSample['speed']
		prvClass = prevSample['Class']
		# grab motionname, and nozzle speed... then use to find the speed of the nozzle defined by these two
		motionname = self.apparatus.findDevice({'descriptors': 'motion'})
		nozzlename = self.apparatus.findDevice({'descriptors': [material, 'nozzle']})
		defSpeed = self.apparatus.getValue(['devices', motionname, nozzlename, 'speed'])
		self.apparatus.setValue(['information','ProcedureData','SpanningSample','cur_parameters','speed'], defSpeed)
		self.recordData.requirements['value']['address'] = ['information','ProcedureData','SpanningSample','cur_parameters']
		self.recordData.requirements['filename']['value'] = 'bleh.json'
		self.recordData.requirements['label']['value'] = 'Data'
		
		#init_speed = 20
		init_speed = defSpeed
		Sample_num = 1
		good_streak = 0 #use good_streak as a double check.. this counts number of goods we have had in a row
		double_check_lim = 3 #this is the number of times it will double check after reciving a good
		
		#changed this so that that one good isn't enough to end loop
		while good_streak < double_check_lim:
		#while prvClass != '1':
			print('\n\nNow Beginning Sample Number: ' + str(Sample_num))
			if prevSpeed == {}:
				print('\nNo Previous Class Detected')
				#nxtSpeed = defSpeed
				nxtSpeed = init_speed
				print('First Speed: ' + str(nxtSpeed) + ' mm/s')
				#no need to set anything here since we are already at default
			else:
				if prvClass == '1':
					#what to do when here?
					nxtSpeed = prevSpeed
					good_streak = good_streak + 1
					if good_streak == double_check_lim:
						print('Good Verified!!')
						break
					elif good_streak < double_check_lim:
						nxtSpeed = prevSpeed
						print(str(good_streak) + ' Good Prints in a Row')
						print('Good Detected... Repeat Speed: ' + str(nxtSpeed) + ' mm/s')
					pass
				elif prvClass == '2':
					nxtSpeed = prevSpeed*(1+0.1) #increase speed by 10% if slumped
					print('Next Speed: ' + str(nxtSpeed) + ' mm/s')
					self.apparatus.setValue(['devices', motionname, nozzlename, 'speed'], nxtSpeed)
				elif prvClass == '3':
					nxtSpeed = prevSpeed*(1-0.1) #decrease speed by 10% if broken
					print('Next Speed: ' + str(nxtSpeed) + ' mm/s')
					self.apparatus.setValue(['devices', motionname, nozzlename, 'speed'], nxtSpeed)
			self.apparatus.setValue(['information','ProcedureData','SpanningSample','cur_parameters','speed'], nxtSpeed)
			trayaddress = ['information', 'sampletray']
			self.newsample.Do({'trayaddress': trayaddress, 'material':material, 'yGap': yGap, 'zGap': zGap})
			ifilename = self.apparatus.getValue(['information','ProcedureData','SpanningSample','cur_parameters','InitialFile'])
			ffilename = self.apparatus.getValue(['information','ProcedureData','SpanningSample','cur_parameters','FinalFile'])
			self.classify.Do({'initial_file':ifilename, 'final_file':ffilename})
			self.recordData.Do()
			prevSpeed = prevSample['speed']
			prvClass = prevSample['Class']
			print('\nClass ' + str(prvClass) + str(' detected'))
			Sample_num = Sample_num + 1
			if prvClass != 1 and good_streak > 0:
				good_streak = 0
			
			
		print('\n\nLoop Finished Succesfully!\n\n')
	
	
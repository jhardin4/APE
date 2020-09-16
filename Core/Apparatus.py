from io import SEEK_END, SEEK_SET

import Devices
import json
import time
import uuid
import AppTemplates
import os
import tarfile
from Core import material

class InvalidApparatusAddressException(Exception):
    pass


class Apparatus(dict):
    def __init__(self):
        dict.__init__(self)
        self['devices'] = {}
        self['information'] = {}
        self['eproclist'] = []
        self['public release'] = '88ABW-2019-6134'
        self['APE version'] = {}
        self['APE version']['time'] = 1583331028
        self['APE version']['branch'] = 'master'
        self['APE version']['dev'] = 'James Hardin'
        self.proclog_threadindex = 0
        self.proclog_depthindex = 0
        self.executor = ''
        self.simulation = False
        self.dependent_Devices = []
        self.logpath = 'Logs//'
        self.AppID = str(int(round(time.time(), 0)))
        self.AppUUID = str(uuid.uuid4())
        self.run_name = ''

        self.timetest = 0
        self.starttime = 0
        self.app_units = ''
        self.proclog_address = ''

    def Connect_All(self, simulation=False):
        self.simulation = simulation
        # Set up the logging files
        self.ProcLogFileName = self.logpath + self.AppID + 'proclog.json'
        self.PLFirstWrite = True
        self.dataPack_prep()
        self.ProcLogFile = open(self.ProcLogFileName, mode='w')
        self.proclog_address = self.ProcLogFileName
        # Start the run ticket

        

        for device in self['devices']:
            self['devices'][device]['Connected'] = False
            if self['devices'][device]['addresstype'] == 'pointer':
                # Create instance of the Device
                self.executor.createDevice(
                    device,
                    self['devices'][device]['type'],
                    '',
                    self['devices'][device]['address'],
                )
                # Register the device with the Executor
                # self['devices'][device]['address'].ERegister(executor)

                # Add Device descriptors to Apparatus ones
                if (
                    'descriptors' in self['devices'][device]
                    and type(self['devices'][device]['descriptors']) == list
                ):
                    self['devices'][device]['descriptors'] = list(
                        {
                            *self['devices'][device]['descriptors'],
                            *self.executor.getDescriptors(
                                device, self['devices'][device]['address']
                            ),
                        }
                    )
                else:
                    self['devices'][device]['descriptors'] = self['devices'][device][
                        'address'
                    ].descriptors

                # Set Device simulation state
                self.executor.setSimulation(
                    device, simulation, self['devices'][device]['address']
                )

                # Check if the device is dependent on other devices and conncect if not dependent
                if self.executor.getDependence(
                    device, self['devices'][device]['address']
                ):
                    # Add to dependent device list for later processing
                    self.dependent_Devices.append(device)
                else:
                    self.Connect(device)
            elif self['devices'][device]['addresstype'] == 'zmqNode':
                # Create a device through the executor
                self.executor.createDevice(
                    device,
                    self['devices'][device]['type'],
                    'procexec',
                    self['devices'][device]['address'],
                )

                # Add Device descriptors to Apparatus ones
                if (
                    'descriptors' in self['devices'][device]
                    and type(self['devices'][device]['descriptors']) == list
                ):
                    self['devices'][device]['descriptors'] = list(
                        {
                            *self['devices'][device]['descriptors'],
                            *self.executor.getDescriptors(
                                device, self['devices'][device]['address']
                            ),
                        }
                    )
                else:
                    self['devices'][device][
                        'descriptors'
                    ] = self.executor.getDescriptors(
                        device, self['devices'][device]['address']
                    )

                # Set Device simulation state
                self.executor.setSimulation(
                    device, simulation, self['devices'][device]['address']
                )

                # Check if the device is dependent on other devices and connect if not dependent
                if self.executor.getDependence(
                    device, self['devices'][device]['address']
                ):
                    # Add to dependent device list for later processing
                    self.dependent_Devices.append(device)
                else:
                    self.Connect(device)

        # Connect the dependent devices
        self.Dep_Connects()
        self.logApparatus(prefix='initial')
        # Note associated materials in run ticket
        for mat in self['information']['material_library']:
            names = self['information']['material_library'][mat]['names']
            m_uuid = self['information']['material_library'][mat]['uuid']
            self.AddTicketItem({'material_names':names, 'uuid':m_uuid})

    def Connect(self, deviceName):
        arguments = self.executor.getRequirements(
            deviceName, 'Connect', self['devices'][deviceName]['address']
        )
        # Try to collect the required arguments together
        details = {}
        for element in arguments:
            if element != '':
                try:
                    details[element] = self['devices'][deviceName][element]
                except KeyError:
                    errorstr = element + ' missing. Insuffienct information to connect.'
                    raise Exception(errorstr)

        # Run the Connect method of the Device with the right arguments
        self.DoEproc(deviceName, 'Connect', details)

        # Note in the apparatus that the device is connected
        self['devices'][deviceName]['Connected'] = True

    def Dep_Connects(self):
        loopcounter = 0

        while len(self.dependent_Devices) > 0:
            device = self.dependent_Devices.pop(0)
            Ready2Connect = True
            depList = self.executor.getDependencies(
                device, self['devices'][device]['address']
            )

            for devname in depList:
                parent_devname = self['devices'][device][devname + 'name']

                if self['devices'][parent_devname]['Connected']:
                    self['devices'][device][devname + 'address'] = self['devices'][
                        parent_devname
                    ]['address']
                else:
                    Ready2Connect = False

            if Ready2Connect:
                self.Connect(device)
                loopcounter = 0
            else:
                self.dependent_Devices.append(device)

            loopcounter += 1
            if len(self.dependent_Devices) != 0 and loopcounter > 4 * len(
                self.dependent_Devices
            ):
                raise Exception('Dependencies not found')

    def Disconnect(self, deviceName):
        if self['devices'][deviceName]['addresstype'] != '':
            self.DoEproc(deviceName, 'Disconnect', {})
            self['devices'][deviceName]['Connected'] = False

    def Disconnect_All(self, simulation=False):
        for device in self['devices']:
            self.Disconnect(device)
        self.logApparatus(prefix='final')
        if not self.PLFirstWrite:
            self.ProcLogFile.close()    
        self.dataPack_make()

    def getValue(self, infoAddress=''):
        if infoAddress == '':
            return ''

        level = self

        for branch in infoAddress:
            try:
                level = level[branch]
            except TypeError:
                raise InvalidApparatusAddressException(
                    f'Type does not match: {infoAddress}'
                )
            except KeyError:
                raise InvalidApparatusAddressException(f'Key not found: {infoAddress}')
        return level

    def getSimulation(self):
        return self.simulation

    def checkAddress(self, infoAddress=''):
        try:
            _ = self.getValue(infoAddress)
        except InvalidApparatusAddressException:
            return False
        else:
            return True

    def setValue(self, infoAddress=None, value=''):
        if not infoAddress:
            return ''

        level = self
        lastlevel = infoAddress[-1]

        for branch in infoAddress[:-1]:
            try:
                level = level[branch]
            except TypeError:
                raise InvalidApparatusAddressException(
                    f'Type does not match: {infoAddress}'
                )
            except KeyError:
                raise InvalidApparatusAddressException(f'Key not found: {infoAddress}')
        level[lastlevel] = value

    def add_device_entry(self, name, dtype='', details={}):
        # Check to see if name is already in use
        if name in self['devices']:
            raise Exception(f'{name} is already in use.')
        # Check to make sure the Device exists
        if dtype != '':
            try:
                getattr(Devices, dtype)
            except AttributeError:
                raise Exception(f'{dtype} was not found in Devices')
        # Make the basic device entry
        self['devices'][name] = {
            'type': dtype,
            'addresstype': 'pointer',
            'descriptors': [],
            'address': ''
        }
        # Fill in other elements
        for detail in details:
            self['devices'][name][detail] = details[detail]

    def findDevices(self, key, value=None):
        if value is None:
            value = []
        foundDevices = []

        for device in self['devices']:
            devicePasses = True

            if key not in self['devices'][device]:
                devicePasses = False
            else:
                if value != []:
                    if (
                        type(self['devices'][device][key]) == dict
                        or type(self['devices'][device][key]) == list
                    ):
                        if value not in self['devices'][device][key]:
                            devicePasses = False

                    elif self['devices'][device][key] != value:
                        devicePasses = False

            if devicePasses:
                foundDevices.append(device)

        return foundDevices

    def findDevice(self, **reqs):
        devicesOld = ''
        devicesNew = []
        devicesTemp = []
        requirements = []

        for req in reqs:
            if type(reqs[req]) == list:
                for element in reqs[req]:
                    requirements.append([req, element])
            else:
                requirements.append([req, reqs[req]])

        for line in requirements:
            devicesNew = self.findDevices(line[0], line[1])

            if devicesOld == '':
                devicesOld = devicesNew
            else:
                devicesTemp = devicesOld[:]

                for device in devicesOld:
                    if device not in devicesNew:
                        devicesTemp.remove(device)

                devicesOld = devicesTemp[:]

        if len(devicesOld) == 1:
            return devicesOld[0]
        elif len(devicesOld) > 1:
            return 'More than 1 device met requirments.' + str(devicesOld)
        elif len(devicesOld) == 0:
            return 'No devices met requirments'

    def LogProc(self, flag, procName, puuid, log='', reqs=''):
        procLogLine = []
        if flag == 'start':
            self.proclog_depthindex += 1
            for n in range(self.proclog_depthindex):
                procLogLine.append('->')
            s_reqs = self.safeCopy(reqs)
            proc_entry = {'name': procName, 'uuid':puuid, 'requirements': s_reqs, 'start_time':time.time()}
              
        elif flag == 'end':
            for n in range(self.proclog_depthindex):
                procLogLine.append('->')
            proc_entry = {'name': procName, 'uuid':puuid, 'end_time':time.time()}
            if log != '':
                proc_entry['e_log'] = log
            self.proclog_depthindex -= 1
            # print(log)

        elif flag == 'report':
            for n in range(self.proclog_depthindex):
                procLogLine.append('->')
            proc_entry = {'name': procName, 'uuid':puuid, 'report':log, 'r_time':time.time()}
            
        procLogLine.append(proc_entry)
        self.UpdateLog(procLogLine)

    def AddTicketItem(self, item_dict):
        if 'start_ticket' in item_dict:
            item_dict['start_ticket'] = time.time()
        elif 'end_ticket' in item_dict:
            item_dict['end_ticket'] = time.time()             
        else:
            item_dict['ticket_time'] = time.time()
        self.UpdateTicket(item_dict)

    def UpdateTicket(self, entry):
        if self.RTFirstWrite:
            json.dump([], self.TicketFile)
            self.RTFirstWrite = False
            eof = self.TicketFile.seek(0, SEEK_END)
            self.TicketFile.seek(eof - 1, SEEK_SET)
        else:
            eof = self.TicketFile.seek(0, SEEK_END)
            self.TicketFile.seek(eof - 1, SEEK_SET)
            self.TicketFile.write(', ')

        json.dump(entry, self.TicketFile)
        self.TicketFile.write(']')

    def UpdateLog(self, entry):
        # print(entry)
        if self.PLFirstWrite:
            json.dump([], self.ProcLogFile)
            self.PLFirstWrite = False
            eof = self.ProcLogFile.seek(0, SEEK_END)
            self.ProcLogFile.seek(eof - 1, SEEK_SET)
        else:
            eof = self.ProcLogFile.seek(0, SEEK_END)
            self.ProcLogFile.seek(eof - 1, SEEK_SET)
            self.ProcLogFile.write(', ')

        json.dump(entry, self.ProcLogFile)
        self.ProcLogFile.write(']')

    def buildInfoEntry(self, information):
        simpleinfo = {}

        if type(information) == str:
            simpleinfo = information
        elif type(information) == dict:
            for info in information:
                if (type(information[info]) == dict) and ('value' in information[info]):
                    if type(information[info]['value']) in [
                        dict,
                        list,
                        int,
                        float,
                        str,
                    ]:
                        simpleinfo[info] = information[info]['value']
                    else:
                        simpleinfo[info] = str(type(information[info]))
                else:
                    if type(information[info]) in [dict, list, int, float, str]:
                        simpleinfo[info] = information[info]
                    else:
                        simpleinfo[info] = str(type(information[info]))

        return simpleinfo

    def serialClone(self, abranch=None, address=None):
        # Default target is the apparatus object
        if abranch is None:
            abranch = self

        # If a specific portion of abranch is specified via a list of indexes
        # navigate to the portion
        if address:
            for entry in address:
                if entry in abranch:
                    abranch = abranch[entry]
                else:
                    return None
        # Return a safe copy of the abranch
        return self.safeCopy(abranch)

    def safeCopy(self, target):
        if isinstance(target, dict):
            tempdict = {}
            for key, value in target.items():
                tempdict[key] = self.safeCopy(target=value)
            return tempdict

        elif isinstance(target, list):
            templist = []
            for item in target:
                templist.append(self.safeCopy(target=item))
            return templist

        elif isinstance(target, (bool, int, float, str)):
            return target
        else:
            return str(type(target))

    def logApparatus(self, fname=None, prefix=''):
        if not fname:
            fname = self.logpath + str(int(round(time.time(), 0))) + prefix + 'Apparatus.json'
        jsonfile = open(fname, mode='w')
        json.dump(self.serialClone(), jsonfile, indent=2, sort_keys=True)
        jsonfile.close()
        self.AddTicketItem({'ApparatusImage':fname})

    def importApparatus(self, fname=None):
        if not fname:
            fname = self.logpath + str(int(round(time.time(), 0))) + 'Apparatus.json'
        with open(fname, 'r') as old_app:
            old_app_data = json.load(old_app)
            # Replace the current device and information
            self['devices'] = old_app_data['devices']
            self['information'] = old_app_data['information']

    def DoEproc(self, device, method, details):
        procname = 'eproc_' + device + '_' + method
        p_uuid = str(uuid.uuid4())
        self.LogProc('start', procname, p_uuid, reqs=details)

        try:
            e_log = self.executor.execute(
                [[{'devices': device, 'procedure': method, 'details': details}]]
            )
            
        finally:  # makes sure depthindex is decreased on error
            self.LogProc('end', procname, p_uuid, log=e_log)

    def createAppEntry(self, app_address):
        target = self
        # Build everything but the last entry
        for entry in app_address[:-1]:
            if entry in target:
                if type(target[entry]) == dict:
                    target = target[entry]
                else:
                    raise Exception(
                        str(entry) + ' in ' + str(app_address) + ' is already occupied'
                    )
            else:
                target[entry] = {}
                target = target[entry]
        if app_address[-1] not in target:
            target[app_address[-1]] = {}

    def removeAppEntry(self, app_address):
        target = self
        for entry in app_address[:-1]:
            if entry in target:
                target = target[entry]
            else:
                return
        if app_address[-1] in target:
            del target[app_address[-1]]

    def applyTemplate(self, template, args=None, kwargs=None):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        if template == 'blank':
            self['devices'] = {}
            self['information'] = {}
        else:
            templateFunc = getattr(AppTemplates, template)
            templateFunc(self, *args, **kwargs)
    def dataPack_prep(self):
        #check if ticket already exists
        main_file_list = os.listdir()
        old_data = False
        old_ticket = ''
        for filename in main_file_list:
            if filename.endswith('RunTicket.json'):
                old_data = True
                old_ticket = filename
        # if old data exists, pack it up.
        # THIS ONLY WORKS FOR ONE OLD TICKET!
        self.RTFirstWrite = True
        if old_data:
            self.dataPack_make(ticket=old_ticket)
        # Create new ticket
        self.TicketFilename = self.AppID + 'RunTicket.json'
        self.TicketFile = open(self.TicketFilename, mode='w')
        self.RTFirstWrite = True
        self.AddTicketItem({'start_ticket':''})
        self.AddTicketItem({'proclog':self.ProcLogFileName})
        self.AddTicketItem({'run_name':self.AppID + self.run_name})

    def dataPack_make(self, ticket=''):
        fname = str(int(round(time.time(), 0)))
        
        # Check to see if the ticket file is still open
        if not self.RTFirstWrite:
            self.AddTicketItem({'DataPack':fname})
            self.AddTicketItem({'end_ticket':''})
            self.TicketFile.close()
        else:
            self.TicketFile = open(ticket, mode='w+')
            self.AddTicketItem({'DataPack':fname})
            self.AddTicketItem({'end_ticket':''})
            self.TicketFile.close()
        
        # Check for DataPacks Folder and create one if not there
        if not os.path.exists('DataPacks'):
            os.mkdir('DataPacks')
        
        # Create a folder for this specific pack
        foldername = os.path.join('DataPacks', fname)
        os.mkdir(foldername)
        
        # Make a Payload folder
        pfolder = os.path.join(foldername,'Payload' + fname)
        os.mkdir(pfolder)
        
        # Move Data and Logs into payload folder
        copied_folders = ['Data', 'Logs']
        excluded_files = ['readme.txt','.gitignore']
        for folder in copied_folders:
            fpath = os.path.join(os.getcwd(), folder)
            new_fpath = os.path.join(os.getcwd(), pfolder, folder)
            os.mkdir(new_fpath)
            for root, dirs, files in os.walk(fpath):
                for file in files:
                    old_file = os.path.join(root, file)
                    new_file = os.path.join(new_fpath, file)
                    if file not in excluded_files:
                        try:
                            os.rename(old_file, new_file)
                        except PermissionError:
                            print(f'{old_file} or {new_file} is probably in use. Trying to close the log...')
                            if hasattr(self.executor, 'close'):
                                self.executor.loghandle.close()
                                os.rename(old_file, new_file)
                                print('Got it. No worries!')
        
        # Copy the scripts into an archive in the payload folder
        APE_version = tarfile.open(pfolder + '\\APE_version.tar', mode='w')
        copied_extensions = ('.py', '.ui', '.qml')
        cwd = os.getcwd()
        for root, dirs, files in os.walk(cwd):
            # print(root, dirs, files)
            for file in files:
                rel_file_path = os.path.join(root.replace(cwd, ''), file)
                if file.endswith(copied_extensions):
                    APE_version.add(os.path.join(root, file), arcname = rel_file_path)
            
        APE_version.close()        
        
        # Move ticket into folder
        main_file_list = os.listdir()
        for filename in main_file_list:
            if filename.endswith('RunTicket.json'):
                ticket_file = filename
        old_file = os.path.join(os.getcwd(), ticket_file)
        new_file = os.path.join(os.getcwd(), foldername, ticket_file)
        os.rename(old_file, new_file)
        self._makeUpLoadPack(foldername)
        self.proclog_address = os.path.join(pfolder, self.proclog_address)

    def _makeUpLoadPack(self, folder):
        # Assumes that folder does not end in \\.
        UpLoadPack = tarfile.open(folder + 'UPLOAD_ME.tar', mode='w')
        for root, dirs, files in os.walk(folder):
            # print(root, dirs, files)
            for file in files:
                rel_file_path = root.replace(folder, '') + '\\' + file
                UpLoadPack.add(os.path.join(root, file), arcname = rel_file_path)
            
        UpLoadPack.close()
    
    def addMaterial(self, m_name, mat_fname):
        # Import the material from file
        if 'material_library' in self['information']:
            self['information']['material_library'][m_name] = material(file=mat_fname)
        else:
            self['information']['material_library'] = {m_name: material(file=mat_fname)}
        # Confirm that m_name is in names list and add it if not, add it
        new_material = self['information']['material_library'][m_name]
        if m_name not in new_material['names']:
            new_material['names'].append(m_name)
        # Add the material properties in Apparatus
        for prop in new_material['properties']:
            self.createAppEntry(['information', 'materials', m_name, prop])
            self.setValue(['information', 'materials', m_name, prop], new_material['properties'][prop]['value'])
        
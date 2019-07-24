import Devices
import json
import time
import AppTemplates


class InvalidApparatusAddressException(Exception):
    pass


class Apparatus(dict):
    def __init__(self):
        dict.__init__(self)
        self['devices'] = {}
        self['information'] = {}
        self['eproclist'] = []
        self.proclog = []
        self[
            'proclog'
        ] = self.proclog  # this was put in because I am too lazy to fix it right
        self.proclog_threadindex = 0
        self.proclog_depthindex = 0
        self.executor = ''
        self.simulation = False
        self.dependent_Devices = []
        self.logpath = 'Logs//'

    def Connect_All(self, simulation=False):
        self.simulation = simulation
        # self.executor = executor

        for device in self['devices']:
            self['devices'][device]['Connected'] = False
            if self['devices'][device]['addresstype'] == 'pointer':
                # Create instance of the Device
                self['devices'][device]['address'] = getattr(
                    Devices, self['devices'][device]['type']
                )(device)
                self.executor.loadDevice(
                    device, self['devices'][device]['address'], 'pointer'
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
                            *self['devices'][device]['address'].descriptors,
                        }
                    )
                else:
                    self['devices'][device]['descriptors'] = self['devices'][device][
                        'address'
                    ].descriptors

                # Set Device simulation state
                self['devices'][device]['address'].simulation = simulation

                # Check if the device is dependent on other devices and conncect if not dependent
                if self['devices'][device]['address'].dependent_device:
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

                # Check if the device is dependent on other devices and conncect if not dependent
                if self.executor.getDependence(
                    device, self['devices'][device]['address']
                ):
                    # Add to dependent device list for later processing
                    self.dependent_Devices.append(device)
                else:
                    self.Connect(device)

        # Connect the dependent devices
        self.Dep_Connects()
        self.logApparatus()

    def Connect(self, deviceName):
        # use default executor if none is given
        # if executor == '':
        #    executor = self.executor

        # Get Arguments of Connect for the device
        # self['devices'][deviceName]['address'].CreateEprocs(self, self.executor)
        if self['devices'][deviceName]['addresstype'] == 'pointer':
            arguments = list(
                self['devices'][deviceName]['address'].requirements['Connect']
            )
        if self['devices'][deviceName]['addresstype'] == 'zmqNode':
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
        # deviceconnect.Do(details)
        self.DoEproc(deviceName, 'Connect', details)

        # Note in the apparatus that the device is connected
        self['devices'][deviceName]['Connected'] = True

    def Dep_Connects(self):
        loopcounter = 0

        while len(self.dependent_Devices) > 0:
            device = self.dependent_Devices.pop(0)
            Ready2Connect = True
            if self['devices'][device]['addresstype'] == 'pointer':
                depList = self.executor.getDependencies(device)
            elif self['devices'][device]['addresstype'] == 'zmqNode':
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
        # if self['devices'][deviceName]['addresstype'] == 'pointer':
        # deviceDisconnect = self.GetEproc(deviceName, 'Disconnect')
        # deviceDisconnect.Do()
        if self['devices'][deviceName]['addresstype'] != '':
            self.DoEproc(deviceName, 'Disconnect', {})
            # Remove the eprocs registered with the apparatus
            # methodlist = self.findDeviceMethods(deviceName)
            # for method in methodlist:
            # self.removeEproc(deviceName, method)

    def Disconnect_All(self, simulation=False):
        for device in self['devices']:
            self.Disconnect(device)
        self.logApparatus()

        # need to change Connected in devices to False to show all devices disconnected

        # code after this was added to wok on disconnect button

    def getValue(self, infoAddress=''):
        if infoAddress == '':
            return ''

        level = self

        for branch in infoAddress:
            try:
                level = level[branch]
            except TypeError:
                raise InvalidApparatusAddressException('Type does not match')
            except KeyError:
                raise InvalidApparatusAddressException('Key not found')
        return level

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
                raise InvalidApparatusAddressException('Type does not match')
            except KeyError:
                raise InvalidApparatusAddressException('Key not found')
        level[lastlevel] = value

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

    def findDevice(self, reqs):
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

    def findDeviceMethods(self, device):
        methodlist = []
        for line in self['eproclist']:
            if line['device'] == device:
                methodlist.append(line['method'])
        return methodlist

    def GetEproc(self, device, method):
        for line in self['eproclist']:
            if line['device'] == device and line['method'] == method:
                return line['handle']

        return 'No matching elemental procedure found.'

    def removeEproc(self, device, method):
        found = False
        for n in range(len(self['eproclist'])):
            if not found:
                if (
                    self['eproclist'][n]['device'] == device
                    and self['eproclist'][n]['method'] == method
                ):
                    self['eproclist'].pop(n)
                    found = True
        if not found:
            print('Elemental procedure ' + method + ' of ' + device + ' not found.')

    def LogProc(self, procName, information):
        if information == 'start':
            self.proclog_depthindex += 1
        elif information == 'end':
            self.proclog_depthindex -= 1
        else:
            info = self.buildInfoEntry(information)
            procLogLine = []

            for n in range(self.proclog_depthindex):
                procLogLine.append('->')

            procLogLine.append({'name': procName, 'information': info})
            self.proclog.append(procLogLine)

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
        if abranch is None:
            abranch = self

        if address:
            for entry in address:
                if entry in abranch:
                    abranch = abranch[entry]
                else:
                    return None

        if isinstance(abranch, dict):
            tempdict = {}
            for key, value in abranch.items():
                tempdict[key] = self.serialClone(abranch=value)
            return tempdict

        elif isinstance(abranch, list):
            templist = []
            for item in abranch:
                templist.append(self.serialClone(abranch=item))
            return templist

        elif isinstance(abranch, (bool, int, float, str)):
            return abranch
        else:
            return str(type(abranch))

    def logApparatus(self, fname=None):
        if not fname:
            fname = self.logpath + str(int(round(time.time(), 0))) + 'Apparatus.json'
        jsonfile = open(fname, mode='w')
        json.dump(self.serialClone(), jsonfile, indent=2, sort_keys=True)
        jsonfile.close()

    def importApparatus(self, fname=None):
        if not fname:
            fname = self.logpath + str(int(round(time.time(), 0))) + 'Apparatus.json'
        with open(fname, 'r') as old_app:
            old_app_data = json.load(old_app)
            # Clear the proclog
            self.proclog = []
            self['proclog'] = self.proclog
            # Replace the current device and information
            self['devices'] = old_app_data['devices']
            self['information'] = old_app_data['information']

    def DoEproc(self, device, method, details):
        self.LogProc('eproc_' + device + '_' + method, 'start')
        self.executor.execute(
            [[{'devices': device, 'procedure': method, 'details': details}]]
        )
        self.LogProc('eproc_' + device + '_' + method, details)
        self.LogProc('eproc_' + device + '_' + method, 'end')

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

# This Device represents a general G-Code motion system.

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#

from Devices import Device


class Motion(Device):
    def __init__(self, name):
        # Run the Device initialization.
        Device.__init__(self, name)
        # Run simulation is controlled by its own
        # Append relevant descriptors
        self.descriptors.append('motion')
        # This log hold commands to be sent
        self.commandlog = []
        # This is the default motion type.  Currently, only linear motion is
        # set up here.
        self.motiontype = 'linear'
        # There are two modes here, 'loadrun' and 'cmd'
        # 'loadrun' does not send the commandlog until explicitly told to
        # 'cmd' sends each command as it gets them
        self.motionmode = 'loadrun'
        # Defines the motion axes of the motion device
        self.axes = ['X', 'x', 'Y', 'y', 'Z', 'z']
        # Strage location for default motion settings
        self.motionsetting = {}
        # Defining the elemental procedures
        self.requirements['Move'] = {}
        self.requirements['Move']['point'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Dictionary with the motions sytem axes as keys and target values',
        }
        self.requirements['Move']['speed'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'speed of motion, typicaly in mm/s',
        }
        self.requirements['Move']['motiontype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'speed of motion, typicaly in mm/s',
        }
        self.requirements['Move']['motionmode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'cmd or loadrun',
        }

        self.requirements['Set_Motion'] = {}
        self.requirements['Set_Motion']['RelAbs'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Relative or Absolute motion',
        }
        self.requirements['Set_Motion']['dmotionmode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'default motion mode',
        }
        self.requirements['Set_Motion']['dmotiontype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'default motion type',
        }
        self.requirements['Set_Motion']['motionmode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'cmd or loadrun',
        }

    def Move(self, point={}, speed='', motiontype='', motionmode=''):
        # Move to a point at a speed in a manner dictated by the motiontype
        # Use default settings for motiontype and speed
        if speed == '':
            speed = self.motionsetting['speed']
        if motiontype == '':
            motiontype = self.motionsetting['motiontype']
        # Create the G-code command line with MotionCMD and append it to the
        # current command log
        self.commandlog.append(self.MotionCMD(point, speed, motiontype))
        # Run according to the current motionmode
        self.fRun(motionmode)

        return self.returnlog()

    def Set_Motion(self, RelAbs='', dmotionmode='', dmotiontype='', motionmode=''):
        # Change settings of the Motion device
        #
        if dmotionmode != '':
            self.motionmode = dmotionmode
            self.motionsettings['motionmode'] = dmotionmode

        if dmotiontype != '':
            self.motiontype = dmotiontype
            self.motionsettings['motiontype'] = dmotiontype

        if RelAbs != '':
            self.fSet_RelAbs(RelAbs, motionmode)

        return self.returnlog()

    def fSet_RelAbs(self, RelAbs, motionmode):
        if RelAbs == 'Rel':
            self.commandlog.append('G91 \n')

        if RelAbs == 'Abs':
            self.commandlog.append('G90 \n')

        self.motionsettings['RelAbs'] = RelAbs
        self.fRun(motionmode)

    def MotionCMD(self, point, speed, motiontype):
        if motiontype == '':
            motiontype = self.motiontype
        cmdline = ''
        if motiontype == 'linear':
            cmdline += 'G01 '
            for axis in self.axes:
                if axis in point:
                    cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' '
            cmdline += 'F ' + '{0:f}'.format(speed) + ' '
            cmdline += '\n'

        return cmdline

    def Run(self, motionmode=''):
        if motionmode == '':
            motionmode = 'cmd'
        self.fRun(motionmode)
        return self.returnlog()

    def fRun(self, motionmode):
        if motionmode == '':
            motionmode = self.motionmode
        if motionmode == 'loadrun':
            self.addlog('Commands Loaded')
        elif motionmode == 'cmd':
            cmdline = self.commandlog
            self.sendCommands(cmdline)
            self.commandlog = []

    def sendCommands(self, commands):
        message = ''

        for line in commands:
            message += line

        self.addlog(message)


if __name__ == '__main__':
    myMotion = Motion('myMotion')

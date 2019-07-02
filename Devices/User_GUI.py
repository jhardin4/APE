from PyQt5.QtWidgets import QInputDialog, QLineEdit, QWidget
from Devices import Sensor


class User_GUI(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.descriptors = [*self.descriptors, *['sensor', 'User', 'guiconsol']]
        self.requirements['GetInput'] = {}
        self.requirements['GetInput']['message'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Message to be displayed',
        }
        self.requirements['GetInput']['options'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Possible answers',
        }
        self.requirements['GetInput']['default'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'default response',
        }

    def GetInputOptions(
        self, message='', options='', default='', address='', addressType=''
    ):
        # Construct the list of options if options are given
        if options != '':
            i = 0
            # if there is no default, the default will be the first value
            d = 0
            for option in options:
                # Add in special formatting if a default is given
                if option == default:
                    d = i
                else:
                    i = i + 1
            # this will create the pop up window
            item, ok = QInputDialog.getItem(None, 'Input', message, options, d, False)
        if item and ok:
            response = item
        else:
            response == 'stop'
        if response == 'stop':
            self.addlog(response)
            raise Exception('User requested stop')
        self.StoreMeasurement(address, addressType, response)
        self.addlog(response)
        return self.returnlog()

    def GetInput(self, message='', default='', address='', addressType=''):
        item, ok = QInputDialog.getText(
            None, 'Input', message, QLineEdit.Normal, default
        )
        if ok:
            response = item
        if response == '':
            response = default
        elif response == 'stop':
            self.addlog(response)
            raise Exception('User requested stop')
        self.StoreMeasurement(address, addressType, response)
        self.addlog(response)
        return self.returnlog()

from qtpy.QtCore import QCoreApplication
from qtpy.QtWidgets import QInputDialog, QLineEdit
from Devices import Sensor


class User_GUI(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.descriptors = list(
            {*self.descriptors, 'sensor', 'User', 'guiconsol', 'consol'}
        )
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
        ok = False
        item = ''
        if options != '':
            input_dialog = QInputDialog()
            input_dialog.setComboBoxItems(options)
            input_dialog.setComboBoxEditable(False)
            if default:  # of there is no default, the first item will be the default
                input_dialog.setTextValue(default)
            input_dialog.setWindowTitle("Input")
            input_dialog.setLabelText(message)
            input_dialog.setModal(False)
            input_dialog.show()
            while input_dialog.isVisible():
                QCoreApplication.processEvents()
            ok = input_dialog.result()
            item = input_dialog.textValue()
        response = item if ok and item else 'stop'

        if response == 'stop':
            self.addlog(response)
            raise Exception('User requested stop')
        self.StoreMeasurement(address, addressType, response)
        self.addlog(response)
        return self.returnlog()

    def GetInput(self, message='', default='', address='', addressType=''):
        input_dialog = QInputDialog()
        input_dialog.setTextEchoMode(QLineEdit.Normal)
        input_dialog.setTextValue(default)
        input_dialog.setWindowTitle("Input")
        input_dialog.setLabelText(message)
        input_dialog.setModal(False)
        input_dialog.show()
        while input_dialog.isVisible():
            QCoreApplication.processEvents()
        ok = input_dialog.result()
        item = input_dialog.textValue()
        response = item if ok else 'stop'

        if response == '':
            response = default
        elif response == 'stop':
            self.addlog(response)
            raise Exception('User requested stop')
        self.StoreMeasurement(address, addressType, response)
        self.addlog(response)
        return self.returnlog()

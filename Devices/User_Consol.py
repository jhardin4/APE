# blank
# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#

from Devices import Sensor


class User_Consol(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.descriptors = [*self.descriptors, *['sensor', 'User', 'consol']]
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
        print(message)
        # Construct the list of options if options are given
        if options != '':
            option_string = '('
            for option in options:
                # Add in special formatting if a default is given
                if option == default:
                    option_string += '['
                option_string += option
                if option == default:
                    option_string += ']'
                if option != options[len(options) - 1]:
                    option_string += ', '
            option_string += ')'
            print(option_string)
        response_list = [options[n] for n in range(len(options))]
        response_list.append('stop')
        acceptable_response = False
        response = 'stop'
        while not acceptable_response:
            response = input('')
            if response == '':
                response = default
            if response in response_list:
                acceptable_response = True
            else:
                print('Incorrect response.')

        if response == 'stop':
            self.addlog(response)
            raise Exception('User requested stop')
        self.StoreMeasurement(address, addressType, response)
        self.addlog(response)
        return self.returnlog()

    def GetInput(self, message='', default='', address='', addressType=''):
        print(message)
        print('[' + str(default) + ']')
        response = input('')
        if response == '':
            response = default
        elif response == 'stop':
            self.addlog(response)
            raise Exception('User requested stop')
        self.StoreMeasurement(address, addressType, response)
        self.addlog(response)
        return self.returnlog()

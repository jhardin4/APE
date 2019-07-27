from Core import Procedure


class Data_User_Input_Options(Procedure):
    def Prepare(self):
        self.name = 'Data_User_Input_Options'
        self.requirements['message'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Message to be displayed',
        }
        self.requirements['options'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Possible answers',
        }
        self.requirements['default'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'default response',
        }
        self.response = ''

    def Plan(self):
        # Renaming useful pieces of informaiton
        message = self.requirements['message']['value']
        options = self.requirements['options']['value']
        default = self.requirements['default']['value']

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        print(message)
        option_string = '('
        for option in options:
            if option == default:
                option_string += '['
            option_string += options
            if option == default:
                option_string += ']'
            if option != options[len(options) - 1]:
                option += ','
        option_string += ')'
        self.response = input('')
        if self.response == '':
            self.response = default
        self.Report(string=self.response)

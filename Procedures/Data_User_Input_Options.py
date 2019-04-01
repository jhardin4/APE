from Core import Procedure


class Data_User_Input_Options(Procedure):
    def Prepare(self):
        self.name = 'Data_User_Input_Options'
        self.requirements['message'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'Message to be displayed'}
        self.requirements['options'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'Possible answers'}
        self.requirements['default'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'default response'}
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
            option_string += option
            if option == default:
                option_string += ']'
            if option != options[len(options)-1]:
                option_string += ', '
        option_string += ')'
        print(option_string)
        response_list = [options[n] for n in range(len(options))]
        response_list.append('stop')
        acceptable_response = False
        while not acceptable_response:
            self.response = input('')
            if self.response == '':
                self.response = default
            if self.response in response_list:
                acceptable_response = True
            else:
                print('Incorrect response.')

        if self.response == 'stop':
            self.Report(string=self.response)
            raise Exception('User requested stop')
        self.Report(string=self.response)

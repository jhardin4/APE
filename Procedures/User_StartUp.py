from Core import Procedure
import Procedures.User_FlexPrinter_Alignments_Update
import Procedures.User_FlexPrinter_Alignments_Derive
import json
import time


class User_StartUp(Procedure):
    def Prepare(self):
        self.name = 'User_StartUp'
        self.requirements['filename'] = {
            'source': 'apparatus',
            'address': ['information', 'StartUp', 'file'],
            'value': '',
            'desc': 'name of start up file',
        }
        self.apparatus.createAppEntry(['information', 'StartUp', 'file'])
        self.apparatus.createAppEntry(['information', 'StartUp', 'info'])
        self.useroptions = Procedures.User_Consol_InputOptions(
            self.apparatus, self.executor
        )
        self.userinput = Procedures.User_Consol_Input(self.apparatus, self.executor)

    def Plan(self):
        filename = self.requirements['filename']['value']
        # List off the basic questions to be asked at the start of a run
        questions = {}
        questions['Name'] = {'message': 'What is your name?', 'default': None}
        questions['Temperature'] = {
            'message': 'What is the lab temperature in Celsius?',
            'default': None,
        }
        questions['Humidity'] = {
            'message': 'What is the lab relative humidity in percent?',
            'default': None,
        }
        questions['Reason'] = {
            'message': 'What are you hoping to accomplish with this experiment?',
            'default': None,
        }
        questions['Difference'] = {
            'message': 'How is this experiment different than the last?',
            'default': None,
        }

        # Doing stuff

        # Check for loading file
        message = 'Import start up information from file from file?'
        options = ['y', 'n']
        default = 'y'
        self.useroptions.Do(
            {'message': message, 'options': options, 'default': default}
        )
        doQuestions = self.useroptions.response
        if doQuestions == 'y':
            message = 'What filename?'
            default = filename
            self.userinput.Do({'message': message, 'default': default})
            afilename = self.userinput.response
            try:
                with open(filename, 'r') as TPjson:
                    answers = json.load(TPjson)
                # Update the answers that are present in the file
                for answer in answers:
                    if (answer in questions) and (answer in answers):
                        questions[answer]['answer'] = answers[answer]['answer']
            except FileNotFoundError:
                print('No file loaded.  Possible error in ' + afilename)

        # If answers to questions were not collected from a file, collect them directly
        for question in questions:
            if ('answer' not in questions[question]) or questions[question][
                'answer'
            ] is None:
                questions[question]['answer'] = self.AskQuestion(questions[question])

        # Check if any questions need to be redone
        infoOK = False
        while not infoOK:
            message = (
                self.PrintInfo(questions) + 'Would you like to redo any questions?'
            )
            options = ['y', 'n']
            default = 'n'
            self.useroptions.Do(
                {'message': message, 'options': options, 'default': default}
            )
            redoQuestion = self.useroptions.response
            if redoQuestion == 'y':
                message = 'Which question would you like to redo?'
                options = list(questions)
                default = ''
                self.useroptions.Do(
                    {'message': message, 'options': options, 'default': default}
                )
                which_question = self.useroptions.response
                if which_question in questions:
                    questions[which_question]['answer'] = self.AskQuestion(
                        questions[which_question]
                    )
                else:
                    print('Question is not in list.')
            else:
                infoOK = True

        # Use the measured alignments to derive the remaining needed alignments
        self.apparatus.setValue(['information', 'StartUp', 'info'], questions)

        # Save a copy of the answers to the main folder and to the log folder
        with open(filename, 'w') as TPjson:
            json.dump(questions, TPjson)

        with open('Logs/' + str(int(round(time.time(), 0))) + filename, 'w') as TPjson:
            json.dump(questions, TPjson)

    def PrintInfo(self, information):
        printstr = ''
        for info in information:
            printstr += info + '\n'
            printstr += information[info]['message'] + '\n'
            printstr += information[info]['answer'] + '\n'
            printstr += '\n'
        return printstr

    def AskQuestion(self, question):
        message = question['message']
        default = question['default']
        # Handle the two potential kinds of questions
        if 'options' in question:
            options = question['options']
            self.useroptions.Do(
                {'message': message, 'options': options, 'default': default}
            )
            return self.useroptions.response
        else:
            self.userinput.Do({'message': message, 'default': default})
            return self.userinput.response

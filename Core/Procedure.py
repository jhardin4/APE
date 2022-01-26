from Core.Apparatus import InvalidApparatusAddressException
import time
import uuid

class Procedure:
    def __init__(self, apparatus, executor, **kwargs):
        self.requirements = {}
        self.apparatus = apparatus
        self.executor = executor
        self.name = 'Undefined Name'
        # dictionary of entries for the form
        # 'requirement':{'desc':'Describe the requirement', 'source':'apparatus' or 'direct', 'value':14 or '', 'address'= ApparatusAdress }
        self.Prepare(**kwargs)
        self.id = str(uuid.uuid4())
        self.first_var_run = True

    def Prepare(self, **kwargs):
        # Set up the requirements
        # Initialize the procedures that make up this procedure
        # Propigate any information necessary for set up of this proceedure
        pass

    def Plan(self):
        # Get the procedures that you want
        pass

    def Do(self, values=None):
        if values is None:
            values = {}
        self.GetRequirements(values)
        # self.CheckRequirements()
        self.apparatus.LogProc('start', self.name, self.id, reqs=self.requirements)
        try:
            self.Plan()
        finally:  # makes sure depthindex is decreased on error
            self.apparatus.LogProc('end', self.name, self.id)

    def Report(self, message):
        self.apparatus.LogProc('report', self.name, self.id, log=message)

    def GetRequirements(self, values):
        # Fills in the the requirements from the apparatus and given values
        # Given values override apparatus values
        # Once set, values are held until changed
        # Handle apparatus values
        for req in self.requirements:
            # Check if set for apparatus reference AND that an appAddress is given
            if self.requirements[req]['source'] == 'apparatus' and self.requirements[
                req
            ]['address'] not in ('', None):
                try:
                    tempvalue = self.apparatus.getValue(
                        self.requirements[req]['address']
                    )
                    self.requirements[req]['value'] = tempvalue
                except InvalidApparatusAddressException:
                    raise Exception(
                        f"ApparatusAddress {self.requirements[req]['address']} was not found."
                    )
        
        # Overwrite with given values
        for value in values:
            if value in self.requirements:
                self.requirements[value]['value'] = values[value]
        self._setVariables()

    def _setVariables(self):
        for req in self.requirements:
            if hasattr(self, req) and self.first_var_run:
                raise Exception(self.name + ' already has attribute ' + str(req))
            else:
                setattr(self, req, self.requirements[req]['value'])
        self.first_var_run = False

    def CheckRequirements(self):
        Reqs_Met = True
        UnmetReqs = []
        for req in self.requirements:
            # print (req)
            if self.requirements[req]['value'] == '':
                UnmetReqs.append(req)
                Reqs_Met = False

        if not Reqs_Met:
            raise Exception(f'Requirements {UnmetReqs} where not met.')

    def GetDetails(self):
        details = {}
        for req in self.requirements:
            details[req] = self.requirements[req]['value']
        return details

    def DoEproc(self, device, method, details):
        procname = 'eproc_' + device + '_' + method
        p_uuid = str(uuid.uuid4())
        self.apparatus.LogProc('start', procname, p_uuid, reqs=details)

        try:
            e_log = self.executor.execute(
                [[{'devices': device, 'procedure': method, 'details': details}]]
            )
            
        finally:  # makes sure depthindex is decreased on error
            end_time = time.time()
            self.apparatus.LogProc('end', procname, p_uuid, log=e_log)

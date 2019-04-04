# APE framework.  Procedure may not be necessary
from ProcExec import ProcExec
import Procedures
from Interface_Node import Interface_Node
from multiprocessing import Process
import threading
from Appa import Appa


# Import the procedure sets that are needed

# Import other libraries
import FlexPrinterApparatus  # This is specific to the Flex Printer at AFRL
import XlineTPGen as TPGen  # Toolpath generator


def StartAppa(A2I_address, A2PE_address):
    # Create apparatus and executor
    MyAppa = Appa(A2I_address, A2PE_address)
    MyApparatus = MyAppa.apparatus
    # ____FLexPrinterApparatus____#
    # Set up a basic description of the system that is later used to create an
    # apparatus specific to the Flex Printer at AFRL
    
    materials = [{'AgPMMA': 'ZZ1'}]
    # These are other tools that can be added in. Comment out the ones not used.
    tools = []
    # tools.append({'name': 'TProbe', 'axis': 'ZZ2', 'type': 'Keyence_GT2_A3200'})
    # tools.append({'name': 'camera', 'axis': 'ZZ4', 'type': 'IDS_ueye'})
    
    FlexPrinterApparatus.Build_FlexPrinter(materials, tools, MyApparatus)
    mat0 = [list(materials[n])[0] for n in range(len(materials))][0]
    # Define the rest of the apparatus
    MyApparatus['devices']['n' + mat0]['descriptors'].append(mat0)
    MyApparatus['devices']['n' + mat0]['trace_height'] = 0.1
    MyApparatus['devices']['n' + mat0]['trace_width'] = 0.2
    MyApparatus['devices']['aeropump0']['descriptors'].append(mat0)
    MyApparatus['devices']['gantry']['default']['speed'] = 40
    MyApparatus['devices']['gantry']['n' + mat0]['speed'] = 0.3  # Calibration is on so this is overwritten
    MyApparatus['devices']['aeropump0']['pumpon_time'] = 1  # Calibration is on so this is overwritten
    MyApparatus['devices']['aeropump0']['mid_time'] = 1
    MyApparatus['devices']['aeropump0']['pumpoff_time'] = 0
    MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.3
    MyApparatus['devices']['aeropump0']['pressure'] = 155
    MyApparatus['devices']['pump0']['COM'] = 9

    MyApparatus['information']['materials'][mat0]['density'] = 1.84
    MyApparatus['information']['toolpaths'] = {}
    MyApparatus['information']['toolpaths']['generator'] = TPGen.GenerateToolpath
    MyApparatus['information']['toolpaths']['parameters'] = TPGen.Make_TPGen_Data(mat0)
    MyApparatus['information']['toolpaths']['toolpath'] = [0]
    MyApparatus['information']['ink calibration']['time'] = 30

    for device in MyApparatus['devices']:
        if MyApparatus['devices'][device]['addresstype'] == 'pointer':
            MyApparatus['devices'][device]['addresstype'] = 'zmqNode'
            MyApparatus['devices'][device]['address'] = 'procexec'

    MyApparatus['devices']['User'] = {'type': 'User_Consol',
               'descriptors': ['Interface'],
               'addresstype': 'zmqNode',
               'address': 'User'}

    return MyApparatus

def StartProcExec(PE2I_address, PE2A_address):
    
    MyProcExec = ProcExec(PE2I_address, PE2A_address)
    MyApparatus = MyProcExec.apparatus
    MyExecutor = MyProcExec.executor
    
    # Connect to all the devices in the setup
    

    MyProcExec.proclist.append({'procedure': Procedures.User_FlexPrinter_Alignments_Align(MyApparatus, MyExecutor),
                           'requirements': {'primenoz': 'n' + 'AgPMMA'}})
    '''
    MyProcExec.proclist.append({'procedure': Procedures.User_InkCal_Calibrate(MyApparatus, MyExecutor),
                           'requirements': {'material': 'AgPMMA'}})
    MyProcExec.proclist.append({'procedure': Procedures.Toolpath_Generate(MyApparatus, MyExecutor),
                           'requirements': {}})
    PrintTP = Procedures.Toolpath_Print(MyApparatus, MyExecutor)
    PrintTP.requirements['toolpath']['address'] = ['information', 'toolpaths', 'toolpath']
    MyProcExec.proclist.append({'procedure': PrintTP,
                           'requirements': {}})
    '''
    return MyProcExec
    
if __name__ == '__main__':
    # Determine the addresses needed
    port = 5565
    I2A_address = "tcp://127.0.0.1:"+str(port)
    I2PE_address = "tcp://127.0.0.1:"+str(port+1)
    A2PE_address = "tcp://127.0.0.1:"+str(port+2)
    TestCase = 1
    if TestCase == 1:
        # Spin up the other processes
        proc_Appa = Process(target=StartAppa, args=(I2A_address,A2PE_address,))
        proc_Appa.start()
        proc_ProcExec = Process(target=StartProcExec, args=(I2PE_address, A2PE_address,))
        proc_ProcExec.start()
        # Start the Interface
        banana = Interface_Node(I2A_address, I2PE_address)
        print(banana.apparatus.getValue(['information', 'calibrationfile']))
        banana.apparatus.Connect_All(simulation=True)
        threading.Timer(20.0, banana.DoProclist).start()
        waitTime = 40.0
        threading.Timer(waitTime, banana.sendCloseAll).start()
        threading.Timer(waitTime+0.1, banana.node.close).start()
        threading.Timer(waitTime+0.2, proc_Appa.join).start()
        threading.Timer(waitTime+0.3, proc_ProcExec.join).start()
    elif TestCase == 2:
        test = StartAppa(appa_address)
    elif TestCase == 3:
        test = StartProcExec(appa_address, procexec_address)        


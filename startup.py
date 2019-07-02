from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow
from MultiProcess.Appa import Appa
from MultiProcess.ProcExec import ProcExec
import sys
import multiprocessing
from multiprocessing import Process
from MultiProcess.zmqNode import zmqNode
from GUI import GUI_Node


class StartUp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # sets up the window with 4 push buttons
        self.setWindowTitle('Start Up Window')
        self.startAPEbtn = QPushButton('Start APE', self)
        self.startAPEbtn.move(0, 10)
        self.startAPEbtn.clicked.connect(self.startAPE)
        self.closeAPEbtn = QPushButton('Close APE', self)
        self.closeAPEbtn.move(0, 40)
        self.closeAPEbtn.setEnabled(False)
        self.closeAPEbtn.clicked.connect(self.closeAPE)
        self.startGUIbtn = QPushButton('Start GUI', self)
        self.startGUIbtn.move(100, 10)
        self.startGUIbtn.setEnabled(False)
        self.startGUIbtn.clicked.connect(self.startGUI)
        self.closeGUIbtn = QPushButton('Close GUI', self)
        self.closeGUIbtn.move(100, 40)
        self.closeGUIbtn.setEnabled(False)
        self.closeGUIbtn.clicked.connect(self.closeGUI)
        self.closeLauncherbtn = QPushButton('Close Launcher', self)
        self.closeLauncherbtn.move(50, 70)
        self.closeLauncherbtn.clicked.connect(self.closeLauncher)
        # creates the node and start logging
        self.node = zmqNode('launcher')
        self.node.logging = True
        self.node.start_listening()
        # Set addresses
        port = 5575
        self.L2A_address = "tcp://127.0.0.1:" + str(port)
        self.L2PE_address = "tcp://127.0.0.1:" + str(port + 1)
        self.L2G_address = "tcp://127.0.0.1:" + str(port + 2)
        self.A2PE_address = "tcp://127.0.0.1:" + str(port + 3)
        self.A2G_address = "tcp://127.0.0.1:" + str(port + 4)
        self.G2PE_address = "tcp://127.0.0.1:" + str(port + 5)
        self.connect2A()
        self.connect2PE()
        self.connect2G()
        # Process holders
        self.proc_Appa = ''
        self.proc_ProcExec = ''

    # connects to all three of the nodes as server
    # server MUST be true for all of these
    def connect2A(self):
        self.node.connect('appa', self.L2A_address, server=True)

    def connect2PE(self):
        self.node.connect('procexec', self.L2PE_address, server=True)

    def connect2G(self):
        self.node.connect('gui', self.L2G_address, server=True)

    # closes all connections when APE is closed
    def sendCloseAll(self):

        for connection in self.node.connections:
            self.sendClose(connection)
        print('Close commands sent')

    def sendClose(self, connection):
        message = {'subject': 'close'}
        self.node.send(connection, message)

    # starts the AP and E portion of the program

    def startAPE(self):
        # Experiment_MultiProcess.Start(self)
        # uncomment to show the communication between launcher and appa
        # print(self.apparatus.getValue(['information', 'calibrationfile']))
        self.proc_Appa = Process(
            target=Appa, args=(self.L2A_address, self.A2PE_address, self.A2G_address)
        )
        self.proc_Appa.start()
        self.proc_ProcExec = Process(
            target=ProcExec,
            args=(self.L2PE_address, self.A2PE_address, self.G2PE_address),
        )
        self.proc_ProcExec.start()
        print('start APE')
        self.closeAPEbtn.setEnabled(True)
        self.startAPEbtn.setEnabled(False)
        self.startGUIbtn.setEnabled(True)
        self.closeLauncherbtn.setEnabled(False)

    # closes the AP and E portion of the program
    def closeAPE(self):
        # disconnects the launcher
        self.sendClose('appa')
        self.proc_Appa.join()
        self.sendClose('procexec')
        self.proc_ProcExec.join()
        print('close APE')
        self.closeAPEbtn.setEnabled(False)
        self.startAPEbtn.setEnabled(True)
        self.startGUIbtn.setEnabled(False)
        self.closeLauncherbtn.setEnabled(True)

    # starts the User Interface
    def startGUI(self):
        self.proc_GUI = Process(
            target=GUI_Node.GUI_Node,
            args=(self.L2G_address, self.A2G_address, self.G2PE_address),
        )
        self.proc_GUI.start()
        print('start GUI')
        self.closeAPEbtn.setEnabled(False)
        self.startAPEbtn.setEnabled(False)
        self.startGUIbtn.setEnabled(False)
        self.closeGUIbtn.setEnabled(True)
        self.closeLauncherbtn.setEnabled(False)

    # closes the User Interface
    def closeGUI(self):
        self.sendClose('gui')
        self.proc_GUI.join()
        print('close GUI')
        self.closeAPEbtn.setEnabled(True)
        self.startAPEbtn.setEnabled(False)
        self.closeGUIbtn.setEnabled(False)
        self.startGUIbtn.setEnabled(True)

    def closeLauncher(self):
        self.node.close()
        self.closeAPEbtn.setEnabled(False)
        self.startAPEbtn.setEnabled(False)
        self.closeGUIbtn.setEnabled(False)
        self.startGUIbtn.setEnabled(False)


if __name__ == '__main__':
    # this is important to avoid forking in UNIX operating systems
    multiprocessing.set_start_method('spawn')
    # make a QApplication to run pyqt5
    app = QApplication(sys.argv)
    # instance of the new class
    startUp = StartUp()
    # target is the GUI from the class
    startUp.node.target = startUp
    # shows the GUI
    startUp.show()
    # exiting function
    sys.exit(app.exec_())

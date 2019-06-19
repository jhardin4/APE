#add button to refresh eproc instead of refreshing in connect all
#def creatEproc(device, method) 
# class eproc(Procedure)
#Prepare empty
#Do eproc.. look at doeproc in apparatus sekf.requirements = reqs from copied procedure
#neweproc= eproc(apparatus,executor)
#returnneweproc

import sys
from GUI.APE1 import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTreeWidgetItem, QTreeWidgetItemIterator, QTableWidgetItem
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QWidget
from Core import Apparatus, Executor
import Procedures
import GUI.TemplateGUIs as tGUIs

class APEGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(APEGUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.blankapp.clicked.connect(self.refresh)
        self.ui.tempapp.clicked.connect(self.temp)
        self.ui.copybtn.clicked.connect(self.enterreq)
        self.ui.fandrbutton.clicked.connect(self.fandr)
        self.ui.addbtn.clicked.connect(self.add)
        self.ui.removebtn.clicked.connect(self.remove)
        self.ui.treeWidget.itemChanged.connect(self.save)
        self.ui.itable.itemChanged.connect(self.update)
        self.ui.saveasbtn.clicked.connect(self.saveas)
        self.ui.abtn.clicked.connect(self.addproc)
        self.ui.rbtn.clicked.connect(self.removeproc)
        self.ui.pbox.itemClicked.connect(self.getreq1)
        self.ui.upbtn.clicked.connect(self.up)
        self.ui.downbtn.clicked.connect(self.down)
        self.ui.rbox.itemChanged.connect(self.updaterbox)
        self.ui.RunListbtn.clicked.connect(self.runProcList)
        self.ui.runCurrentbtn.clicked.connect(self.runproc)
        self.ui.pbox_2.itemClicked.connect(self.getreq2)
        self.ui.connectbtn.clicked.connect(self.connectall)
        self.ui.disconnectbtn.clicked.connect(self.disconnectall)
        self.ui.showeproc.clicked.connect(self.eprocbox)
        self.apparatus = ''
        self.executor = ''
        self.appImage = {}
        
    # --------------------- Apparatus Tab ---------------------     
    
    # finds the given value and replaces all instances with the new value    
    def fandr(self):
        #finds from findbox and replaces with replacebox
        pathn = self.ui.findbox.text()
        value = self.ui.replacebox.text()
        # creates a list of all items with the given value
        parent = self.ui.treeWidget.findItems(pathn, Qt.MatchExactly | Qt.MatchRecursive)
        # if there are multiple matching children this runs each separately looking for a match
        for t in range(len(parent)):
            # the final child is used and is what needs replaced
            item = parent[t]
            # replaces the pathname value with the given value
            item.setText(0, value)
        # will need to send these values and update the appa
        # empties the find and replace boxes
        self.ui.findbox.setText('')
        self.ui.replacebox.setText('')
    
    # adds a child to the selected item
    def add(self):
        # gets selected item and makes a child
        parent = self.ui.treeWidget.currentItem()
        child = QtWidgets.QTreeWidgetItem()
        # adds to tree, expands, makes the child editable, and adds a checkbox
        parent.addChild(child)
        parent.setExpanded(True)
        if child.child(0) is None:
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            child.setCheckState(0, Qt.Unchecked)
        # this should add a value in the appa node
        
    # removes selected item from qtreewidget
    def remove(self):
        # gets selected item and number of children
        item = self.ui.treeWidget.currentItem()
        parent = item.parent()
        # if item is not top level item, the item is removed
        if parent != None:
                parent.removeChild(item)
        # this will need to remove the appa node's value
    
    # if an item is changed this will update the apparatus to match the qtreewidget
    def save(self):
        child = self.ui.treeWidget.currentItem()
        # if a selected item exists
        if child: 
            # checks to see if the item is checked
            # if is check it will update the itable if needed
            if child.checkState(0) == Qt.Checked:
                self.fillitable(child)
            # if it is not checked it will remove it from the itable if present
            else:
                self.removefromitable(child)
        # can only update template as the user goes
        # blank apparatus must be saved as once
        if self.apptype == 'template':
            pathn = []
            # if check box is checked, it will add it to the table
            if child: 
                # magical code that finds the items string
                Child = child.text(0)
                # prints the magical string that took me 15 hours
                # makes a list of the parents in reverse order
                while (child.parent()) != None:    
                    getParent = child.parent()
                    Parent = getParent.text(0)
                    child = getParent
                    pathn.insert(0,Parent)
                # updates the apparatus using the pathname and new value
                # Apparatus.setValue(self.MyApparatus, pathn, Child)
                # sends the value to appa node / updates real apparatus
                self.apparatus.setValue(pathn, Child)
     
    # runs everytime the apparatus type is changed
    # clears all tables and lists
    def startover(self):
        # clears tree and table widget for new apparatus
        self.ui.treeWidget.clear()
        row = self.ui.itable.rowCount()
        # if the table widget has contents, this will clear them
        if row != 0:
            for r in range(row + 1):
                self.ui.itable.removeRow(row-r)
        # clears out all of the procedures
        self.ui.pbox.clear()
        # gets all procedure from folder
        #self.procedurebox()

        self.appImage = self.apparatus.serialClone()

    def refresh(self):
        #How to pull old Appa so python doesnt crash
        
        # creates a blank apparatus
        self.apptype = 'blank'
        self.startover()
        # takes the structure of a blank apparatus and puts it in the qtreewidget
        for key, value in self.appImage.items():
            if type(value) is dict:
                keyitem = self.fillchildren(key, value)
            else:
                keyitem = QtWidgets.QTreeWidgetItem([key])
            self.ui.treeWidget.addTopLevelItem(keyitem)
    
    # fill in the children of the tree using reccursion
    def fillchildren(self, key, value):
        keyitem = QtWidgets.QTreeWidgetItem([key])
        if type(value) is dict:
            for k, v in value.items():
                keyitem.addChild(self.fillchildren(k,v))
        else:
            valueitem = QtWidgets.QTreeWidgetItem([str(value)])
            keyitem.addChild(valueitem)
        return keyitem

    def new_item(self, parent, text, val=None):
        # creates a new option
        child = QTreeWidgetItem([text])
        # fills the option with the next value
        self.fill_item(child, val)
        # assigns the option to the parent variable
        parent.addChild(child)
        # sets the options to be close
        child.setExpanded(False)

    def fill_item(self, item, value):
        # if this is the last value in that string, go to next
        if value is None: 
            # we only want to be able to edit the last value
            # the set to edit function is placed here
            item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            if item != None:
                item.setCheckState(0, Qt.Unchecked)
            return
            
        # the value contains a dictionary
        elif isinstance(value, dict):
            for key, val in sorted(value.items()):
                # add a new item for each key in the dictionary
                self.new_item(item, key, val)
        # the value is a tuple
        elif isinstance(value, (list, tuple)):
            # for every value in the tuple, make an item from the 
            #item, text, and value
            for val in value:
                text = (str(val) if not isinstance(val, (dict, list, tuple))
                        else '[%s]' % type(val).__name__)
                self.new_item(item, text, val) 
        # if the value is none of the other options add it as a string
        else:
            self.new_item(item, str(value))

    def temp(self, simulation = True):
        # Clear tree widget
        self.startover()
        # Get list of templates
        files = dir(tGUIs)
        GUIlist = []
        for name in files:
            if '__' not in name:
                GUIlist.append(name)
        # Ask user to select template
        message = 'Name of the Template to be used.'
        d = 0
        options = GUIlist
        tName, ok = QInputDialog.getItem(None, 'Input', message, options, d, False)
        try:
            tGUI = getattr(tGUIs, tName)
            args, kwargs = tGUI()
        except AttributeError:
            message = 'That template was not found.'
            tName, ok = QInputDialog.getText(None, 'Input', message, QLineEdit.Normal, default)
        self.apparatus.applyTemplate(tName, args=args, kwargs=kwargs)
        self.appImage = self.apparatus.serialClone()
        # puts the apparatus in the qtreewidget

                 
        # provides access to the top level items using recursive functions
        self.fill_item(self.ui.treeWidget.invisibleRootItem(), self.appImage)
        # list of things that need checked
        ithings = []
        
        # goes through the list of preselected and sets their boxes as checked
        for k in range(len(ithings)):
            # finds these in the qtreewidget
            IT = self.ui.treeWidget.findItems(ithings[k][len(ithings[k])-1], Qt.MatchExactly | Qt.MatchRecursive)
            for l in range(len(IT)):
                item = IT[l]
                # sets the tree 
                if item.parent().text(0) == ithings[k][len(ithings[k])-2]:
                    child = item.child(0)
                    child.setCheckState(0, Qt.Checked)
                    # checks to see if the values go into the important qtablewidget
                    self.fillitable(child)
        # gets the elementary procedures from the apparatus and puts them into the procedure qlistwidget
        # self.eprocbox()
  
    # fills the table with checked values
    def fillitable(self, item = ''):
        # grab current item and get pathname
        if item.checkState(0) == Qt.Checked:
            value = item
            # gets the pathname of the value
            path = ''
            while item.parent() != None:
                parent = item.parent()
                path = parent.text(0) + ' ' + path
                item = parent
            # checks to see if this value already exists in the table
            if len(self.ui.itable.findItems(path, Qt.MatchExactly | Qt.MatchRecursive)) is 0:
                # if it is not already in the table, it adds it to the bottom
                k = self.ui.itable.rowCount()
                self.ui.itable.insertRow(k)
                self.ui.itable.setItem(k, 1, QTableWidgetItem(value.text(0)))
                self.ui.itable.setItem(k, 0, QTableWidgetItem(path))
                newitem = self.ui.itable.item(k, 0)
                # used to make the table fit the pathname and values
                self.ui.itable.resizeColumnsToContents()
                # makes the keys not editable
                newitem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            else:
                # if already exists in itable and just needs updated, this will update
                ibox = self.ui.itable.findItems(path, Qt.MatchExactly | Qt.MatchRecursive)[0]
                self.ui.itable.setItem(ibox.row(), 1, QTableWidgetItem(value.text(0)))
    
    # if a qtreewidgetitems checkbox is unchecked, it will be removed from the qtablewidget
    # to do this the item must be selected when the check box is changed
    # this is because there is not signal for a check box in a qtreewidget
    def removefromitable(self, item = ''):
        path = ''
        # loop creates the pathname of the selected item
        while item.parent() != None:
            parent = item.parent()
            path = parent.text(0) + ' ' + path
            item = parent
        # finds items in the qtablewidget of important values that match the pathname
        ibox = self.ui.itable.findItems(path, Qt.MatchExactly | Qt.MatchRecursive)
        # if there is a match in the qtablewidget, this removes the row of the matched qtablewidgetitem
        if not len(ibox) is 0:
            self.ui.itable.removeRow(ibox[0].row())
    
    # updates the qtreewidget and apparatus if the value in the qtablewidget (important valeus) is changed    
    def update(self):
        newvalue = self.ui.itable.currentItem()
        # this eliminates going through the process during start up
        # otherwise it will update every value in the qtreewidget which is not needed
        if newvalue != None:
            row = self.ui.itable.currentRow()
            # gets pathname from left column
            newkey = self.ui.itable.item(row, 0)
            path = newkey.text()
            pathn = path.split(' ')
            # removes last item of the pathname 
            pathn.pop()
            if newvalue != None:   
                # this has to be 1 because of how pathn is created
                key = pathn[len(pathn)-1]
                # finds item in the qtreewidget with the same pathname
                listnewv = self.ui.treeWidget.findItems(key, Qt.MatchExactly | Qt.MatchRecursive)
                # from this list of pathnames inserts the new value into the apparatus
                for k in range(len(listnewv)):
                    if listnewv[k].parent().text(0) == pathn[len(pathn)-2]:
                        text = newvalue.text()
                        # places the new value into the correct place in the qtreewidget
                        listnewv[k].child(0).setText(0, text)
                        # sets the new value in the apparatus and appa node
                        Apparatus.setValue(self.MyApparatus, pathn, text)
                        self.apparatus.setValue(pathn, text)
                        
    # for the copy to procedure requirements button on apparatus tab
    def enterreq(self):
        # gets the current item of the qtreewidget
        child = self.ui.treeWidget.currentItem()
        # gets text of child
        Child = child.text(0)
        # inserts the text into the selected qtablewidget item (requirement box)
        r = self.ui.rbox.currentRow()
        self.ui.rbox.setItem(r, 1, QTableWidgetItem(Child))
        
    # saves the apparatus as the name in the text box
    def saveas(self):
        # this will build the blank apparatus
        # not needed for template apparatus because it already has a structure
        if self.apptype == 'blank':
            for k in range(self.ui.treeWidget.topLevelItemCount()):
                parent = self.ui.treeWidget.topLevelItem(k)
                pathn = []
                i = 0
                if (parent.child(0)) != None:
                    while (parent.child(0)) != None:
                        child = parent.child(0)
                        Parent = parent.text(0)
                        # makes a list of the parents in reverse order
                        #stops when it reaches the bottom item (no child)
                        # inserts child at the end of the array
                        pathn.insert(i, Parent)
                        parent = child
                        i = i + 1
                    pathn.insert(i, parent.text(0))
                    # sets Child equal to it's own value for setValue function
                    Child = child.text(0)
                    # updates the apparatus
                    Apparatus.setValue(self.MyApparatus, pathn, Child)
                    # needs to update the appa node
        # gets the filename from the textbox and sets the apparatus to that name
        filename = self.ui.fnamebox.text()
        filename = self.MyApparatus
        # logs the apparatus as a JSON
        Apparatus.logApparatus(filename)
        
    def eprocbox(self):
        #calls on interface using the procexec as the address
        #self.ui.pbox.clear()
        self.epl = self.executor.getDevices('procexec') 
        
        #for loop that goes through each device and eproc for that device and displays it in the procedure tab
        
        for m in range(len(self.epl)):  
            self.eproclist=self.executor.getEprocs(str(self.epl[m]), 'procexec')
            for n in range(len(self.eproclist)):
                self.ui.pbox.addItem(self.epl[m] + ' ' + self.eproclist[n])
                
    def connectall(self):
        self.apparatus.Connect_All(simulation = self.ui.simBox.isChecked())

        for device in self.appImage['devices']:
            self.appImage['devices'][device]['Connected'] = 'True'
        
        self.ui.treeWidget.clear()
         # takes the structure of a blank apparatus and puts it in the qtreewidget
        for key, value in self.appImage.items():
            if type(value) is dict:
                keyitem = self.fillchildren(key, value)
            else:
                keyitem = QtWidgets.QTreeWidgetItem([key])
            self.ui.treeWidget.addTopLevelItem(keyitem)
    
    def disconnectall(self):
        self.apparatus.Disconnect_All()
        for device in self.appImage['devices']:
            self.appImage['devices'][device]['Connected'] = 'False'
        
        self.ui.treeWidget.clear()
         # takes the structure of a blank apparatus and puts it in the qtreewidget
        for key, value in self.appImage.items():
            if type(value) is dict:
                keyitem = self.fillchildren(key, value)
            else:
                keyitem = QtWidgets.QTreeWidgetItem([key])
            self.ui.treeWidget.addTopLevelItem(keyitem)
    # --------------------- Procedures Tab ---------------------  
    
    # imports the filenames from the procedures folder
    def procedurebox(self):
        #print(self.apparatus.serialClone()['proclog'])
        procs = self.apparatus.serialClone()['proclog']
        for i, proc in enumerate(procs):
            self.ui.pbox.insertItem(i, proc[1]['name'])
        
        
        #only shows used not unused
        
        
        #for p in range(len(self.apparatus.proclist)):
            #self.ui.pbox.insertItem(p, self.apparatus.proclist[p])
            #self.proclist = []
     

     
    # gets eprocs from apparatus and puts them into the qlistwidget
    # this does not work anymore after we added multiprocessing because 
    # of the connect all function's change
    # once the eprocs populate in the apparatus this should work 
    
  
    def addproc(self):
        newp = self.ui.pbox.currentItem()
        self.ui.pbox_2.addItem(newp.text())
        # adds to proclist corresponding to the row of the pbox_2
        # this is where code needs put to save the procedure and requirements in the order that 
        # it is added to pbox_2. This is how you will want to save it in the proclist. 
        # will need to have a requirements {} that extracts from the rbox
        requirements = {}
        for row in range(self.ui.rbox.rowCount()):
            rname = self.ui.rbox.item(row, 0).text()
            rvalue = self.ui.rbox.item(row, 1).text()
            print(rname + '   ' + rvalue)
            requirements[rname] = rvalue
        # self.proclist.append({'procedure': getattr(Procedures, newp.text())(self.MyApparatus, self.MyExecutor),
                                # 'requirements': requirements})
        if newp.text() in dir(Procedures):
            self.proclist.append({'procedure': getattr(Procedures, newp.text())(self.MyApparatus, self.MyExecutor),
                                  'requirements': requirements})
    
    # deletes the selected procedure from the proclist    
    def removeproc(self):
        row = self.ui.pbox_2.currentRow()
        self.ui.pbox_2.takeItem(row)
        
        #self.proclist.pop(row)
        
    # used tp update rbox    
    def getreq1(self):
        self.getreq(self.ui.rbox, self.ui.pbox)
    
    # used to update rboc_2
    def getreq2(self):
        self.getreq(self.ui.rbox_2, self.ui.pbox_2)  
    
    # gets the requirements from the selected procedure
    def getreq(self, rbox, pbox):
        row = rbox.rowCount()
        # clears out qtablewidgets contents
        if row != 0:
            for r in range(row +1 ):
                rbox.removeRow(row-r)
        name = pbox.currentItem().text()
        # locates the selected procedure in the folder
        if name in dir(Procedures):
            # makes an instance of the selected procedure
            f = getattr(Procedures, name)(self.MyApparatus, Executor)
            # gets the requirements
            reqs = f.requirements
            i = 0
            # places the requirements into the qtablewidget
            for key in reqs:
                rbox.insertRow(i)
                rbox.setItem(i, 0, QTableWidgetItem(key))
                # must set this to '' if you plan on adding text later
                rbox.setItem(i, 1, QTableWidgetItem(''))
                # must be able to select for the apparatus copy to requirements button to work
                rbox.item(i,0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                value = reqs[key]['value']
                # if the value is empty, red --> otherwise, green
                if value == '':
                    rbox.item(i, 1).setBackground(Qt.red)
                else:
                    rbox.item(i, 0).setBackground(Qt.green)
            i = i + 1
        else:
            dname = name.split(' ')[0]
            ename = name.split(' ')[1]
            
            self.reqs = self.executor.getRequirements(dname, ename, 'procexec')
            
            #reqs = list(self.epl[dname]['Address'].requirements[ename].keys())
           
            t = 0
            for g in range(len(self.reqs)):
                rbox.insertRow(t)
                rbox.setItem(t, 0, QTableWidgetItem(self.reqs[g]))
                rbox.setItem(t, 1, QTableWidgetItem(''))
                rbox.item(t, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                t = t + 1
            # reqs = d[device]['address']['requirements'][method]
        
            
    # moves the selected procedure up one row
    def up(self):
        # takes current row
        currentRow = self.ui.pbox_2.currentRow()
        # removes item from the list
        currentItem = self.ui.pbox_2.takeItem(currentRow)
        # inserts the item back into the list, one row up
        self.ui.pbox_2.insertItem(currentRow - 1, currentItem)
        # move the item in self.proclist also
        
    # moves the selected procedure down one row 
    def down(self):
        # takes current row
        currentRow = self.ui.pbox_2.currentRow()
        # removes item from the list
        currentItem = self.ui.pbox_2.takeItem(currentRow)
        # inserts the item back into the list, one row down
        self.ui.pbox_2.insertItem(currentRow + 1, currentItem)
        # move the item in self.proclist also
        
    # when a new item is selected the requirements are changed to match that procedure
    def updaterbox(self, value = ''):
        citem = self.ui.rbox.currentItem()
        r = self.ui.rbox.currentRow()
        self.ui.rbox.resizeColumnsToContents()
        name = self.ui.pbox.currentItem().text()
        if citem != None: 
            value = citem.text()
            if value == '':
                self.ui.rbox.item(r, 1).setBackground(Qt.red)
            else:
                self.ui.rbox.item(r, 1).setBackground(Qt.green)
            # update the requirements in the executer
            # gets the requirements
            req = self.ui.rbox.itemAt(r,0)
            dname = name.split(' ')[0]
            ename = name.split(' ')[1]
            #commented so code will run
            #self.executor.setRequirements(dname, ename, req, value, 'procexec')
                
                
        
                
    # when a procedure from the proclist is selected, the corresponding requirements are visible
    def fillrbox_2(self):
        # gets the corresponding requirements from the proclist
        pRow = self.ui.pbox_2.currentRow()
        #proc = self.proclist[pRow]
        #requirement = proc['requirements']

    # runs the selected procedure from pbox_2
    def runproc(self):
        # gets the current row to find the desired item in the proclist
        pRow = self.ui.pbox_2.currentRow()
        proc = self.proclist[pRow]
        # extract the procedure and requirements
        procedure = proc['procedure']
        requirements = proc['requirements']
        # send to the gui node to be executed
        self.node.Do(procedure, requirements)

    # sends proc list to gui node to send to procexec
    def runProcList(self):
        self.node.DoProclist()
            
# -------------- Functions for the startup window to start and close --------------

# allows for the start up window to set up this GUI
def Start(self):
    global GUIwindow
    GUIwindow = APEGUI()
    GUIwindow.show()

# closes the GUI from the start up window   
def Close(self):
    GUIwindow.close()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUIwindow = APEGUI()
    GUIwindow.show()
    sys.exit(app.exec_())
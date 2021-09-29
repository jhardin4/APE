"""
This file is an example of how to set up and use the ROSEDA_getResults 
Procedure.  All of the cases below use files fed directly by the users. 
"""

import Core
import Procedures
import json
import os
from shutil import copyfile

MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()
MyApparatus.executor = MyExecutor

# This is a simple example so I am manually setting up the devices rather than
# using and apparatus builder
kfile = "/home/james_hardin_11/Desktop/jhardin-repos-1sud/Keys/rxms-roseda-eb7721e580d1.json"
MyApparatus.add_device_entry("system", "System")
MyApparatus.add_device_entry("user", "User_Consol")
# MyApparatus.add_device_entry("GCP", "GoogleCloudPlatform", {"key_file": kfile})

# Connect to all the devices in the setup. This monolith does not need to be
# run in simulation
MyApparatus.Connect_All(simulation=False)

# Renaming some elements for the variable explorer
information = MyApparatus["information"]

# Create Procedure
getResults = Procedures.ROSEDA_getResults(MyApparatus, MyExecutor)
# Locations of example files
example_proclog_path = r"Examples/ROSEDA/1599456073proclog.json"
example_runtic_path = r"Examples/ROSEDA/1599456073Run_Ticket.json"
example_image_path = r"Examples/ROSEDA/HDS2_sample10.png"
# Making copies in relevant places
proclog_path = os.path.join("Logs", os.path.split(example_proclog_path)[1])
image_path = os.path.join("Data", os.path.split(example_image_path)[1])
runtic_path = os.path.split(example_runtic_path)[1].replace("Run_Ticket", "RunTicket")

copyfile(example_proclog_path, proclog_path)
copyfile(example_runtic_path, runtic_path)
copyfile(example_image_path, image_path)

# Do the experiment
details = {}
details["bucket"] = "rxms-roseda-data-jhardin"
details["proclog"] = proclog_path
details["image"] = image_path
details["run_ticket"] = runtic_path

getResults.Do(details)
# Clean up the fake run tickets
os.remove(runtic_path)
MyApparatus.Disconnect_All()
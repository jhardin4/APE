# APE framework.
import Core

# Create an empty Apparatus
MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()

# Create an entry for the pump
required_pump_info = {}
# Tell the Apparatus what type of device it is.  This has to be exactly correct
# because this is the name of the Device used.
required_pump_info['type'] = 'Nordson_UltimusV'

# Currently, this is always 'pointer' but the goal is to have others ways of
# connecting to devices.
required_pump_info['addresstype'] = 'pointer'

# Furthermore, any other information for connecting to the device needs to be 
# places in this structure.
required_pump_info['COM'] = 5

# Once that is set, we can add a device entry in the Apparatus
MyApparatus['devices']['mypump'] = required_pump_info



# This will attempt to connect to all devices in the Apparatus but there is
# only one in this case.  It also registers them with the Executor. This is
# will also set them all to a designated simulation state.
MyApparatus.Connect_All(MyExecutor, simulation=True)

# Example 1 can be completes from here using the following line:
# mypump = MyApparatus['devices']['mypump']['address']
# To take advantage of the tracking/organization/abstraction capacities of APE
# it is necessary to manage the devices through procedures.

# For this demonstration, we will simply grab elemental procedures from
# MyApparatus['eproclist'] using a built-in search method.
# It is important to note that Connect and Disconnect are handled by the
# Apparatus methods rather than device ones here.
mypump_On = MyApparatus.GetEproc('mypump', 'On')
mypump_Off = MyApparatus.GetEproc('mypump', 'Off')

# Procedures don't do anything untill their Do method is called.  Any
# necessary information is passed along at this time.
mypump_On.Do()
mypump_Off.Do()

# Now that you are done, disconnect everything.
MyApparatus.Disconnect_All()

print('''
      Look in the Logs folder for three files.
      One is the log of what was done.
      There are two snapshots of the Apparatus
      as well. One at the start and one at the
      end.
      ''')

print('''
      Also explore the MyApparatus object in
      the variable explorer of your coding
      program.  Specifically, the proclog
      gives context to the information it
      contains.
      ''')

print('''
      ..and yes, this is a completely absurd
      way of turning on and off a pump.
      Move on to Example 3 for this to make
      more sense.
      ''')

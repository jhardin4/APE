# This is the main file that calls all of the other elements of APE

import Devices

mypump = Devices.Nordson_UltimusV('mypump')

# This is set to run in simulation mode for the sake of testing. If you want
# this to actually run, you will need to change it to False or comment out this
# line.
mypump.simulation = True

# As long as we are using methods of the Device that are setup as elemental
# procedures then they will return a string for logging.  We can then capture
# that string for overall loggin purposes.
log = ''

# COM is the serial connection to the pump
# pyserial is required for this to run so make sure that it is installed
log += mypump.Connect(COM=5)
log += mypump.On()
log += mypump.Off()
log += mypump.Disconnect()

print('And now the log...')
print(log)

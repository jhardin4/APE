# APE framework.
import Core
import Procedures

# Create an empty Apparatus
MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()

# Let's assume we habe three pumps drive extrusion of red, green, and blue.

# We will start with a generic pump builder.
COM_list = [2, 3, 10]
material_list = ['red', 'green', 'blue']
for n in range(3):
    # We can quickly handle the elements described in Example 2
    MyApparatus['devices']['mypump' + str(n)] = {
            'type': 'Nordson_UltimusV',
            'addresstype': 'pointer',
            'COM': COM_list[n]
            }

    # But we can also add further descriptions using descriptor tags.  In this
    # case, we are adding and explicit one but some descriptors are implicit.
    MyApparatus['devices']['mypump' + str(n)]['descriptors'] = [material_list[n]]

# Almost all meaningful Apparatus structures will require some reference to
# the computer that it is on for accessing timing and such.  In APE, this is
# the 'system' Device.
    MyApparatus['devices']['system'] = {
            'type': 'System',
            'addresstype': 'pointer',
            }

# We connect, as we did in example 2
MyApparatus.Connect_All(MyExecutor, simulation=True)

# Instead of using elemental procedures, we use more abstract procedures for
# pumps but... how do we know whick pumps are used for what material?
# Turns out that we do not need to know a specific pump's name.
red_pump_name = MyApparatus.findDevice({'descriptors': ['pump', 'red']})
green_pump_name = MyApparatus.findDevice({'descriptors': ['pump', 'green']})
blue_pump_name = MyApparatus.findDevice({'descriptors': ['pump', 'blue']})

# Now we create two procedures that let us handle our system more abstractly
PumpOn = Procedures.Pump_PumpOn(MyApparatus, MyExecutor)
PumpOff = Procedures.Pump_PumpOff(MyApparatus, MyExecutor)

# We can further complicate our control problem with some real-world issues
# like delays between pump signal and response.  For this example, we will
# assume all the materials and pumps behave the same but this is usually not
# the case.
PumpOn.requirements['pumpon_time']['value'] = 1
PumpOff.requirements['pumpoff_time']['value'] = 2

# These procedures are used much like the ones in Example 2 but they require
# More information

for n in range(5):
    PumpOn.Do({'name': red_pump_name})
    PumpOff.Do({'name': red_pump_name})
    PumpOn.Do({'name': green_pump_name})
    PumpOff.Do({'name': green_pump_name})
    PumpOn.Do({'name': blue_pump_name})
    PumpOff.Do({'name': blue_pump_name})

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

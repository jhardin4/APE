"""
Class to control an ultimus V pump connected using a serial com port and optional
    digital out.

Created on Tue May 23 16:00:48 2017
Modified 2017-06-16 V2 Added kwargs to input, DO and some error handling
Modified 2018-01-02 Cleaned up and added docs

@author: Alexander Cook
"""

import time
import serial

class Ultimus_V_Pump():
    '''
    Class to control an ultimus V pump connected via serial
    
    Command Structure:
        [STX] [No. of Byte] [Command] [Data] [Checksum] [ETX]
        STX: start of packet char: 0x02h
        #Byte: sum of the number of chars in command and data portion, 2 digit hex encoded as ascii
        Cmd: 4 char command, empty space is space char 0x20h, encoded in ascii
        data: 0-251 chars, xmit in ascii
        ChkSum: subtrac ascii values of #btys, cmd and data from zero, 2 digit hex encoded in ascii
        ETX: end of packet char, 0x03h
        
        Acknowledge :   0x06h
        Not Ack:        0x15h
        Enquiry:        0x05h
        End of Xmssion: 0x04h
        Success Command: A0
        Failure Command: A2
    '''
    
    VAC_UNITS = {   'kpa' :  0,
                    'inh2o': 1,
                    'inhg':  2,
                    'mmhg':  3,
                    'torr':  4}
    
    PRESS_UNITS = { 'psi' :  0,
                    'bar':   1,
                    'kpa':   2}
    
    VAC_MULT = {   'kpa' :   100,
                    'inh2o': 10,
                    'inhg':  100,
                    'mmhg':  10,
                    'torr':  10}
     
    PRESS_MULT = { 'psi' :  10,
                    'bar':   1000,
                    'kpa':   10}
    
    def __init__(self, com, **kwargs):
        '''
        Set up a pump object, connect to the pump via serial io and optionally 
            run initial configurations.
        
        Input:
            com: the serial port number that the pump is connected to as an int.
            **kwargs <optional keyword arguments>
                stop_on_errors: instruct the error handling to halt the program 
                    upon an error if Boolean True defaults to False
                trigger: set the trigger method 'com' or 'DO' defaults to 'com'
                pressure_units: the pressure units you would like to set,
                    defaults to whatever is on the pump
                vacuum_units: the vacuum units you would like to set,
                    defaults to whatever is on the pump
                pressure: float value of the pressure to set 
                For DO only:
                A3200: the A3200 instance
                
        
        '''
        self.no_pump = False
        self.debug = False
        self.pressure_units = None
        self.vacuum_units = None
        self.pressure = -1
        self.vacuum = -1
        self.pump = serial.Serial(
            port = "COM" + str(com),
            baudrate = 115200,
            parity = serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits = serial.STOPBITS_ONE,
            timeout = 0.125)
        self.dispensing = False
        if 'stop_on_errors' in kwargs:
            self.stop_on_errors = kwargs['stop_on_errors']
        else:
            self.stop_on_errors = False
        if 'trigger' in kwargs:
            self.trigger = 'com' #default to com
            if kwargs['trigger'].lower() is 'do':
                self.trigger = "DO"
                try:
                    from A3200 import A3200
                    self.A3200 = kwargs['A3200']
                    self.trigger_bit = kwargs['bit']
                    self.trigger_axis = kwargs['axis']
                except KeyError:
                    self.trigger = 'com'
        else:
            self.trigger = 'com'
        if 'pressure_units' in kwargs:
            self.set_pressure_units(kwargs['pressure_units'])
        else:
            self.get_pressure_units()
        if 'vacuum_units' in kwargs:
            self.set_vacuum_units(kwargs['pressure_units'])
        else:
            self.get_vacuum_units()
        if 'pressure' in kwargs:
            self.set_pressure(kwargs['pressure'])
        if 'vacuum' in kwargs:
            self.set_pressure(kwargs['vacuum'])
        if 'on_delay' in kwargs:
            self.dispense_on_delay = kwargs['on_delay']
        else:
            self.dispense_on_delay = 0
        if 'off_delay' in kwargs:
            self.dispense_off_delay = kwargs['off_delay']
        else:
            self.dispense_off_delay = 0
        
        
    def connect(self):
        if not self.pump.isOpen():
            self.pump.open()
            if self.pump.isOpen():
                self.connected = True
                return 1
            else:
                return 0
        else:
            return -1
    
    def disconnect(self, stopPump = False):
        if self.debug:
            print("Disconnecting pump")
            return 1
        else:
            if self.pump.isOpen():
                if stopPump:
                    self.stopPump()
                self.pump.close()
                if self.pump.isOpen():
                    return 0
                else:
                    return 1
            else:
                return -1
            
    def calc_checksum(self, code):
        '''
        Calculate a checsum value from a given code
        '''  
        return '%2X' % (-(sum(ord(c) for c in code) %256) & 0xFF)          
    
    def format_command(self, code):
        '''
        For a given string containing the command and data, format a complete command
        '''
        #calculate and append the Byte Count:
        code = "{length:02X}{text}".format(length = len(code), text = code)
        #calculate and append the checksum:
        code = code + self.calc_checksum(code)
        code = "\x02" + code + "\x03"
        return code
    
    def transmit_command(self, command):
        '''
        Send 'command' to the pump.
        '''
        print(command.encode("utf-8"))
        if self.no_pump:
            print('sending command: ', command.encode('utf-8'))
            return 1
        else:
            if self.pump.isOpen():
                self.pump.write(u"\x05".encode('utf-8'))
                ack = self.pump.readline()
                if self.debug:
                    if ack == '':
                        print('ack not read')
                    else:
                        print(ack)
                self.pump.write(command.encode('utf-8'))
                ack = self.pump.readline()
                if self.debug:
                    if ack == '':
                        print('A0/A2 not read')
                    else:
                        print(ack)
                self.pump.write(u"\x04".encode('utf-8'))        
                return 1
            else:
                if self.debug:
                    print('Cannot send command: {} , pump is not open'.format(command.encode('utf-8')))
                return -1                                                                        
    
    def transmit_query(self, command):
        '''
        Send 'command' to the pump.
        '''
        print(command.encode("utf-8"))
        if self.no_pump:
            print('sending command: ', command.encode('utf-8'))
            return 1
        else:
            if self.pump.isOpen():
                self.pump.write(u"\x05".encode('utf-8'))
                ack = self.pump.readline()
                if self.debug:
                    if ack == '':
                        print('ack not read')
                    else:
                        print(ack)
                self.pump.write(command.encode('utf-8'))
                ack = self.pump.readline()
                if self.debug:
                    if ack == '':
                        print('A0/A2 not read')
                    else:
                        print(ack)
                self.pump.write(u"\x06".encode('utf-8'))
                ack = self.pump.readline()
                if self.debug:
                    if ack == '':
                        print('ack not read')
                    else:
                        print(ack)
                self.pump.write(u"\x04".encode('utf-8'))        
                return ack
            else:
                if self.debug:
                    print('Cannot send command: {} , pump is not open'.format(command.encode('utf-8')))
                return ""                                                                        
    
                                                                                                                
    def set_pressure(self, pressure, units = None):
        '''
        Set the pressure on the pressure pump
        
        Command structure: PS--pppp 4 digit pressure excluding the decimal point.
            The value is unitless and range is determined by the selected pressure 
            units on the pump.
        '''
        if units is not None:
            self.set_pressure_units(units)
        #format the pressure
        press = int(round(pressure * Ultimus_V_Pump.PRESS_MULT[self.pressure_units]))
        #format the command and send
        r = self.transmit_command(self.format_command("PS  {:04}".format(press)))
        if r == 1:
            self.pressure = round(pressure, 1)
        
    def set_vacuum(self, vacuum, units = None):
        '''
        Set the pressure on the pressure pump
        
        Command structure: VS--vvvv 4 digit vacuum excluding the decimal point.
            The value is unitless and range is determined by the selected vacuum 
            units on the pump.
        '''
        if units is not None:
            self.set_vacuum_units(units)
        vac = int(round(vacuum * Ultimus_V_Pump.VAC_MULT[self.vacuum_units]))
        r = self.transmit_command(self.format_command("VS  {:04}".format(vac)))
        if r == 1:
            self.vacuum = round(vacuum, 1)
    
    def set_vacuum_units(self, units):
        '''
        Set the vacuum units on the pressure pump.
        
        Command structure: E7--uu 
            uu: the vacuum units:
                00: kPa
                01: inH2O
                02: inHg
                03: mmHg
                04: TORR
            note that the units codes are in the class dict: VAC_UNITS, keyed as seen here
        '''
        if units.lower() in Ultimus_V_Pump.VAC_UNITS:    
            if self.vacuum_units is not units.lower():
                r = self.transmit_command(self.format_command("E7  {:02}".format(Ultimus_V_Pump.VAC_UNITS[units.lower()])))
                if r == 1:
                    self.vacuum_units = units.lower()
        else:
            if self.debug:
                print("set_vac_units: improper vac units: {}".format(units))
            return -1
    
    def set_pressure_units(self, units):
        '''
        Set the pressure units on the pressure pump.
        
        Command structure: E7--uu 
            uu: the vacuum units:
                    'psi' :  00,
                    'bar':   01,
                    'kPa':   02}
            note that the units codes are in the class dict: PRESS_UNITS, keyed as seen here
        '''
        if units.lower() in Ultimus_V_Pump.PRESS_UNITS:    
            if self.pressure_units is not units.lower():
                r = self.transmit_command(self.format_command("E6  {:02}".format(Ultimus_V_Pump.PRESS_UNITS[units.lower()])))
                if r == 1:
                    self.pressure_units = units.lower()
        else:
            if self.debug:
                print("set_pressure_units: improper press units: {}".format(units))
            return -1
                                                    
    def toggle_dispense(self):
        '''
        Toggles the dispense on/off.
        '''
        if self.trigger == "com":        
            r = self.transmit_command(self.format_command("DI  "))
            if r == 1:
                self.dispensing = not self.dispensing
        if self.trigger is 'DO':
            if self.dispensing:
                if self.A3200.DO(self.trigger_bit, self.trigger_axis, False):
                    self.dispensing = False
            else:
                if self.A3200.DO(self.trigger_bit, self.trigger_axis, True):
                    self.dispensing = True
    
    def startPump(self):
        if not self.dispensing:
            self.toggle_dispense()
            time.sleep(self.dispense_on_delay)
        else:
            pass
    
    def stopPump(self):
        if self.dispensing:
            self.toggle_dispense()
            time.sleep(self.dispense_off_delay)
        else:
            pass
            
    def get_vacuum_units(self):
        '''
        Get the vacuum_units on the pump.
        
        return format:
            "DOVUuu" with uu as the unit numbers as stored in VAC_UNITS
        '''
        raw = self.transmit_query(self.format_command("E5  "))
        #check in case an empty string was returned
        if "VU".encode("utf-8") in raw:
            start = raw.find("VU".encode('utf-8')) + 2
            value = int(raw[start:start+2])
            #need to do reverse lookup in dictionary
            units = [key for key, v in Ultimus_V_Pump.VAC_UNITS.items() if v == value][0]
            self.vacuum_units = units
            if self.debug:
                print("get_vacuum_units: pump is using {}".format(units))
            return units
        else:
            if self.debug:
                print("get_vacuum_units: failure to communicate")
            return None
    
    def get_pressure_units(self):
        '''
        Get the pressure_units on the pump.
        
        return format:
            "DOPUuu" with uu as the unit numbers as stored in PRESS_UNITS
        '''
        raw = self.transmit_query(self.format_command("E4  "))
        #check in case an empty string was returned
        if "PU".encode("utf-8") in raw:
            start = raw.find("PU".encode('utf-8')) + 2
            value = int(raw[start:start+2])
            #need to do reverse lookup in dictionary
            units = [key for key, v in Ultimus_V_Pump.PRESS_UNITS.items() if v == value][0]
            self.pressure_units = units
            if self.debug:
                print("get_pressure_units: pump is using {}".format(units))
            return units
        else:
            if self.debug:
                print("get_pressure_units: failure to communicate")
            return None
        

'''
test code to run the pump
'''
if __name__ == "__main__":
   
    pump = Ultimus_V_Pump(4)
    pump.connect()
    time.sleep(1)
    pump.set_pressure_units('kPa')
    pump.set_vacuum_units('kPa')
    pump.set_pressure(150)
    pump.set_vacuum(0.1)
    time.sleep(1)
    '''
    pump.startPump()
    time.sleep(2)
    pump.stopPump()
    time.sleep(2)
    '''
    for i in range(100):
        pump.startPump()
        time.sleep(1)
        pump.stopPump()
        time.sleep(1)
    time.sleep(1)

    #a.disconnect()    
    pump.disconnect(True)
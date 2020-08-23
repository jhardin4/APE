"""
Class to control Keyence LS7010 micrometer via serial.
"""

import serial

class KeyenceLS7010(object):
    """
    The Keyence LS7010 micrometer array functions by communicating
    primarily over serial. The LS7010 controller only supports reading
    from 2 micrometer heads, but 3 micrometer heads are required for this
    setup (X,Y,Z). A digital output from the A3200 is required
    to switch a relay bank, which switches the connection from the controller
    between the Y and Z heads.
    """

    EOT = '\r\n'

    def __init__(self, com):
        self.connect(com)
        
    def connect(self, com):
        """
        Connect to micrometer over serial port.
        """
        self.s = serial.Serial(
            port="COM" + str(com),
            baudrate=115200,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            timeout=1)

    def disconnect(self):
        """
        Disconnect from micrometer over serial port.
        """
        self.s.close()

    def _send(self, command):
        """
        Send 'command' to the micrometer
        """
        msg = command + KeyenceLS7010.EOT
        self.s.write(msg.encode())
        data = '0'
        while data[-1] != '\r':
            data += self.s.read(self.s.inWaiting())
        return data[1:-1]

    def _set_program(self, number):
        """
        Set current program running on micrometer controller
        """
        return self._send('PW,{}'.format(number))

    def xy_mode(self):
        """
        Switch micrometer to program 3, for reading XY position
        Note: Relay bank must also be switched $DO7.0=0
        """
        self._set_program(3)

    def z_mode(self):
        """
        Switch micrometer to program 4, for reading Z position
        Note: Relay bank must also be switched $DO7.0=1
        """
        self._set_program(4)

    def _read(self, output=1):
        """
        Read measurement from micrometer.
        output : either 1, 2, or 'both'
            Which of the measurement heads to read
        """
        if output == 'both':
            output = 0
        val = self._send('M{},0'.format(output))[3:]
        if output == 0:
            val1, val2 = val.split(',')
            if '--' not in val1:
                return float(val1), float(val2)
            else:
                return None, None
        if '--' not in val:
            return float(val)
        else:
            return None
    
    def get_z(self):
        """
        Measure Z position of nozzle tip.
        Note: The relay bank must be switched to $DO7.0=1
            and the micrometer must be set to program 4
            (z_mode).
        """
        return self._read(output=2)

    def get_xy(self):
        """
        Measure XY position of nozzle tip.
        Note: The relay bank must be switched to $DO7.0=0
            and the micrometer must be set to program 3
            (xy_mode).
        """
        return self._read(output='both')
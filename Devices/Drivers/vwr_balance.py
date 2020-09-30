"""
Class to control VWR P2 series balances via serial.
"""

import serial

class VWRBalance(object):
    """
    List of Commands:
    *   Z : Zero balance
    *   T : Tare balance
        OT : Give tare value
        UT : Set tare
    *   S : Send stable measurement result in basic measuring unit
    *   SI : Immediately send measurement result in basic measuring unit SU Send stable measurement result in current measuring unit
        SUI : Immediately send measurement result in current measuring unit C1 Switch on continuous transmission in basic measuring unit
        C0 : Switch off continuous transmission in basic measuring unit
        CU1 : Switch on continuous transmission in current measuring unit CU0 Switch off continuous transmission in current measuring unit
        K1 : Lock balance keypad
        K0 : Unlock balance keypad
        NB : Give balance serial number
        PC : Send all implemented commands

    * Implemented
    """

    EOT = '\r\n'

    def __init__(self, com):
        self.connect(com)
        
    def connect(self, com):
        """
        Connect to balance over serial port.
        """
        self.s = serial.Serial(
            port="COM" + str(com),
            baudrate=115200,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            timeout=2,)

    def disconnect(self):
        """
        Disconnect from balance over serial port.
        """
        self.s.close()
        
    def _send(self, command, response_count):
        """
        Send 'command' to the pump.
        Commands can result in a varied number of responses with a possible second(s)
            delay (if stabilizing). The response count argument denotes how many responses 
            to wait for before continuing. Each command must end with CR LF characters.
            Wait before sending another command until the answer has been received, otherwise
            the answers may be lost.
        """
        response = []
        msg = command + VWRBalance.EOT
        self.s.write(msg.encode())
        for _ in range(response_count):
            response.append(self.s.readline().decode())
        return response

    def zero(self):
        """
        Balance should be zeroed before use. Meant for small adjustments.
        Response options:
            1. Command understood and in progrss, command carried out:
                'Z_A CR LF' then 'Z_D CR LF'
            2. Command understood and in progress, command understood but zeroing range is exceeded.
                'Z_A CR LF' then 'Z_^ CR LF' 
            3. Command understood and in progress, time limit exceeded while waiting for stable measurement result.
                'Z_A CR LF' then 'Z_E CR LF'
            4. Command understood but not accessible at this moment
                'Z_I CR LF'
        """
        return self._send('Z',2)

    def tare(self):
        """
        Balance should be tared with container on plate. Meant for large adjustments.
        Response options:
            1. Command understood and in progrss, command carried out:
                'T_A CR LF' then 'T_D CR LF'
            2. Command understood and in progress, command understood but taring range is exceeded.
                'T_A CR LF' then 'T_v CR LF' 
            3. Command understood and in progress, time limit exceeded while waiting for stable measurement result.
                'TA CR LF' then 'T_E CR LF'
            4. Command understood but not accessible at this moment
                'T_I CR LF'
        """
        return self._send('T',2)

    def measure(self):
        """
        Immediately send measurement result in basic measuring unit (g).
        Response options:
            1. Command understood but not accessible at this moment
                'SI_I CR LF'
            2. Immediate response, mass value in basic measuring unit.
                'MASS FRAME' detailed below
 
        Response format (MASS FRAME):
            Stability Marker:
                ' ' if measurement result is stable
                '?' if measurement result is unstable
                '^' if high limit is out of range
                'v' if low limit is out of range 
            Character:
                ' ' for positive values
                '-' for negative values
            Mass:
                9 characters with decimal point, right justification
            Unit:
                3 characters, left justification (ex: 'g','lb','kg')
        """
        reading = self._send('SI',1)[0]
        while reading == 'SI_I \r \n':
            reading = self._send('SI',1)[0]
        self.stability_marker = reading[3]
        self.character= reading[5]
        self.mass = float(reading[6:15])
        self.unit = reading[16:19]
        return self.mass

    def stable_measure(self):
        """
        Send stable measurement result in basic measuring unit (g).
        Response options:
            1. Command understood and in progress, time limit exceeded while waiting for stable measurement result.
                'S_A CR LF' then 'S_E CR LF'
            2. Command understood but not accessible at this moment
                'S_I CR LF'
            3. Command understood and in progress, response with masss value in basic measuring unit.
                'S_A CR LF' then 'MASS FRAME' detailed below
 
        Response format (MASS FRAME):
            Stability Marker:
                ' ' if measurement result is stable
                '?' if measurement result is unstable
                '^' if high limit is out of range
                'v' if low limit is out of range 
            Character:
                ' ' for positive values
                '-' for negative values
            Mass:
                9 characters with decimal point, right justification
            Unit:
                3 characters, left justification (ex: 'g','lb','kg')
        """
        reading = self._send('S',2)
        while reading[0] == 'S_I \r \n' or reading[1] == 'SI_E \r \n':
            reading = self._send('SI',2)
        reading = reading[1]
        self.stability_marker = reading[3]
        self.character = reading[5]
        self.mass = float(reading[6:15])
        self.unit = reading[16:19]
        return self.mass
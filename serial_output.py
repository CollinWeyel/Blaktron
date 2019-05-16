#A serial Output for the mido library

from mido.ports import BaseOutput
import serial
import time
import array as arr

def get_devices():
    return [{'name': 'Serial Port', 'isInput': False, 'isOutput': True}]

class Output(BaseOutput):
    def _open(self, **kwargs):
        device = get_devices()[0]

        self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, rtscts=False, dsrdtr=False)
        print(self.ser.name)

        if self.name is None:
            self.name = device['name']
        elif self.name != device['name']:
            raise ValueError('unknown port {!r}'.format(self.name))

        time.sleep(15)

    def _send(self, message):
        print(message)
        print(message.bytes())
        if (len(message.bytes()) == 3):
            m = bytes([message.bytes()[0]])
            self.ser.write(m)
            print(m)

            m = bytes([message.bytes()[1]])
            self.ser.write(m)
            print(m)

            m = bytes([message.bytes()[2]])
            self.ser.write(m)
            print(m)

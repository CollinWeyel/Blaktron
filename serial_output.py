#A serial Output for the mido library

from mido.ports import BaseOutput

def get_devices():
    return [{'name': 'Serial Port', 'isInput': False, 'isOutput': True}]

class Output(BaseOutput):
    def _open(self, **kwargs):
        device = get_devices()[0]

        if self.name is None:
            self.name = device['name']
        elif self.name != device['name']:
            raise ValueError('unknown port {!r}'.format(self.name))

    def _send(self, message):
        print(message.hex())

import struct
import time
import can
import math
from vesc_controller import VESC, VESCStatusPacket

# Configuration
CHANNEL_LOAD = 'can1'    #"Load" is the motor that is inducing some load (for some reason the can ports are swapped compared to what's shown on the hat board)
CHANNEL_ACTIVE = 'can0'  #"Active" is the motor trying to match the induced load
BITRATE = 500000
ID_LOAD = 10
ID_ACTIVE = 11

CAN_CMD_SET_CURRENT = 1
CAN_CMD_STATUS = 0x200

PSEUDO_INPUT_LOAD = 5 #N-m

load_vesc = VESC(can_channel = CHANNEL_LOAD, vesc_id = ID_LOAD)
active_vesc = VESC(can_channel = CHANNEL_ACTIVE, vesc_id = ID_ACTIVE)

def pseudo_load(input_load: float):
    """Emulating a load cell 0-5V output with some added noise. Assumes load cell output is sigmoidal and noise exponentially decreases.
        input_load: The desired load we want to emulate
    """
    output_load = float

    sigmoid_function = 3.5/(1+math.pow(math.e,(-(input_load - 5)))) + 0.5
    noise_function = (math.random()-0.5)*(math.pow(1.4,-(input_load + 0.7) + 0.2))
    output_load = sigmoid_function + noise_function

    return output_load


def main():
    try:
        while True:

            load_vesc.set_current(3)
            active_vesc.set_current(-3)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()


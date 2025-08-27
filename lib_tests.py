import struct
import time
import can
from vesc_controller import VESC, VESCStatusPacket

# Configuration
CHANNEL_LOAD = 'can1'    #"Load" is the motor that is inducing some load (for some reason the can ports are swapped compared to what's shown on the hat board)
CHANNEL_ACTIVE = 'can0'  #"Active" is the motor trying to match the induced load
BITRATE = 500000
ID_LOAD = 10
ID_ACTIVE = 11

CAN_CMD_SET_CURRENT = 1
CAN_CMD_STATUS = 0x200

load_vesc = VESC(can_channel = CHANNEL_LOAD, vesc_id = ID_LOAD)
active_vesc = VESC(can_channel = CHANNEL_ACTIVE, vesc_id = ID_ACTIVE)

def main():
    try:
        while True:
            load_vesc.set_erpm(6000)
            active_vesc.set_erpm(-6000)
            time.sleep(1)
            load_speed = float(load_vesc.get_erpm())
            active_speed = float(active_vesc.get_erpm())
            print(f"Load Speed: {load_speed} \t Active Speed: {active_speed}")

    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()


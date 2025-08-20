import struct
import time
import can

# Configuration
CHANNEL_LOAD = 'can1'    #"Load" is the motor that is inducing some load
CHANNEL_ACTIVE = 'can0'  #"Active" is the motor trying to match the induced load
BITRATE = 500000
ID_LOAD = 10
ID_ACTIVE = 11

CAN_CMD_SET_CURRENT = 1
CAN_CMD_STATUS = 0x200

def make_current(vesc_id, current_amps):
    """Create a CAN message to command phase current in mA"""
    eid = (CAN_CMD_SET_CURRENT << 8) | vesc_id
    value = int(current_amps * 1000)
    data = struct.pack('>i',value)
    return can.Message(arbitration_id = eid, data = data, is_extended_id = True)


def parse_status(msg):
    """Parse a status frame"""
    mA, = struct.unpack('>i', msg.data[0:4])
    amps = mA / 1000.0
    return amps


def main():
    bus_load = can.Bus(interface='socketcan', channel=CHANNEL_LOAD, bitrate=BITRATE)
    bus_active = can.Bus(interface='socketcan', channel=CHANNEL_ACTIVE, bitrate=BITRATE)
    notifier0 = can.Notifier(bus_load, [can.Printer(),])
    notifier1 = can.Notifier(bus_active, [can.Printer(),])

    try:
        while True:
            bus_load.send(make_current(ID_LOAD, 3))
            bus_active.send(make_current(ID_ACTIVE, 0.7))
            
            time.sleep(0.2)

            msg_load = bus_load.recv(timeout=1.0)
            msg_active = bus_active.recv(timeout=1.0)

            if msg_load:
                print(f"Load status ({hex(msg_load.arbitration_id)}): {parse_status(msg_load):.3f} A")
            if msg_active:
                print(f"Active status ({hex(msg_active.arbitration_id)}): {parse_status(msg_active):.3f} A")
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        notifier0.stop()
        notifier1.stop()
        bus_load.shutdown()
        bus_active.shutdown()

if __name__ == "__main__":
    main()


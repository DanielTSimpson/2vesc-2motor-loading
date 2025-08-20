import struct
import time
import can

# Configuration
CHANNEL_LOAD = 'can1'    #"Load" is the motor that is inducing some load (for some reason the can ports are swapped compared to what's shown on the hat board)
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


def parse_can_status(msg):
    """Parse a status frame"""
    packet_id = (msg.arbitration_id >> 8) & 0xFF
    data = msg.data
    
    print(msg)
    duty = int.from_bytes(msg.data[6:8], 'big', signed=True) / 10.0 # %
    current = int.from_bytes(msg.data[4:6], 'big', signed=True) / 10.0 # A
    rpm = int.from_bytes(msg.data[0:4], 'big', signed=True) # RPM

    return {"duty":duty, "current":current, "rpm":rpm}


def main():
    bus_load = can.Bus(interface='socketcan', channel=CHANNEL_LOAD, bitrate=BITRATE)
    bus_active = can.Bus(interface='socketcan', channel=CHANNEL_ACTIVE, bitrate=BITRATE)

    try:
        while True:
            bus_load.send(make_current(ID_LOAD, 3))
            bus_active.send(make_current(ID_ACTIVE, 0.7))
            
            time.sleep(0.2)

            msg_load = bus_load.recv(timeout=1.0)
            msg_active = bus_active.recv(timeout=1.0)
            
            load_data = None
            active_data = None

            if msg_load:
                load_data = parse_can_status(msg_load)
            if msg_active:
                active_data = parse_can_status(msg_active)
            
            if msg_load and msg_active:
                print(f"LOAD CURRENT: {load_data['current']} A \t ACTIVE CURRENT: {active_data['current']} \t")
            
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        bus_load.shutdown()
        bus_active.shutdown()

if __name__ == "__main__":
    main()


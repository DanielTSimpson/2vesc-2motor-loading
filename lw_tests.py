import struct
import time
import can
from labjack import ljm

# Configuration
CHANNEL_LOAD = 'can1'    #"Load" is the motor that is inducing some load (for some reason the can ports are swapped compared to what's shown on the hat board)
CHANNEL_ACTIVE = 'can0'  #"Active" is the motor trying to match the induced load
BITRATE = 500000
ID_LOAD = 10
ID_ACTIVE = 11
POLE_PAIRS = 4

CAN_CMD_SET_CURRENT = 1
CAN_CMD_SET_RPM = 3
CAN_CMD_STATUS = 0x200

#LabJack setup
handle = ljm.openS("ANY", "ANY", "ANY")
info = ljm.getHandleInfo(handle)
name = "AIN0"


def set_current(vesc_id, current_amps):
    """Create a CAN message to command phase current in mA"""
    eid = (CAN_CMD_SET_CURRENT << 8) | vesc_id
    value = int(current_amps * 1000)
    data = struct.pack('>i',value)
    return can.Message(arbitration_id = eid, data = data, is_extended_id = True)

def set_erpm(vesc_id, speed_erpm):
    """Create a CAN message to command revolutions per minute"""
    eid = (CAN_CMD_SET_RPM << 8) | vesc_id
    value = int(speed_erpm)
    data = struct.pack('>i',value)
    return can.Message(arbitration_id = eid, data = data, is_extended_id = True)

def parse_can_status(msg):
    """Parse a status frame"""
    data = msg.data
    
    duty = struct.unpack(">h",data[6:8])[0] / 1000.0
    current = struct.unpack(">h",data[4:6])[0] / 10.0
    erpm = struct.unpack(">i",data[0:4])[0]

    return {"duty":duty, "current":current, "erpm":erpm}


def main():
    bus_load = can.Bus(interface='socketcan', channel=CHANNEL_LOAD, bitrate=BITRATE)
    bus_active = can.Bus(interface='socketcan', channel=CHANNEL_ACTIVE, bitrate=BITRATE)

    try:
        while True:
            #bus_load.send(set_current(ID_LOAD, -2))
            #bus_active.send(set_current(ID_ACTIVE, 0.7))
            
            bus_load.send(set_erpm(ID_LOAD, -400*POLE_PAIRS))
            bus_active.send(set_erpm(ID_ACTIVE, 300*POLE_PAIRS))
            
            time.sleep(0.001)

            msg_load = bus_load.recv(timeout=1.0)
            msg_active = bus_active.recv(timeout=1.0)
            
            load_data = None
            active_data = None

            if msg_load:
                load_data = parse_can_status(msg_load)
            if msg_active:
                active_data = parse_can_status(msg_active)
            measured_load = ljm.eReadName(handle, name)

            if msg_load and msg_active:
                #print(f"LOAD CURRENT: {load_data['current']} A \t ACTIVE CURRENT: {active_data['current']} \t")
                print(f"LOAD ERPM: {load_data['erpm']/POLE_PAIRS} rpm \t ACTIVE ERPM: {active_data['erpm']/POLE_PAIRS} rpm \t Load Voltage: {measured_load}")
                
            
            time.sleep(1/60)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        bus_load.shutdown()
        bus_active.shutdown()
        ljm.close(handle)

if __name__ == "__main__":
    main()


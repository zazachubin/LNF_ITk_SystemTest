from datetime import datetime
from opcua import Client
import logging
import time
import os

Delay = 1


print('##################### START #####################')
# LISSY OPC UA Client
interlock_client = Client("opc.tcp://192.168.2.99:4841/") # Initiate
# HMP4040 Power supply OPC UA Client
psu_client = Client("opc.tcp://localhost:4843/HMP4040_opcua/server/") # Initiate
# Connect to Server
interlock_client.connect()
# Connect to Server
psu_client.connect()

while True:
    try:
        # LISSY OPCUA DPs hierarchy
        interlock_objects = interlock_client.get_objects_node()
        # HMP4040 PS OPCUA DPs hierarchy
        psu_objects = psu_client.get_objects_node()

        #################### Time in miliseconds UTC ##########################
        CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())
        #######################################################################
        # Retrive LISSY Digital Out Slot 10 status
        out_a = interlock_objects.get_child(["2:MonitorController","2:Frascati","2:OUT_S10","2:out_a"]).get_value()
        out_b = interlock_objects.get_child(["2:MonitorController","2:Frascati","2:OUT_S10","2:out_b"]).get_value()
        OUT_S10_state = "{:016b}".format(out_a)[::-1] + "{:016b}".format(out_b)[::-1]
        #######################################################################
        # Retrive HMP4040 PS2 channel statuses (CH1, CH2, Ch4)
        ps2_get_ch1_status = psu_objects.get_child(["2:ps2","2:channel1","2:actual","2:isOn"]).get_value()
        ps2_get_ch2_status = psu_objects.get_child(["2:ps2","2:channel2","2:actual","2:isOn"]).get_value()
        ps2_get_ch4_status = psu_objects.get_child(["2:ps2","2:channel4","2:actual","2:isOn"]).get_value()
        
        # Retrive HMP4040 PS1 channel statuses (CH1, CH2)
        ps1_get_ch1_status = psu_objects.get_child(["2:ps1","2:channel1","2:actual","2:isOn"]).get_value()
        ps1_get_ch2_status = psu_objects.get_child(["2:ps1","2:channel2","2:actual","2:isOn"]).get_value()

        # Print all data
        print('#################################################')
        print("Time: {}".format(CurrentTime))
        print("OUT_S10_status: {}".format(OUT_S10_state))
        print("PS2 - CH1_status: {}".format(ps2_get_ch1_status))
        print("PS2 - CH2_status: {}".format(ps2_get_ch2_status))
        print("PS2 - CH4_status: {}".format(ps2_get_ch4_status))
        print("PS1 - CH1_status: {}".format(ps1_get_ch1_status))
        print("PS1 - CH1_status: {}".format(ps1_get_ch2_status))
        print('############## Interlock status #################')

        # Compare SLOT 10 digita out statuses
        if OUT_S10_state[3] == "1":
            print("### Module3_V2_Event ###")
            # Turn OFF channel after Module3 V2 Event
            psu_objects.get_child(["2:ps1","2:channel1","2:settings","2:onOff"]).set_value(False)
            psu_objects.get_child(["2:ps1","2:channel2","2:settings","2:onOff"]).set_value(False)

        if OUT_S10_state[2] == "1":
            print("### OptoBoard_Event ###")
            # Turn OFF channel after OptoBoard Event
            psu_objects.get_child(["2:ps2","2:channel1","2:settings","2:onOff"]).set_value(False)

        if OUT_S10_state[1] == "1":
            print("### Cooling_Event ###")
            # Turn OFF channel after Cooling Event
            psu_objects.get_child(["2:ps2","2:channel2","2:settings","2:onOff"]).set_value(False)

        if OUT_S10_state[0] == "1":
            print("### SP_Modules_Event ###")
            # Turn OFF channel after SP Modules Event
            psu_objects.get_child(["2:ps2","2:channel4","2:settings","2:onOff"]).set_value(False)

        if OUT_S10_state[0] != "1" and OUT_S10_state[1] != "1" and OUT_S10_state[2] != "1" and OUT_S10_state[3] != "1":
            print("### All Ok ###")

        time.sleep(Delay)

    except:
        print('##################### STOP ######################')
        os.kill(os.getpid(), 9)
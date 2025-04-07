from datetime import datetime
from opcua import Client
import logging
import time
import os

logFile = False
Delay = 1

try:
    print('##################### START #####################')
    interlock_client = Client("opc.tcp://192.168.2.99:4841/") # Initiate
    psu_client = Client("opc.tcp://localhost:4841/") # Initiate
    # Connect to Server
    interlock_client.connect()
    # Connect to Server
    psu_client.connect()

    #def your_function():
    # Your code here
    while True:
        try:
            interlock_objects = interlock_client.get_objects_node()
            psu_objects = psu_client.get_objects_node()

            #################### Time in miliseconds UTC ##########################
            CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())
            #######################################################################
            out_a = interlock_objects.get_child(["2:MonitorController","2:Frascati","2:OUT_S10","2:out_a"]).get_value()
            out_b = interlock_objects.get_child(["2:MonitorController","2:Frascati","2:OUT_S10","2:out_b"]).get_value()
            OUT_S10_state = "{:016b}".format(out_a)[::-1] + "{:016b}".format(out_b)[::-1]
            #######################################################################
            get_ch1_status = psu_objects.get_child(["2:ps2","2:channel1","2:actual","2:isOn"]).get_value()
            get_ch2_status = psu_objects.get_child(["2:ps2","2:channel2","2:actual","2:isOn"]).get_value()
            #get_ch3_status = psu_objects.get_child(["2:ps2","2:channel3","2:actual","2:isOn"]).get_value()
            get_ch4_status = psu_objects.get_child(["2:ps2","2:channel4","2:actual","2:isOn"]).get_value()

            # Print all sensors data
            print('#################################################')
            print("Time: {}".format(CurrentTime))
            print("OUT_S10_status: {}".format(OUT_S10_state))
            print("CH1_status: {}".format(get_ch1_status))
            print("CH2_status: {}".format(get_ch2_status))
            #print("CH3_status: {}".format(get_ch3_status))
            print("CH4_status: {}".format(get_ch4_status))
            print('############## Interlock status #################')

            if OUT_S10_state[2] == "1":
                print("### OptoBoard_Event ###")
                psu_objects.get_child(["2:ps2","2:channel1","2:settings","2:onOff"]).set_value(False)

            if OUT_S10_state[1] == "1":
                print("### Cooling_Event ###")
                psu_objects.get_child(["2:ps2","2:channel2","2:settings","2:onOff"]).set_value(False)

            if OUT_S10_state[0] == "1":
                print("### Serial_Modules_Event ###")
                psu_objects.get_child(["2:ps2","2:channel4","2:settings","2:onOff"]).set_value(False)

            if OUT_S10_state[0] != "1" and OUT_S10_state[1] != "1" and OUT_S10_state[2] != "1":
                print("### All Ok ###")

            time.sleep(Delay)

        except:
            print('##################### STOP ######################')
            os.kill(os.getpid(), 9)
            #logging.error(traceback.format_exc())
            #break
except OSError:
    logging.error("No route to host!")
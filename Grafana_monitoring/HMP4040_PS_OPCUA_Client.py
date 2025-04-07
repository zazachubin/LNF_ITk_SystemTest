from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient
from datetime import datetime
from opcua import Client
import time

############################## InfluxDB ###############################
InfluxDB_ADDRESS = "http://localhost:8086"     # InfluxDB Local address
# You can generate an API token from the "API Tokens Tab" in the UI
token = "0xnV4c1Lfe1ZYMS41nPlJ66nb-c6XA7DUioX9iu8PeQC1Q2QoNJp2eCh8R3bx7pXlGtBpjY_Oh5TBzuAuCrP5w=="
org = "ITK"
bucket = "test"

Delay = 1                                      # Device reading delay [s]

# InfluxDB setup
dbclient = InfluxDBClient(url=InfluxDB_ADDRESS, token=token, org=org)
write_api = dbclient.write_api(write_options=SYNCHRONOUS)

client = Client("opc.tcp://localhost:4843/HMP4040_opcua/server/") # Initiate

while True:
    try:
        # Connect to Server
        client.connect()

        # should always be in address space such as Root or Objects
        #root = client.get_root_node()
        #print("Objects node is: ", root)

        objects = client.get_objects_node()
        #print("Objects node is: ", objects)

        #################### Time in miliseconds UTC ##########################
        CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())

        get_ch1_i0 = round(objects.get_child(["2:ps2","2:channel1","2:actual","2:iMon"]).get_value(),6)
        get_ch1_v0 = round(objects.get_child(["2:ps2","2:channel1","2:actual","2:vMon"]).get_value(),3)
        get_ch1_settings_v0 = round(objects.get_child(["2:ps2","2:channel1","2:readbackSettings","2:v0"]).get_value(),3)
        get_ch1_settings_i0 = round(objects.get_child(["2:ps2","2:channel1","2:readbackSettings","2:i0"]).get_value(),6)
        if objects.get_child(["2:ps2","2:channel1","2:actual","2:isOn"]).get_value() == True:
            get_ch1_status = 1
        else:
            get_ch1_status = 0

        get_ch2_i0 = round(objects.get_child(["2:ps2","2:channel2","2:actual","2:iMon"]).get_value(),6)
        get_ch2_v0 = round(objects.get_child(["2:ps2","2:channel2","2:actual","2:vMon"]).get_value(),3)
        get_ch2_settings_v0 = round(objects.get_child(["2:ps2","2:channel2","2:readbackSettings","2:v0"]).get_value(),3)
        get_ch2_settings_i0 = round(objects.get_child(["2:ps2","2:channel2","2:readbackSettings","2:i0"]).get_value(),6)
        if objects.get_child(["2:ps2","2:channel2","2:actual","2:isOn"]).get_value() == True:
            get_ch2_status = 1
        else:
            get_ch2_status = 0

        get_ch4_i0 = round(objects.get_child(["2:ps2","2:channel4","2:actual","2:iMon"]).get_value(),6)
        get_ch4_v0 = round(objects.get_child(["2:ps2","2:channel4","2:actual","2:vMon"]).get_value(),3)
        get_ch4_settings_v0 = round(objects.get_child(["2:ps2","2:channel4","2:readbackSettings","2:v0"]).get_value(),3)
        get_ch4_settings_i0 = round(objects.get_child(["2:ps2","2:channel4","2:readbackSettings","2:i0"]).get_value(),6)
        if objects.get_child(["2:ps2","2:channel4","2:actual","2:isOn"]).get_value() == True:
            get_ch4_status = 1
        else:
            get_ch4_status = 0

        # Print all sensors data
        print('#################################################')
        print("Time: {}".format(CurrentTime))
        print("OptoBoard_Voltage [V]: {}".format(get_ch1_v0))
        print("OptoBoard_Current [A]: {}".format(get_ch1_i0))
        print("OptoBoard_Status [on/off]: {}".format(get_ch1_status))
        print('_________________________________________________')
        print("Cooling_Voltage [V]: {}".format(get_ch2_v0))
        print("Cooling_Current [A]: {}".format(get_ch2_i0))
        print("Cooling_Status [on/off]: {}".format(get_ch2_status))
        print('_________________________________________________')
        print("SerialModules_Voltage [V]: {}".format(get_ch4_v0))
        print("SerialModules_Current [A]: {}".format(get_ch4_i0))
        print("SerialModules_Status [on/off]: {}".format(get_ch4_status))

        # Container for DB
        influxdbContainer = []

        # Add OptoBoard Power info in DB
        influxdbContainer.append(
            {
                "measurement": "OptoBoard Power",
                "tags": {
                    "OptoBoard" : 'Power'
                },
                "time": CurrentTime,
                "fields": {
                    "OptoBoard_Voltage[V]" : get_ch1_v0,
                    "OptoBoard_Current[A]" : get_ch1_i0,
                    "OptoBoard_Status[On/Off]" : get_ch1_status,
                    "OptoBoard_Voltage_Setting[V]" : get_ch1_settings_v0,
                    "OptoBoard_Current_Setting[A]" : get_ch1_settings_i0,
                }
            }
        )
        # Add Module Cooling Power info in DB
        influxdbContainer.append(
            {
                "measurement": "Modules Cooling Power",
                "tags": {
                    "Modules Cooling" : 'Power'
                },
                "time": CurrentTime,
                "fields": {
                    "Cooling_Voltage[V]" : get_ch2_v0,
                    "Cooling_Current[A]" : get_ch2_i0,
                    "Cooling_Status[On/Off]" : get_ch2_status,
                    "Cooling_Voltage_Setting[V]" : get_ch2_settings_v0,
                    "Cooling_Current_Setting[A]" : get_ch2_settings_i0,
                }
            }
        )
        # Add Module Power info in DB
        influxdbContainer.append(
            {
                "measurement": "Serial Modules Power",
                "tags": {
                    "Serial Modules" : 'Power'
                },
                "time": CurrentTime,
                "fields": {
                    "Serial_Modules_Voltage[V]" : get_ch4_v0,
                    "Serial_Modules_Current[A]" : get_ch4_i0,
                    "Serial_Modules_Status[On/Off]" : get_ch4_status,
                    "Serial_Modules_Voltage_Setting[V]" : get_ch4_settings_v0,
                    "Serial_Modules_Current_Setting[A]" : get_ch4_settings_i0,
                }
            }
        )
        # Write All sensors data into DB
        write_api.write(bucket, org, influxdbContainer)
        # Delay of data taking

        time.sleep(Delay)

    except ValueError:
        pass

    except:
        print("Except event")
        pass
    
    finally :
        # Disconnect when finish
        client.disconnect()

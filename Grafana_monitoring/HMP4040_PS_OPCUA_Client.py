from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient
from datetime import datetime
from opcua import Client
import time
import os

############################## InfluxDB ###############################
InfluxDB_ADDRESS = os.environ.get("INFLUXDB_ADDRESS", "http://localhost:8086")
# API token should be set via environment variable INFLUXDB_TOKEN
token = os.environ.get("INFLUXDB_TOKEN", "")
if not token:
    raise ValueError("INFLUXDB_TOKEN environment variable must be set")
org = os.environ.get("INFLUXDB_ORG", "ITK")
bucket = os.environ.get("INFLUXDB_BUCKET", "PixelSetup")

Delay = 1                                      # Device reading delay [s]

# InfluxDB setup
dbclient = InfluxDBClient(url=InfluxDB_ADDRESS, token=token, org=org)
write_api = dbclient.write_api(write_options=SYNCHRONOUS)

client = Client("opc.tcp://localhost:4843/HMP4040_opcua/server/")  # Initiate

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
                "measurement": "OptoBoard",
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
                "measurement": "Modules Cooling",
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
                "measurement": "Pixel_SP_Chain",
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

from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient
from datetime import datetime
from opcua import Client
import time
import os

def dewPoint_formula(DPv):
    chamber_DewPoint = ((DPv-2.016) / 0.0192) - 2.434
    return chamber_DewPoint

############################## InfluxDB ###############################
InfluxDB_ADDRESS = os.environ.get("INFLUXDB_ADDRESS", "http://localhost:8086")
# API token should be set via environment variable INFLUXDB_TOKEN
token = os.environ.get("INFLUXDB_TOKEN", "")
if not token:
    raise ValueError("INFLUXDB_TOKEN environment variable must be set")
org = os.environ.get("INFLUXDB_ORG", "ITK")
bucket = os.environ.get("INFLUXDB_BUCKET", "PixelSetup")

Delay = 0.1                                      # Device reading delay [s]

# InfluxDB setup
dbclient = InfluxDBClient(url=InfluxDB_ADDRESS, token=token, org=org)
write_api = dbclient.write_api(write_options=SYNCHRONOUS)

client = Client("opc.tcp://localhost:4844/DAQ970A_opcua/server/")  # Initiate

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

        module1_V = round(objects.get_child(["2:DAQ970A","2:Channels","2:Ch_101"]).get_value(),6)
        module2_V = round(objects.get_child(["2:DAQ970A","2:Channels","2:Ch_111"]).get_value(),6)

        Optoboard_V = round(objects.get_child(["2:DAQ970A","2:Channels","2:Ch_102"]).get_value(),6)

        dewPoint = round(dewPoint_formula(objects.get_child(["2:DAQ970A","2:Channels","2:Ch_105"]).get_value()),6)

        # Print all sensors data
        print('#################################################')
        print("Time: {}".format(CurrentTime))
        print("MODULE 1 Voltage [V]: {}".format(module1_V))
        print("MODULE 2 Voltage [V]: {}".format(module2_V))
        print("OptoBoard Voltage [V]: {}".format(Optoboard_V))
        print("Dew Point [°C]: {}".format(dewPoint))
        print('_________________________________________________')

        # Container for DB
        influxdbContainer = []

        # Add OptoBoard Power info in DB
        influxdbContainer.append(
            {
                "measurement": "Pixel_SP_Chain",
                "time": CurrentTime,
                "fields": {
                    "Module1_Voltage[V]" : module1_V,
                    "Module2_Voltage[V]" : module2_V,
                }
            }
        )
        # Add Dew Point info in DB
        influxdbContainer.append(
            {
                "measurement": "Environment",
                "time": CurrentTime,
                "fields": {
                    "Dew Point [°C]" : dewPoint,
                }
            }
        )

        # Add Dew Point info in DB
        influxdbContainer.append(
            {
                "measurement": "OptoBoard",
                "time": CurrentTime,
                "fields": {
                    "Opto Board Voltage [V]" : Optoboard_V,
                }
            }
        )
        # Write All sensors data into DB
        write_api.write(bucket, org, influxdbContainer)
        # Delay of data taking

        time.sleep(Delay)

    except ValueError:
        pass

    #except:
    #    print("Except event")
    #    pass
    
    finally :
        # Disconnect when finish
        client.disconnect()

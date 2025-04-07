from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient
from datetime import datetime
from opcua import Client
import logging
import time
import math
import os


def ConvAdc2Temp(adc_chan):
    tn = 298.15
    b = 3435.0

    if (0<adc_chan & adc_chan<32760):
        adc_to_degree = 1.0/(math.log(1./(32767./adc_chan-1))/b+1/tn)-273.15
        return adc_to_degree
    else:
        adc_to_degree=adc_chan
        return -999

############################## InfluxDB ###############################
InfluxDB_ADDRESS = "http://localhost:8086"     # InfluxDB Local address
# You can generate an API token from the "API Tokens Tab" in the UI
token = "0xnV4c1Lfe1ZYMS41nPlJ66nb-c6XA7DUioX9iu8PeQC1Q2QoNJp2eCh8R3bx7pXlGtBpjY_Oh5TBzuAuCrP5w=="
org = "ITK"
bucket = "test"

logFile = False

Delay = 1                                      # Device reading delay [s]

filePath = 'data_{}.csv'.format(str(datetime.fromtimestamp(datetime.utcnow().timestamp())).replace(':','-'))

try:
    print('##################### START #####################')
    # InfluxDB setup
    dbclient = InfluxDBClient(url=InfluxDB_ADDRESS, token=token, org=org)
    write_api = dbclient.write_api(write_options=SYNCHRONOUS)

    client = Client("opc.tcp://192.168.2.99:4841/") # Initiate
    # Connect to Server
    client.connect()

    while True:
        try:
            if logFile == True:
                with open(filePath, 'w') as f:
                    f.write("Time[UTC],Module1_Temperature[*C],Module2_Temperature[*C],OptoBoard_Temperature[*C],Environment_Temperature[*C]\n")
                    f.close()

            # should always be in address space such as Root or Objects
            #root = client.get_root_node()
            #print("Objects node is: ", root)

            objects = client.get_objects_node()
            #print("Objects node is: ", objects)

            #################### Time in miliseconds UTC ##########################
            CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())
            OptoBoardTemp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan1"]).get_value()
            OptoBoardTemp = float(ConvAdc2Temp(OptoBoardTemp_ADC))

            Module1Temp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan2"]).get_value()
            Module1Temp = float(ConvAdc2Temp(Module1Temp_ADC))

            Module2Temp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan3"]).get_value()
            Module2Temp = float(ConvAdc2Temp(Module2Temp_ADC))

            EnvTemp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan4"]).get_value()
            EnvTemp = float(ConvAdc2Temp(EnvTemp_ADC))

            
            out_a = objects.get_child(["2:MonitorController","2:Frascati","2:OUT_S10","2:out_a"]).get_value()
            out_b = objects.get_child(["2:MonitorController","2:Frascati","2:OUT_S10","2:out_b"]).get_value()
            OUT_S10_state = "{:016b}".format(out_a)[::-1] + "{:016b}".format(out_b)[::-1]

            OUT_S10_C1 = int(OUT_S10_state[0])
            OUT_S10_C2 = int(OUT_S10_state[1])
            OUT_S10_C3 = int(OUT_S10_state[2])
            OUT_S10_C4 = int(OUT_S10_state[3])
            OUT_S10_C5 = int(OUT_S10_state[4])
            OUT_S10_C6 = int(OUT_S10_state[5])
            OUT_S10_C7 = int(OUT_S10_state[6])
            OUT_S10_C8 = int(OUT_S10_state[7])
            OUT_S10_C9 = int(OUT_S10_state[8])
            OUT_S10_C10 = int(OUT_S10_state[9])
            OUT_S10_C11 = int(OUT_S10_state[10])
            OUT_S10_C12 = int(OUT_S10_state[11])
            OUT_S10_C13 = int(OUT_S10_state[12])
            OUT_S10_C14 = int(OUT_S10_state[13])
            OUT_S10_C15 = int(OUT_S10_state[14])
            OUT_S10_C16 = int(OUT_S10_state[15])
            OUT_S10_C17 = int(OUT_S10_state[16])
            OUT_S10_C18 = int(OUT_S10_state[17])
            OUT_S10_C19 = int(OUT_S10_state[18])
            OUT_S10_C20 = int(OUT_S10_state[19])

            # Print all sensors data
            print('#################################################')
            print("Time: {}".format(CurrentTime))
            print("OptoBoard Temperature [*C]: {}".format(OptoBoardTemp))
            print("Module1 Temperature [*C]: {}".format(Module1Temp))
            print("Module2 Temperature [*C]: {}".format(Module2Temp))
            print("Environment Temperature [*C]: {}".format(EnvTemp))
            print("OUT_S10_status: {}".format(OUT_S10_state))

            if logFile == True:
                # Create data file header
                with open(filePath, 'a') as f:
                    f.write("{},{},{},{},{}\n".format(str(CurrentTime),
                                                    Module1Temp,
                                                    Module2Temp,
                                                    OptoBoardTemp,
                                                    EnvTemp))
                    f.close()
            # Container for DB
            influxdbContainer = []

            # Add OptoBoard Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "OptoBoard Temperature",
                    "tags": {
                        "OptoBoard" : 'NTC'
                    },
                    "time": CurrentTime,
                    "fields": {
                        "OptoBoard_Temperature[*C]" : OptoBoardTemp,
                    }
                }
            )
            # Add Environment Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "Environment Temperature",
                    "tags": {
                        "Environment" : 'NTC'
                    },
                    "time": CurrentTime,
                    "fields": {
                        "Environment_Temperature[*C]" : EnvTemp,
                    }
                }
            )
            # Add Module1 Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "Module1 Temperature",
                    "tags": {
                        "Module1" : 'NTC'
                    },
                    "time": CurrentTime,
                    "fields": {
                        "Module1_Temperature[*C]" : Module1Temp,
                    }
                }
            )
            # Add Module2 Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "Module2 Temperature",
                    "tags": {
                        "Module2" : 'NTC'
                    },
                    "time": CurrentTime,
                    "fields": {
                        "Module2_Temperature[*C]" : Module2Temp,
                    }
                }
            )
            # Add Interlock OUT_S10 ststus in DB
            influxdbContainer.append(
                {
                    "measurement": "OUT_S10",
                    "tags": {
                        "Interlock" : 'Status'
                    },
                    "time": CurrentTime,
                    "fields": {
                        "OUT_S10_C1" : OUT_S10_C1,
                        "OUT_S10_C2" : OUT_S10_C2,
                        "OUT_S10_C3" : OUT_S10_C3,
                        "OUT_S10_C4" : OUT_S10_C4,
                        "OUT_S10_C5" : OUT_S10_C5,
                        "OUT_S10_C6" : OUT_S10_C6,
                        "OUT_S10_C7" : OUT_S10_C7,
                        "OUT_S10_C8" : OUT_S10_C8,
                        "OUT_S10_C9" : OUT_S10_C9,
                        "OUT_S10_C10" : OUT_S10_C10,
                        "OUT_S10_C11" : OUT_S10_C11,
                        "OUT_S10_C12" : OUT_S10_C12,
                        "OUT_S10_C13" : OUT_S10_C13,
                        "OUT_S10_C14" : OUT_S10_C14,
                        "OUT_S10_C15" : OUT_S10_C15,
                        "OUT_S10_C16" : OUT_S10_C16,
                        "OUT_S10_C17" : OUT_S10_C17,
                        "OUT_S10_C18" : OUT_S10_C18,
                        "OUT_S10_C19" : OUT_S10_C19,
                        "OUT_S10_C20" : OUT_S10_C20,
                    }
                }
            )

            # Write All sensors data into DB
            write_api.write(bucket, org, influxdbContainer)
            # Delay of data taking

            time.sleep(Delay)

        except:
            print('##################### STOP ######################')
            os.kill(os.getpid(), 9)

except OSError:
    logging.error("No route to host!")

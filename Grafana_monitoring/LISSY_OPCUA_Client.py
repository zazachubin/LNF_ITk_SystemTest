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

def module_NTC_10K_formula(R):
    # NTC 10k
    A = 1.103026059e-03
    B = 2.203809745e-04
    C = 2.831203056e-07

    logR2 = math.log(R)
    T = (1.0 / (A + B*logR2 + C*logR2*logR2*logR2))
    Tc = T - 273.15
    return Tc
    
def NTC_10K_formula(R):
    # NTC 10k
    A = 1.098012950e-03
    B = 2.391408415e-04
    C = 0.7500259398e-07

    logR2 = math.log(R)
    T = (1.0 / (A + B*logR2 + C*logR2*logR2*logR2))
    Tc = T - 273.15
    return Tc


def ConvAdc2NTC_Res(adc_chan):
    Vout = 2.5/32767.0 * adc_chan
    Rntc = Vout * 10000/(2.5 - Vout)
    return Rntc

    

############################## InfluxDB ###############################
InfluxDB_ADDRESS = "http://localhost:8086"     # InfluxDB Local address
# You can generate an API token from the "API Tokens Tab" in the UI
token = "0xnV4c1Lfe1ZYMS41nPlJ66nb-c6XA7DUioX9iu8PeQC1Q2QoNJp2eCh8R3bx7pXlGtBpjY_Oh5TBzuAuCrP5w=="
org = "ITK"
bucket = "PixelSetup"

Delay = 1                                      # Device reading delay [s]

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
            objects = client.get_objects_node()
            #print("Objects node is: ", objects)

            #################### Time in miliseconds UTC ##########################
            CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())
            OptoBoardTemp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan1"]).get_value()
            OptoBoardTemp = round(float(module_NTC_10K_formula(ConvAdc2NTC_Res(OptoBoardTemp_ADC))),6)

            Module1Temp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan2"]).get_value()
            Module1Temp = round(float(module_NTC_10K_formula(ConvAdc2NTC_Res(Module1Temp_ADC))),6)

            Module2Temp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan3"]).get_value()
            Module2Temp = round(float(module_NTC_10K_formula(ConvAdc2NTC_Res(Module2Temp_ADC))),6)

            EnvTemp_ADC = objects.get_child(["2:MonitorController","2:Frascati","2:T2I_S3","2:t2i_adc1_chan4"]).get_value()
            EnvTemp = round(float(NTC_10K_formula(ConvAdc2NTC_Res(EnvTemp_ADC))),6)

            
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

            # Container for DB
            influxdbContainer = []

            # Add OptoBoard Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "OptoBoard",
                    "time": CurrentTime,
                    "fields": {
                        "OptoBoard_Temperature[*C]" : OptoBoardTemp,
                    }
                }
            )
            # Add Environment Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "Environment",
                    "time": CurrentTime,
                    "fields": {
                        "Environment_Temperature[*C]" : EnvTemp,
                    }
                }
            )
            # Add Module1 Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "Pixel_SP_Chain",
                    "time": CurrentTime,
                    "fields": {
                        "Module1_Temperature[*C]" : Module1Temp,
                    }
                }
            )
            # Add Module2 Temperature info in DB
            influxdbContainer.append(
                {
                    "measurement": "Pixel_SP_Chain",
                    "time": CurrentTime,
                    "fields": {
                        "Module2_Temperature[*C]" : Module2Temp,
                    }
                }
            )
            # Add Interlock OUT_S10 ststus in DB
            influxdbContainer.append(
                {
                    "measurement": "LYSSY_OUT_S10",
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

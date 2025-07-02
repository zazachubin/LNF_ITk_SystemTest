from datetime import datetime
from opcua import Server
from DAQ970A import DAQ970A
import pyvisa
import time

debug = False
delay = 0

class OPCUA_DAQ970A():
    def __init__(self, ipAddress, serverName):
        # Initialize the Server
        self.server = Server()

        # Set endpoint and self.server name
        self.server.set_endpoint(ipAddress)
        self.server.set_server_name(serverName)

        # Set up namespaces
        uri = "http://" + ipAddress.split('//')[1]
        idx = self.server.register_namespace(uri)

        # Create objects with nested structure
        root_obj = self.server.nodes.objects.add_object(idx, "DAQ970A")
        channels = root_obj.add_object(idx, "Channels")
        
        # create DPs structure for DAQ list of channels
        self.obj_list = []

        for i in range (20):
            if i+1 < 10:
                self.obj_list.append(channels.add_variable(idx, "Ch_10{}".format(i + 1), 0.0))
            elif i+1 == 10:
                self.obj_list.append(channels.add_variable(idx, "Ch_1{}".format(i + 1), 0.0))
            elif i+1 <= 20:
                self.obj_list.append(channels.add_variable(idx, "Ch_1{}".format(i + 1), 0.0))

        for i in range (20): 
            if i+1 < 10:
                self.obj_list.append(channels.add_variable(idx, "Ch_20{}".format(i + 1), 0.0))
            elif i+1 == 10:
                self.obj_list.append(channels.add_variable(idx, "Ch_2{}".format(i + 1), 0.0))
            elif i+1 <= 20:
                self.obj_list.append(channels.add_variable(idx, "Ch_2{}".format(i + 1), 0.0))

        for i in range (20): 
            if i+1 < 10:
                self.obj_list.append(channels.add_variable(idx, "Ch_30{}".format(i + 1), 0.0))
            elif i+1 == 10:
                self.obj_list.append(channels.add_variable(idx, "Ch_3{}".format(i + 1), 0.0))
            elif i+1 <= 20:
                self.obj_list.append(channels.add_variable(idx, "Ch_3{}".format(i + 1), 0.0))

        for item in self.obj_list:
            item.set_writable()

        # Start the self.server
        self.server.start()

    def sendDPs(self, data):
        i = 0
        for keys, value in data.items():
            self.obj_list[i].set_value(value)
            i = i + 1

    # Close OPC UA Server session
    def portTermination(self):
        self.server.stop()
    

#####################################################################
#####################################################################

if __name__ == "__main__":
    ###############################################################################
    ################################### DAQ #######################################
    ###############################################################################
    # DAQ IP address
    daq_port = "TCPIP::192.168.2.10::5025::SOCKET"

    # DAQ USB address
    #daq_port = 'USB0::10893::20481::MY58018576::0::INSTR'

    # List of DAQ channels
    daq_channels = [101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,
                    201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,
                    301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320]
    
    # List of DAQ channels parameters
    daq_measureParam = ['VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','RES','RES','VOLT:DC','RES','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES',
                        'RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES',
                        'RES','RES','RES','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES','RES']
    
    # List of DAQ active channels
    daq_channelsStatus = [True, True, True, False, True, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False,
                          False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                          False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]


    # DAQ
    daq = DAQ970A(daq_port, daq_channels, daq_measureParam, daq_channelsStatus)

    ###############################################################################
    ################################## OPCUA ######################################
    ###############################################################################

    ipAddress = "opc.tcp://localhost:4844/DAQ970A_opcua/server/"
    serverName = "DAQ970A OPCUA Server"

    opcDaq = OPCUA_DAQ970A(ipAddress, serverName)
    
    while True:
        time.sleep(delay)
        try:
            t0 = time.time()
            #################### Time in miliseconds UTC ##########################
            CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())

            # Print all sensors data
            print('#################################################')
            print("Time: {}".format(CurrentTime))

            daq.readChannels()
            daqData = daq.getDAQdata()
            print("DAQ DATA: {}\n".format(daqData))

            opcDaq.sendDPs(daqData)

            print("Readout Duration [s] {}".format(time.time() - t0))

            time.sleep(1)
        except pyvisa.errors.VisaIOError:
            print("Connect USB!")
        except ValueError:
            pass
        except KeyboardInterrupt:
            daq.portTermination()
            opcDaq.portTermination()
            print("STOP!")
            break
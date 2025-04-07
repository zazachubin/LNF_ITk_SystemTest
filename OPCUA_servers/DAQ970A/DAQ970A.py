from datetime import datetime
import pyvisa
import time

debug = False
delay = 1

class DAQ970A:
    def __init__(self, port, channels, measureParam, channelsStatus):

        self.channels =  channels
        self.measureParam = measureParam
        self.channelsStatus = channelsStatus

        # Data structure
        self.data ={101 : 0.0,
                    102 : 0.0,
                    103 : 0.0,
                    104 : 0.0,
                    105 : 0.0,
                    106 : 0.0,
                    107 : 0.0,
                    108 : 0.0,
                    109 : 0.0,
                    110 : 0.0,
                    111 : 0.0,
                    112 : 0.0,
                    113 : 0.0,
                    114 : 0.0,
                    115 : 0.0,
                    116 : 0.0,
                    117 : 0.0,
                    118 : 0.0,
                    119 : 0.0,
                    120 : 0.0,
                    201 : 0.0,
                    202 : 0.0,
                    203 : 0.0,
                    204 : 0.0,
                    205 : 0.0,
                    206 : 0.0,
                    207 : 0.0,
                    208 : 0.0,
                    209 : 0.0,
                    210 : 0.0,
                    211 : 0.0,
                    212 : 0.0,
                    213 : 0.0,
                    214 : 0.0,
                    215 : 0.0,
                    216 : 0.0,
                    217 : 0.0,
                    218 : 0.0,
                    219 : 0.0,
                    220 : 0.0,
                    301 : 0.0,
                    302 : 0.0,
                    303 : 0.0,
                    304 : 0.0,
                    305 : 0.0,
                    306 : 0.0,
                    307 : 0.0,
                    308 : 0.0,
                    309 : 0.0,
                    310 : 0.0,
                    311 : 0.0,
                    312 : 0.0,
                    313 : 0.0,
                    314 : 0.0,
                    315 : 0.0,
                    316 : 0.0,
                    317 : 0.0,
                    318 : 0.0,
                    319 : 0.0,
                    320 : 0.0}

        # Connect to DAQ system
        devObj=pyvisa.ResourceManager()

        if debug:
            self.getDevicesList(devObj)
        
        self.daq970=devObj.open_resource(port, timeout=10000, chunk_size=2048)
        self.daq970.read_termination = '\n'

        # Get Device model
        print(self.daq970.query('*IDN?'))

        # Reset Device
        self.daq970.write("*RST")
        self.daq970.write("*CLS")

        # Turn off beep
        self.daq970.write("SYST:BEEP:STATE OFF")

        # Configure Channels
        self.configChannels()
    # Get all available USB Devices
    def getDevicesList(self, devObj):
        print("Available Devices: {}".format(devObj.list_resources()))
    # Configure each DAQ channel
    def configChannels(self):
        self.activeChannelsList = []
        routingCommand = 'ROUTE:SCAN (@'
        for index in range(len(self.channels)):
            if self.channelsStatus[index] == True:
                channelsConfigCommand = 'CONF:{} (@{})'.format(self.measureParam[index], self.channels[index])
                self.daq970.write(channelsConfigCommand)

                routingCommand += '{},'.format(self.channels[index])
                self.activeChannelsList.append(self.channels[index])
                time.sleep(0.05)
                if debug:
                    print("Sent Command to {}".format(channelsConfigCommand))

        if True in self.channelsStatus:
            routingCommand = routingCommand[:len(routingCommand)-1] + ')'
            print(routingCommand)
            self.daq970.write(routingCommand)
    # Readout DAQ Channels
    def readChannels(self):
        channelsReadCommand = 'READ?'
        self.meas = self.daq970.query(channelsReadCommand).replace('\n','').split(',')
        if debug:
            print("Raw data: ->{}".format(self.meas))
        return self.meas
    # Retrive data
    def getDAQdata(self):
        for idx, item in enumerate(self.activeChannelsList):
            if debug:
                print('index: {} --> value: {} -- Status: {}'.format(idx, item, self.channelsStatus[idx]))
            self.data[item] = float(self.meas[idx])

        if debug:
            print("Full DAQ DATA per Channels\n {}".format(self.data))
        return self.data
    # Close DAQ comunication port
    def portTermination(self):
        self.daq970.close()

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
    daq_measureParam = ['VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES','RES','RES','RES','RES',
                        'RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES','RES',
                        'RES','RES','RES','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES','VOLT:DC','RES','RES','RES','RES']
    
    # List of DAQ active channels
    daq_channelsStatus = [False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, False,
                          False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
                          False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

    # DAQ
    daq = DAQ970A(daq_port, daq_channels, daq_measureParam, daq_channelsStatus)
    
    while True:
        time.sleep(delay)
        try:
            t0 = time.time()
            #################### Time in miliseconds UTC ##########################
            CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())

            # Print all sensors data
            print('#################################################')
            print("Time: {}".format(CurrentTime))

            # Read all configured channels data
            daq.readChannels()
            daqData = daq.getDAQdata()
            print("DAQ DATA: {}\n".format(daqData))

            print("Readout Duration [s] {}".format(time.time() - t0))
            time.sleep(1)
        except pyvisa.errors.VisaIOError:
            print("Connect USB!")
        except ValueError:
            pass
        except KeyboardInterrupt:
            daq.portTermination()
            print("")
            print("STOP!")
            break
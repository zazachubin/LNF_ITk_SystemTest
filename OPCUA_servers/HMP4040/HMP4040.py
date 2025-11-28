from datetime import datetime
from opcua import Server
from opcua import Client
import threading
import pyvisa
import time

debug = False
delay = 1

class HMP4040:
    def __init__(self, ps_name, deviceAddress):
        self.ps_name = ps_name
        self.deviceAddress = deviceAddress

        # Connect to HMP4040 system by LAN or USB
        devObj=pyvisa.ResourceManager()

        if debug:
            self.getDevicesList(devObj)

        self.hmp4040=devObj.open_resource(self.deviceAddress, timeout=10000)
        self.hmp4040.read_termination = '\n'

        ### RESET DEVICE
        #self.reset()
        ## Activate Remote control
        self.remoteMode(True)
        ## Get Device Model
        self.deviceModel()
    
    ## Return Device model
    def deviceModel(self):
        print(self.hmp4040.query('*IDN?'))
    
    ## Retun available devices through USB
    def getDevicesList(self, visaObj):
        print("Available Devices: {}".format(visaObj.list_resources()))
    
    ################ VOLTAGE FUNCTIONS ###############
    ## Set voltage
    def setVoltage(self, iChannel, fValue):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('SOUR:VOLT {}'.format(fValue))
    
    ## Get setting voltage
    def getVoltage(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return float(self.hmp4040.query('VOLT?'))

    ## Get Max voltage
    def getVoltageMax(self, iChannel):
        self.hmp4040.write('INST OUT {}'.format(iChannel))
        return float(self.hmp4040.query('VOLT? MAX'))

    ## Get Min voltage
    def getVoltageMin(self, iChannel):
        self.hmp4040.write('INST OUT {}'.format(iChannel))
        return float(self.hmp4040.query('VOLT? MIN'))

    ## Measure voltage
    def measVoltage(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return float(self.hmp4040.query('MEAS:VOLT?'))

    ################ CURRENT FUNCTIONS ###############
    ## Set current
    def setCurrent(self, iChannel, fValue):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('SOUR:CURR {}'.format(fValue))

    ## Get setting current
    def getCurrent(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return float(self.hmp4040.query('CURR?'))

    ## Get Max current
    def getCurrentMax(self, iChannel):
        self.hmp4040.write('INST OUT {}'.format(iChannel))
        return float(self.hmp4040.query('CURR? MAX'))

    ## Get Min current
    def getCurrentMin(self, iChannel):
        self.hmp4040.write('INST OUT {}'.format(iChannel))
        return float(self.hmp4040.query('CURR? MIN'))

    ## Measure Current
    def measCurrent(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return float(self.hmp4040.query('MEAS:CURR?'))

    ################ OUTPUT FUNCTIONS ################
    ## Set individual channels output status
    def setOutput(self, iChannel, bEnable):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('OUTP {:d}'.format(bEnable))

    ## Get individual channels output status
    def getOutput(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        status = self.hmp4040.query('OUTP?')
        if status == '1':
            return True
        elif status == '0':
            return False

    ## Set Global power OUTPUT Button status
    def enablePower(self, bValue):
        self.hmp4040.write('OUTP:GEN {0:d}'.format(bValue))

    ## Get Global power OUTPUT Button status
    def getEnablePower(self):
        status = self.hmp4040.query('OUTP:GEN?')
        if status == '1':
            return True
        elif status == '0':
            return False

    ################## OVP FUNCTIONS #################
    ## Set Over voltage protection Limit
    def setOVPLimit(self, iChannel, fValue):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('VOLT:PROT {}'.format(fValue))

    ## Get Over voltage protection Limit
    def getOVPLimit(self, iChannel):
        self.hmp4040.write('INST OUT {}'.format(iChannel))
        return float(self.hmp4040.query('VOLT:PROT?'))

    ## Get Over voltage protection the upper Limit
    def getOVP_MAX_Limit(self, iChannel):
        self.hmp4040.write('INST OUT {}'.format(iChannel))
        return float(self.hmp4040.query('VOLT:PROT? MAX'))

    ## Get Over voltage protection the lower Limit
    def getOVP_MIN_Limit(self, iChannel):
        self.hmp4040.write('INST OUT {}'.format(iChannel))
        return float(self.hmp4040.query('VOLT:PROT? MIN'))

    ## Resets a tripped OVP in the selected channel
    def setOVP_Clear(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('VOLT:PROT:CLE')

    ## Get the OVP channels output trip status
    def getOVP_Trip(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        status = self.hmp4040.query('VOLT:PROT:TRIP?')
        if status == '1':
            return True
        elif status == '0':
            return False

    ## Set over VOLTAGE Protection MODE (mode='MEAS' or mode='PROT')
    def setOVP_Mode(self, iChannel, mode='MEAS'):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('SOUR:VOLT:PROT:MODE {}'.format(mode))

    ## Get over VOLTAGE Protection MODE
    def getOVP_Mode(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return self.hmp4040.query('VOLT:PROT:MODE PROT?')

    ## Resets the OVP state of the selected channel
    def resetOVPstate(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('VOLT:PROT:CLE')

    ################# FUSE FUNCTIONS #################
    ## Set Fuse Delay in min
    def setFuseDelay(self, iChannel, delayms):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('FUSE:DEL {}'.format(delayms))

    ## Get Fuse Delay
    def getFuseDelay(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return int(self.hmp4040.query('FUSE:DEL?'))
    
    ## Get Fuse Delay Max
    def getFuseDelayMax(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return int(self.hmp4040.query('FUSE:DEL? MAX'))
    
    ## Get Fuse Delay Min
    def getFuseDelayMin(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return int(self.hmp4040.query('FUSE:DEL? MIN'))

    ## Set Fuse Link
    def setFuseLink(self, iChannel, linkChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('FUSE:LINK {}'.format(linkChannel))

    ## Get Fuse Link
    def getFuseLink(self, iChannel, linkChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        return int (self.hmp4040.query('FUSE:LINK? {}'.format(linkChannel)))

    ## Dissolve the link of the electronic fuses
    def setFuseUnLink(self, iChannel, linkChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        self.hmp4040.write('FUSE:UNL {}'.format(linkChannel))

    ## Set Fuse State
    def setFuseState(self, iChannel, onOff=False):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        if onOff:
            self.hmp4040.write('FUSE:STATE ON')
        else:
            self.hmp4040.write('FUSE:STATE OFF')
    
    ## Get Fuse State
    def getFuseState(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        status = self.hmp4040.query('FUSE?')
        if status == '1':
            return True
        elif status == '0':
            return False
    
    ## Get Fuse Tripped Status
    def getFuseTripped(self, iChannel):
        self.hmp4040.write('INST OUT{}'.format(iChannel))
        status = self.hmp4040.query('FUSE:TRIPPED?')
        if status == '1':
            return True
        elif status == '0':
            return False

    ############### GENERAL FUNCTIONS ################
    ## Set Remote MODE status
    def remoteMode(self, status=False):
        if status:
            self.hmp4040.write('SYSTEM:REMOTE')
        else:
            self.hmp4040.write('SYST:LOC')

    ## Reset Device
    def reset(self):
        self.hmp4040.write("*RST")
        self.hmp4040.write("*CLS")
    
    ## Get device Channels basic info
    def getInfo(self):
        print("****************************")
        for ch in range(4):
            # Get Channels set voltage-current
            print("Ch{} -- Get: Voltage: {}, Current: {}".format(ch+1, self.getVoltage(ch+1), self.getCurrent(ch+1)))
            print("Ch{} -- Measure: Voltage: {}, Current: {}".format(ch+1, self.measVoltage(ch+1), self.measCurrent(ch+1)))        

    ## Terminate the Device
    def portTermination(self):
        for ch in range(1, 5):
            self.setOutput(ch, False)
        self.enablePower(False)
        self.remoteMode(False)
        self.hmp4040.close()

if __name__ == "__main__":
    ###############################################################################
    ################################### HMP4040 ###################################
    ###############################################################################
    ## LAN Device
    deviceAddress = "TCPIP::192.168.2.30::5025::SOCKET"
    #deviceAddress = "TCPIP::192.168.2.20::5025::SOCKET"

    ## USB Device
    #deviceAddress = 'ASRL/dev/ttyACM0::INSTR'

    #deviceAddress = 'ASRL/dev/ttyUSB0::INSTR'

    hmp4040 = HMP4040('ps1', deviceAddress)

    #hmp4040.setOutput(1, True)
    #hmp4040.setOutput(1, False)

    while True:
        time.sleep(delay)
        try:
            t0 = time.time()
            #################### Time in miliseconds UTC ##########################
            CurrentTime = datetime.fromtimestamp(datetime.utcnow().timestamp())

            # Print all sensors data
            print('#################################################')
            print("Time: {}".format(CurrentTime))

            hmp4040.getInfo()

            print("Readout Duration [s] {}".format(time.time() - t0))

            time.sleep(1)
        except pyvisa.errors.VisaIOError:
            print("Connect USB!")
        except ValueError:
            pass
        except KeyboardInterrupt:
            hmp4040.portTermination()
            print("STOP!")
            break
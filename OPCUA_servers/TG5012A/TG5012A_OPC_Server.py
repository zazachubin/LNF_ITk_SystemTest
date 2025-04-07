from opcua import Server
import pyvisa
import time

debug = False
delay = 1

class TG5012A:
    def __init__(self, gen_name, deviceAddress):
        self.gen_name = gen_name
        self.deviceAddress = deviceAddress
        # Connect to TG5012A system by LAN
        devObj=pyvisa.ResourceManager()

        if debug:
            self.getDevicesList(devObj)

        self.tg5012A=devObj.open_resource(self.deviceAddress, timeout=10000)
        self.tg5012A.read_termination = '\n'

        print(self.tg5012A.query('*IDN?'))

    def setAmplitude(self, ch, amplitude):
        self.tg5012A.write("CHN {}".format(ch))
        self.tg5012A.write("AMPUNIT VPP")
        self.tg5012A.write("AMPL {}".format(amplitude))

    def setDCoffset(self, ch, dc_Offset):
        self.tg5012A.write("CHN {}".format(ch))
        self.tg5012A.write("DCOFFS {}".format(dc_Offset))
        
    def setFrequency(self, ch, frequency):
        self.tg5012A.write("CHN {}".format(ch))
        self.tg5012A.write("FREQ {}".format(frequency))
    
    def setWaveForm(self, ch, waveForm):
        self.tg5012A.write("CHN {}".format(ch))
        self.tg5012A.write("WAVE {}".format(waveForm))

    def setDutyCycle(self, ch, dutyCycle):
        self.tg5012A.write("CHN {}".format(ch))
        self.tg5012A.write("SQRSYMM {}".format(dutyCycle))
    
    def setPhase(self, ch, phase):
        self.tg5012A.write("CHN {}".format(ch))
        self.tg5012A.write("PHASE {}".format(phase))
    
    def setCh_On_Off(self, ch, status):
        self.tg5012A.write("CHN {}".format(ch))
        if status:
            self.tg5012A.write("OUTPUT ON")
        else:
            self.tg5012A.write("OUTPUT OFF")

    def setZLOAD(self, ch, ZLOAD):
        self.tg5012A.write("CHN {}".format(ch))
        self.tg5012A.write("ZLOAD {}".format(ZLOAD))

    def setBEEPMODE(self, status):
        self.tg5012A.write("BEEPMODE {}".format(status))

    def reset(self):
        self.tg5012A.write("*RST")
        self.tg5012A.write("*CLS")

    def getDevicesList(self, devObj):
        print("Available Devices: {}".format(devObj.list_resources()))

    def portTermination(self):
        self.tg5012A.close()


class OPCUA_TG5012A():
    def __init__(self, ipAddress, serverName, gen_list):
        # signal Generators device list
        self.gen_list = gen_list

        for gen in self.gen_list:
            gen.setBEEPMODE('OFF')
            
            for ch in range(1, 3):
                gen.setWaveForm(ch, 'SQUARE')
                gen.setFrequency(ch, 100000)
                gen.setAmplitude(ch, 1.2)
                gen.setDCoffset(ch, 0)
                gen.setDutyCycle(ch, 50)
                gen.setPhase(ch, 0)
                gen.setZLOAD(ch, '50')
                #gen.setZLOAD(ch, 'OPEN')

                #gen.setCh_On_Off(ch, 'ON')
                gen.setCh_On_Off(ch, 'OFF')

            gen.tg5012A.write("LOCAL")

        # Initialize the self.server
        self.server = Server()

        # Set endpoint and self.server name
        self.server.set_endpoint(ipAddress)
        self.server.set_server_name(serverName)

        # Set up namespaces
        uri = "http://" + ipAddress.split('//')[1]
        self.idx = self.server.register_namespace(uri)

        # Create Data points structure for power supply decices
        self.createDPs_structure()
        ###
        ###
        ###
        # Start the OPC UA server
        print("Starting OPC UA Server...")

        self.server.start()

        self.createDPs_EventList()

    # Create Data points structure for Signal Generator devices
    def createDPs_structure(self):
        # Pre defined DPs structure for PS
        data = {'channel1': {'OutputStatus': False},
                'channel2': {'OutputStatus': False}
                }

        # Create root object in OPC UA server
        for gen in self.gen_list:
            self.root_node = self.server.nodes.objects.add_object(self.idx, gen.gen_name)
            # Convert dictionary to OPC UA nodes
            self.create_opcua_variables(self.root_node, data, self.server, self.idx)

    # Function to create OPC UA variables from a nested dictionary
    def create_opcua_variables(self, parent_node, data_dict, server, namespace_idx):
        """
        Recursively creates OPC UA variables from a nested dictionary.

        :param parent_node: The parent OPC UA node to attach variables to.
        :param data_dict: The nested dictionary containing data.
        :param server: The OPC UA server instance.
        :param namespace_idx: The namespace index for creating nodes.
        """
        for key, value in data_dict.items():
            if isinstance(value, dict):
                # Create a new folder for nested dictionary
                new_node = parent_node.add_object(namespace_idx, key)
                self.create_opcua_variables(new_node, value, server, namespace_idx)
            else:
                # Create a variable for a single value
                var_node = parent_node.add_variable(namespace_idx, key, value)
                var_node.set_writable()  # Allow clients to write to this variable

    # Select the DPs for data change events
    def createDPs_EventList(self):
        objects = self.server.get_objects_node()
        handlers = []
        for gen in self.gen_list:
            handlers.append(SubHandler(self.gen_list))
            sub = self.server.create_subscription(100, handlers[-1])

            for ch in range(1, 3):
                sub.subscribe_data_change(objects.get_child(["2:{}".format(gen.gen_name), "2:channel{}".format(ch), "2:OutputStatus"]))

    # Close Server
    def serverTermination(self):
        self.server.stop()
        for gen in self.gen_list:
            gen.portTermination()

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    This class is just a sample class. Whatever class having these methods can be used
    """
    def __init__(self, gen_list):
        self.gen_list = gen_list

    def get_full_node_path(self, node):
        path = []
        while node:
            path.insert(0, node.get_browse_name().Name)
            try:
                node = node.get_parent()
            except:
                break  # Stop when there's no parent
        return "/".join(path)  # Return full path as text
    
    def datachange_notification(self, node, val, data):
        """
        called for every datachange notification from server
        """
        full_path = self.get_full_node_path(node)
        print("Data changed:" + full_path)

        selected_gen_name = full_path.split('/')[2]
        selected_channel = full_path.split('/')[3]
        selected_param = full_path.split('/')[4]

        for gen in self.gen_list:
            if selected_gen_name == gen.gen_name:
                if selected_param == "OutputStatus":
                    if selected_channel == "channel1":
                        gen.setCh_On_Off(1, val)
                    elif selected_channel == "channel2":
                        gen.setCh_On_Off(2, val)

#####################################################################
#####################################################################


if __name__ == "__main__":
    ###############################################################################
    ############################ TG5012A OPC UA Server ############################
    ###############################################################################
    ## LAN Device
    ps_devices = {"gen1" : "TCPIP::192.168.2.50::9221::SOCKET"}

    gen_list = []
    for key, value in ps_devices.items():
        gen_list.append(TG5012A(key, value))

    #######
    ### OPC UA Server Config
    ipAddress = "opc.tcp://localhost:4842/TG5012A_opcua/server/"
    serverName = "TG5012A OPC UA Server"
    tg5012a_opcua = OPCUA_TG5012A(ipAddress, serverName, gen_list)

    try:
        while True:
            time.sleep(delay)
            pass
    except KeyboardInterrupt:
        print("")
        tg5012a_opcua.serverTermination()
        print("Stopping OPC UA Server...")
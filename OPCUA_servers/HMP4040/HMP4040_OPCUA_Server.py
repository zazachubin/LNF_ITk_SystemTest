from opcua import Server
from opcua import Client
import threading
from HMP4040 import HMP4040
import time

class OPCUA_HMP4040():
    def __init__(self, ipAddress, serverName, ps_list):
        # Power supply device list
        self.ps_list = ps_list

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

        # Initialize datapoints
        self.initializeDps()
        ###
        ###
        ###
        # Start the OPC UA server
        print("Starting OPC UA Server...")

        self.server.start()

        self.createDPs_EventList()

    # Create Data points structure for power supply decices
    def createDPs_structure(self):
        # Pre defined DPs structure for PS
        data = {'channel1': { 'actual': { 'fuseTrip': False,
                                        'iMon': 0.0,
                                        'isOn': False,
                                        'trip': False,
                                        'vMon' : 0.0},

                            'readbackSettings':{'fuseDelay': 0,
                                                'fuseLink' : 0,
                                                'fuseOnOff' : False,
                                                'i0': 0.0,
                                                'iRangeMax' : 0.0,
                                                'iRangeMin' : 0.0,
                                                'onOff' : False,
                                                'v0' : 0.0,
                                                'vProtectionLevel' : 0.0,
                                                'vProtectionMode' : '',
                                                'vRangeMax' : 0.0,
                                                'vRangeMin' : 0.0},

                            'settings' : {  'clearTrip': False,
                                            'fuseDelay' : 0,
                                            'fuseLink' : 0,
                                            'fuseOnOff' : False,
                                            'fuseUnlink' : False,
                                            'i0' : 0.0,
                                            'onOff' : False,
                                            'v0' : 0.0,
                                            'vProtectionLevel' : 0.0,
                                            'vProtectionMode' : '',}},

                'channel2': { 'actual': { 'fuseTrip': False,
                                        'iMon': 0.0,
                                        'isOn': False,
                                        'trip': False,
                                        'vMon' : 0.0},

                            'readbackSettings':{'fuseDelay': 0,
                                                'fuseLink' : 0,
                                                'fuseOnOff' : False,
                                                'i0': 0.0,
                                                'iRangeMax' : 0.0,
                                                'iRangeMin' : 0.0,
                                                'onOff' : False,
                                                'v0' : 0.0,
                                                'vProtectionLevel' : 0.0,
                                                'vProtectionMode' : '',
                                                'vRangeMax' : 0.0,
                                                'vRangeMin' : 0.0},

                            'settings' : {  'clearTrip': False,
                                            'fuseDelay' : 0,
                                            'fuseLink' : 0,
                                            'fuseOnOff' : False,
                                            'fuseUnlink' : False,
                                            'i0' : 0.0,
                                            'onOff' : False,
                                            'v0' : 0.0,
                                            'vProtectionLevel' : 0.0,
                                            'vProtectionMode' : '',}},

                'channel3': { 'actual': { 'fuseTrip': False,
                                        'iMon': 0.0,
                                        'isOn': False,
                                        'trip': False,
                                        'vMon' : 0.0},

                            'readbackSettings':{'fuseDelay': 0,
                                                'fuseLink' : 0,
                                                'fuseOnOff' : False,
                                                'i0': 0.0,
                                                'iRangeMax' : 0.0,
                                                'iRangeMin' : 0.0,
                                                'onOff' : False,
                                                'v0' : 0.0,
                                                'vProtectionLevel' : 0.0,
                                                'vProtectionMode' : '',
                                                'vRangeMax' : 0.0,
                                                'vRangeMin' : 0.0},

                            'settings' : {  'clearTrip': False,
                                            'fuseDelay' : 0,
                                            'fuseLink' : 0,
                                            'fuseOnOff' : False,
                                            'fuseUnlink' : False,
                                            'i0' : 0.0,
                                            'onOff' : False,
                                            'v0' : 0.0,
                                            'vProtectionLevel' : 0.0,
                                            'vProtectionMode' : '',}},

                'channel4': { 'actual': { 'fuseTrip': False,
                                        'iMon': 0.0,
                                        'isOn': False,
                                        'trip': False,
                                        'vMon' : 0.0},

                            'readbackSettings':{'fuseDelay': 0,
                                                'fuseLink' : 0,
                                                'fuseOnOff' : False,
                                                'i0': 0.0,
                                                'iRangeMax' : 0.0,
                                                'iRangeMin' : 0.0,
                                                'onOff' : False,
                                                'v0' : 0.0,
                                                'vProtectionLevel' : 0.0,
                                                'vProtectionMode' : '',
                                                'vRangeMax' : 0.0,
                                                'vRangeMin' : 0.0},

                            'settings' : {  'clearTrip': False,
                                            'fuseDelay' : 0,
                                            'fuseLink' : 0,
                                            'fuseOnOff' : False,
                                            'fuseUnlink' : False,
                                            'i0' : 0.0,
                                            'onOff' : False,
                                            'v0' : 0.0,
                                            'vProtectionLevel' : 0.0,
                                            'vProtectionMode' : '',}}
            }
        # Create root object in OPC UA server
        for ps in self.ps_list:
            self.root_node = self.server.nodes.objects.add_object(self.idx, ps.ps_name)
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

                #var_node.set_read_only()

    # Initialize datapoints
    def initializeDps(self):
        objects = self.server.get_objects_node()
        for ps in self.ps_list:
            for ch in range(1, 5):
                objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:settings", "2:onOff"]).set_value(ps.getOutput(ch))
                objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:settings", "2:v0"]).set_value(ps.getVoltage(ch))
                objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:settings", "2:i0"]).set_value(ps.getCurrent(ch))

    # Select the DPs for data change events
    def createDPs_EventList(self):
        objects = self.server.get_objects_node()
        handlers = []
        for ps in self.ps_list:
            handlers.append(SubHandler(self.ps_list))
            sub = self.server.create_subscription(100, handlers[-1])

            for ch in range(1, 5):
                sub.subscribe_data_change(objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:settings", "2:onOff"]))
                sub.subscribe_data_change(objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:settings", "2:v0"]))
                sub.subscribe_data_change(objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:settings", "2:i0"]))
    
    # Read Back Settings update to ReadbackSettings DPs
    def readbackSettings(self, ps):
        objects = self.server.get_objects_node()
        for ch in range(1, 5):
            ## ReadbackSettings
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:v0"]).set_value(ps.getVoltage(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:i0"]).set_value(ps.getCurrent(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:vRangeMax"]).set_value(ps.getVoltageMax(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:vRangeMin"]).set_value(ps.getVoltageMin(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:iRangeMax"]).set_value(ps.getCurrentMax(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:iRangeMin"]).set_value(ps.getCurrentMin(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:onOff"]).set_value(ps.getOutput(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:fuseDelay"]).set_value(ps.getFuseDelay(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:fuseOnOff"]).set_value(ps.getFuseState(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:vProtectionMode"]).set_value(ps.getOVP_Mode(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:readbackSettings", "2:vProtectionLevel"]).set_value(ps.getOVPLimit(ch))

    # Actual petrics update to actual DPs
    def actual(self, ps):
        objects = self.server.get_objects_node()
        for ch in range(1, 5):
            ## Actual
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:actual", "2:vMon"]).set_value(ps.measVoltage(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:actual", "2:iMon"]).set_value(ps.measCurrent(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:actual", "2:isOn"]).set_value(ps.getOutput(ch))
            #objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:actual", "2:trip"]).set_value(ps.getOVPtrip(ch))
            objects.get_child(["2:{}".format(ps.ps_name), "2:channel{}".format(ch), "2:actual", "2:fuseTrip"]).set_value(ps.getFuseTripped(ch))

    # Monitoring
    def monitoring(self, ps):
        while True:
            self.actual(ps)
            self.readbackSettings(ps)

    # Close Server
    def serverTermination(self):
        self.server.stop()
        for ps in self.ps_list:
            ps.portTermination()

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    This class is just a sample class. Whatever class having these methods can be used
    """
    def __init__(self, ps_list):
        self.ps_list = ps_list

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

        selected_ps_name = full_path.split('/')[2]
        selected_channel = full_path.split('/')[3]
        selected_param = full_path.split('/')[5]


        for ps in self.ps_list:
            if selected_ps_name == ps.ps_name:
                if selected_param == "onOff":
                    if selected_channel == "channel1":
                        ps.setOutput(1, val)
                    elif selected_channel == "channel2":
                        ps.setOutput(2, val)
                    elif selected_channel == "channel3":
                        ps.setOutput(3, val)
                    elif selected_channel == "channel4":
                        ps.setOutput(4, val)

                elif selected_param == "v0":
                    if selected_channel == "channel1":
                        ps.setVoltage(1, val)
                    elif selected_channel == "channel2":
                        ps.setVoltage(2, val)
                    elif selected_channel == "channel3":
                        ps.setVoltage(3, val)
                    elif selected_channel == "channel4":
                        ps.setVoltage(4, val)
                
                elif selected_param == "i0":
                    if selected_channel == "channel1":
                        ps.setCurrent(1, val)
                    elif selected_channel == "channel2":
                        ps.setCurrent(2, val)
                    elif selected_channel == "channel3":
                        ps.setCurrent(3, val)
                    elif selected_channel == "channel4":
                        ps.setCurrent(4, val)


if __name__ == "__main__":
    ###############################################################################
    ############################ HMP4040 OPC UA Server ############################
    ###############################################################################
    ## USB Device
    #ps_devices = {"ps1" : "ASRL/dev/ttyACM0::INSTR",
    #              "ps2" : "ASRL/dev/ttyUSB0::INSTR"}

    ## LAN Device
    ps_devices = {"ps1" : "TCPIP::192.168.2.30::5025::SOCKET",
                  "ps2" : "TCPIP::192.168.2.20::5025::SOCKET"}

    ps_list = []
    for key, value in ps_devices.items():
        ps_list.append(HMP4040(key, value))

    #######
    #######
    #######
    ### OPC UA Server Config
    ipAddress = "opc.tcp://localhost:4843/HMP4040_opcua/server/"
    serverName = "HMP4040 OPC UA Server"
    hmp4040_opcua = OPCUA_HMP4040(ipAddress, serverName, ps_list)

    # Starting threads for each PS
    threads = []
    for ps in ps_list:
        t = threading.Thread(target=hmp4040_opcua.monitoring, args=(ps,))
        t.daemon = True
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        print("")
        hmp4040_opcua.serverTermination()
        print("Stopping OPC UA Server...")
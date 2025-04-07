import os
import subprocess

from opcua import Server
from datetime import datetime
import time

felixInfo = {"OpticalLinksAlignment" : {"Ch1":False,
                                        "Ch2":False,
                                        "Ch3":False,
                                        "Ch4":False,
                                        "Ch5":False,
                                        "Ch6":False,
                                        "Ch7":False,
                                        "Ch8":False,
                                        "Ch9":False,
                                        "Ch10":False,
                                        "Ch11":False,
                                        "Ch12":False},

            "ElinksAlignment" : {"DECODING_LINK_ALIGNED_00" :{"Ch1" : False,
                                            "Ch2" : False,
                                            "Ch3" : False,
                                            "Ch4" : False,
                                            "Ch5" : False,
                                            "Ch6" : False},

                                "DECODING_LINK_ALIGNED_01" : {"Ch1" : False,
                                            "Ch2" : False,
                                            "Ch3" : False,
                                            "Ch4" : False,
                                            "Ch5" : False,
                                            "Ch6" : False},

                                "DECODING_LINK_ALIGNED_02" : {"Ch1" : False,
                                            "Ch2" : False,
                                            "Ch3" : False,
                                            "Ch4" : False,
                                            "Ch5" : False,
                                            "Ch6" : False},

                                "DECODING_LINK_ALIGNED_03" : {"Ch1" : False,
                                            "Ch2" : False,
                                            "Ch3" : False,
                                            "Ch4" : False,
                                            "Ch5" : False,
                                            "Ch6" : False}
                                            }}

def elinkSelector(text, lineIndex, channel):
    lpGBT = text.split("\n")[lineIndex].split("DECODING_LINK_ALIGNED_0{}  ".format(str(channel)))[1].replace("  Every bit corresponds to an E-link on one (lp)GBT or FULL-mode", "")
    return lpGBT

def elinksStatus(lpGBT, lpGBT_name):
    if lpGBT[16] == "1":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch1"] = True
    elif lpGBT[16] == "0":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch1"] = False

    if lpGBT[15] == "1":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch2"] = True
    elif lpGBT[15] == "0":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch2"] = False

    if lpGBT[14] == "1":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch3"] = True
    elif lpGBT[14] == "0":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch3"] = False

    if lpGBT[13] == "1":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch4"] = True
    elif lpGBT[13] == "0":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch4"] = False

    if lpGBT[12] == "1":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch5"] = True
    elif lpGBT[12] == "0":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch5"] = False

    if lpGBT[11] == "1":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch6"] = True
    elif lpGBT[11] == "0":
        felixInfo["ElinksAlignment"][lpGBT_name]["Ch6"] = False

def opticalAlignmentStatus(text):
    stringList = text.split("\n")[2].split("| ")[1].split("  ")

    for i, val in enumerate(stringList):
        if "YES" in val:
            felixInfo["OpticalLinksAlignment"]["Ch{}".format(i+1)] = True
        elif "NO" in val:
            felixInfo["OpticalLinksAlignment"]["Ch{}".format(i+1)] = False

def readFelixInfo():
    cmd = "source /home/felix/opt/LNF_ITk_SyestemTest/OPCUA_servers/Optoboard2FelixInfo/FelixInfo.sh"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

    DECODING_LINK_ALIGNED_00 = elinkSelector(result.stdout, 4, 0)
    DECODING_LINK_ALIGNED_01 = elinkSelector(result.stdout, 5, 1)
    DECODING_LINK_ALIGNED_02 = elinkSelector(result.stdout, 6, 2)
    DECODING_LINK_ALIGNED_03 = elinkSelector(result.stdout, 7, 3)

    elinksStatus(DECODING_LINK_ALIGNED_00, "DECODING_LINK_ALIGNED_00")
    elinksStatus(DECODING_LINK_ALIGNED_01, "DECODING_LINK_ALIGNED_01")
    elinksStatus(DECODING_LINK_ALIGNED_02, "DECODING_LINK_ALIGNED_02")
    elinksStatus(DECODING_LINK_ALIGNED_03, "DECODING_LINK_ALIGNED_03")

    opticalAlignmentStatus(result.stdout)

ipAddress = "opc.tcp://localhost:4840/FelixInfo_opcua/server/"

# Initialize the server
server = Server()

# Set endpoint and server name
server.set_endpoint(ipAddress)
server.set_server_name("Nested Structure OPC UA Server")

# Set up namespaces
# Set up namespaces
uri = "http://" + ipAddress.split('//')[1]
idx = server.register_namespace(uri)

# Create objects with nested structure
root_obj = server.nodes.objects.add_object(idx, "FelixInfo")

# Add a nested structure
opticalAlignment = root_obj.add_object(idx, "OpticalLinksAlignment")
elinksAlignment = root_obj.add_object(idx, "ElinksAlignment")

# Add variables in the nested object
opticalAlignment_Ch1 = opticalAlignment.add_variable(idx, "Ch1", False)
opticalAlignment_Ch2 = opticalAlignment.add_variable(idx, "Ch2", False)
opticalAlignment_Ch3 = opticalAlignment.add_variable(idx, "Ch3", False)
opticalAlignment_Ch4 = opticalAlignment.add_variable(idx, "Ch4", False)
opticalAlignment_Ch5 = opticalAlignment.add_variable(idx, "Ch5", False)
opticalAlignment_Ch6 = opticalAlignment.add_variable(idx, "Ch6", False)
opticalAlignment_Ch7 = opticalAlignment.add_variable(idx, "Ch7", False)
opticalAlignment_Ch8 = opticalAlignment.add_variable(idx, "Ch8", False)
opticalAlignment_Ch9 = opticalAlignment.add_variable(idx, "Ch9", False)
opticalAlignment_Ch10 = opticalAlignment.add_variable(idx, "Ch10", False)
opticalAlignment_Ch11 = opticalAlignment.add_variable(idx, "Ch11", False)
opticalAlignment_Ch12 = opticalAlignment.add_variable(idx, "Ch12", False)


DECODING_LINK_ALIGNED_00 = elinksAlignment.add_object(idx, "DECODING_LINK_ALIGNED_00")
DECODING_LINK_ALIGNED_01 = elinksAlignment.add_object(idx, "DECODING_LINK_ALIGNED_01")
DECODING_LINK_ALIGNED_02 = elinksAlignment.add_object(idx, "DECODING_LINK_ALIGNED_02")
DECODING_LINK_ALIGNED_03 = elinksAlignment.add_object(idx, "DECODING_LINK_ALIGNED_03")


DECODING_LINK_ALIGNED_00_Ch1 = DECODING_LINK_ALIGNED_00.add_variable(idx, "Ch1", False)
DECODING_LINK_ALIGNED_00_Ch2 = DECODING_LINK_ALIGNED_00.add_variable(idx, "Ch2", False)
DECODING_LINK_ALIGNED_00_Ch3 = DECODING_LINK_ALIGNED_00.add_variable(idx, "Ch3", False)
DECODING_LINK_ALIGNED_00_Ch4 = DECODING_LINK_ALIGNED_00.add_variable(idx, "Ch4", False)
DECODING_LINK_ALIGNED_00_Ch5 = DECODING_LINK_ALIGNED_00.add_variable(idx, "Ch5", False)
DECODING_LINK_ALIGNED_00_Ch6 = DECODING_LINK_ALIGNED_00.add_variable(idx, "Ch6", False)

DECODING_LINK_ALIGNED_01_Ch1 = DECODING_LINK_ALIGNED_01.add_variable(idx, "Ch1", False)
DECODING_LINK_ALIGNED_01_Ch2 = DECODING_LINK_ALIGNED_01.add_variable(idx, "Ch2", False)
DECODING_LINK_ALIGNED_01_Ch3 = DECODING_LINK_ALIGNED_01.add_variable(idx, "Ch3", False)
DECODING_LINK_ALIGNED_01_Ch4 = DECODING_LINK_ALIGNED_01.add_variable(idx, "Ch4", False)
DECODING_LINK_ALIGNED_01_Ch5 = DECODING_LINK_ALIGNED_01.add_variable(idx, "Ch5", False)
DECODING_LINK_ALIGNED_01_Ch6 = DECODING_LINK_ALIGNED_01.add_variable(idx, "Ch6", False)

DECODING_LINK_ALIGNED_02_Ch1 = DECODING_LINK_ALIGNED_02.add_variable(idx, "Ch1", False)
DECODING_LINK_ALIGNED_02_Ch2 = DECODING_LINK_ALIGNED_02.add_variable(idx, "Ch2", False)
DECODING_LINK_ALIGNED_02_Ch3 = DECODING_LINK_ALIGNED_02.add_variable(idx, "Ch3", False)
DECODING_LINK_ALIGNED_02_Ch4 = DECODING_LINK_ALIGNED_02.add_variable(idx, "Ch4", False)
DECODING_LINK_ALIGNED_02_Ch5 = DECODING_LINK_ALIGNED_02.add_variable(idx, "Ch5", False)
DECODING_LINK_ALIGNED_02_Ch6 = DECODING_LINK_ALIGNED_02.add_variable(idx, "Ch6", False)

DECODING_LINK_ALIGNED_03_Ch1 = DECODING_LINK_ALIGNED_03.add_variable(idx, "Ch1", False)
DECODING_LINK_ALIGNED_03_Ch2 = DECODING_LINK_ALIGNED_03.add_variable(idx, "Ch2", False)
DECODING_LINK_ALIGNED_03_Ch3 = DECODING_LINK_ALIGNED_03.add_variable(idx, "Ch3", False)
DECODING_LINK_ALIGNED_03_Ch4 = DECODING_LINK_ALIGNED_03.add_variable(idx, "Ch4", False)
DECODING_LINK_ALIGNED_03_Ch5 = DECODING_LINK_ALIGNED_03.add_variable(idx, "Ch5", False)
DECODING_LINK_ALIGNED_03_Ch6 = DECODING_LINK_ALIGNED_03.add_variable(idx, "Ch6", False)

# Make variables writable
opticalAlignment_Ch1.set_writable()
opticalAlignment_Ch2.set_writable()
opticalAlignment_Ch3.set_writable()
opticalAlignment_Ch4.set_writable()
opticalAlignment_Ch5.set_writable()
opticalAlignment_Ch6.set_writable()
opticalAlignment_Ch7.set_writable()
opticalAlignment_Ch8.set_writable()
opticalAlignment_Ch9.set_writable()
opticalAlignment_Ch10.set_writable()
opticalAlignment_Ch11.set_writable()
opticalAlignment_Ch12.set_writable()


####
DECODING_LINK_ALIGNED_00_Ch1.set_writable()
DECODING_LINK_ALIGNED_00_Ch2.set_writable()
DECODING_LINK_ALIGNED_00_Ch3.set_writable()
DECODING_LINK_ALIGNED_00_Ch4.set_writable()
DECODING_LINK_ALIGNED_00_Ch5.set_writable()
DECODING_LINK_ALIGNED_00_Ch6.set_writable()

DECODING_LINK_ALIGNED_01_Ch1.set_writable()
DECODING_LINK_ALIGNED_01_Ch2.set_writable()
DECODING_LINK_ALIGNED_01_Ch3.set_writable()
DECODING_LINK_ALIGNED_01_Ch4.set_writable()
DECODING_LINK_ALIGNED_01_Ch5.set_writable()
DECODING_LINK_ALIGNED_01_Ch6.set_writable()

DECODING_LINK_ALIGNED_02_Ch1.set_writable()
DECODING_LINK_ALIGNED_02_Ch2.set_writable()
DECODING_LINK_ALIGNED_02_Ch3.set_writable()
DECODING_LINK_ALIGNED_02_Ch4.set_writable()
DECODING_LINK_ALIGNED_02_Ch5.set_writable()
DECODING_LINK_ALIGNED_02_Ch6.set_writable()

DECODING_LINK_ALIGNED_03_Ch1.set_writable()
DECODING_LINK_ALIGNED_03_Ch2.set_writable()
DECODING_LINK_ALIGNED_03_Ch3.set_writable()
DECODING_LINK_ALIGNED_03_Ch4.set_writable()
DECODING_LINK_ALIGNED_03_Ch5.set_writable()
DECODING_LINK_ALIGNED_03_Ch6.set_writable()

# Start the server
server.start()

print("OPC UA Server is running at {}".format(ipAddress))
try:
    while True:
        # Update values dynamically
        readFelixInfo()

        opticalAlignment_Ch1.set_value(felixInfo["OpticalLinksAlignment"]["Ch1"])
        opticalAlignment_Ch2.set_value(felixInfo["OpticalLinksAlignment"]["Ch2"])
        opticalAlignment_Ch3.set_value(felixInfo["OpticalLinksAlignment"]["Ch3"])
        opticalAlignment_Ch4.set_value(felixInfo["OpticalLinksAlignment"]["Ch4"])
        opticalAlignment_Ch5.set_value(felixInfo["OpticalLinksAlignment"]["Ch5"])
        opticalAlignment_Ch6.set_value(felixInfo["OpticalLinksAlignment"]["Ch6"])
        opticalAlignment_Ch7.set_value(felixInfo["OpticalLinksAlignment"]["Ch7"])
        opticalAlignment_Ch8.set_value(felixInfo["OpticalLinksAlignment"]["Ch8"])
        opticalAlignment_Ch9.set_value(felixInfo["OpticalLinksAlignment"]["Ch9"])
        opticalAlignment_Ch10.set_value(felixInfo["OpticalLinksAlignment"]["Ch10"])
        opticalAlignment_Ch11.set_value(felixInfo["OpticalLinksAlignment"]["Ch11"])
        opticalAlignment_Ch12.set_value(felixInfo["OpticalLinksAlignment"]["Ch12"])


        DECODING_LINK_ALIGNED_00_Ch1.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_00"]["Ch1"])
        DECODING_LINK_ALIGNED_00_Ch2.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_00"]["Ch2"])
        DECODING_LINK_ALIGNED_00_Ch3.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_00"]["Ch3"])
        DECODING_LINK_ALIGNED_00_Ch4.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_00"]["Ch4"])
        DECODING_LINK_ALIGNED_00_Ch5.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_00"]["Ch5"])
        DECODING_LINK_ALIGNED_00_Ch6.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_00"]["Ch6"])

        DECODING_LINK_ALIGNED_01_Ch1.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_01"]["Ch1"])
        DECODING_LINK_ALIGNED_01_Ch2.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_01"]["Ch2"])
        DECODING_LINK_ALIGNED_01_Ch3.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_01"]["Ch3"])
        DECODING_LINK_ALIGNED_01_Ch4.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_01"]["Ch4"])
        DECODING_LINK_ALIGNED_01_Ch5.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_01"]["Ch5"])
        DECODING_LINK_ALIGNED_01_Ch6.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_01"]["Ch6"])

        DECODING_LINK_ALIGNED_02_Ch1.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_02"]["Ch1"])
        DECODING_LINK_ALIGNED_02_Ch2.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_02"]["Ch2"])
        DECODING_LINK_ALIGNED_02_Ch3.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_02"]["Ch3"])
        DECODING_LINK_ALIGNED_02_Ch4.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_02"]["Ch4"])
        DECODING_LINK_ALIGNED_02_Ch5.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_02"]["Ch5"])
        DECODING_LINK_ALIGNED_02_Ch6.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_02"]["Ch6"])

        DECODING_LINK_ALIGNED_03_Ch1.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_03"]["Ch1"])
        DECODING_LINK_ALIGNED_03_Ch2.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_03"]["Ch2"])
        DECODING_LINK_ALIGNED_03_Ch3.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_03"]["Ch3"])
        DECODING_LINK_ALIGNED_03_Ch4.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_03"]["Ch4"])
        DECODING_LINK_ALIGNED_03_Ch5.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_03"]["Ch5"])
        DECODING_LINK_ALIGNED_03_Ch6.set_value(felixInfo["ElinksAlignment"]["DECODING_LINK_ALIGNED_03"]["Ch6"])

        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down server...")
finally:
    server.stop()
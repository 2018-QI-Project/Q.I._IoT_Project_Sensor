from neo_adc import ADC
from bluetooth import *

#initialize the ADC class with pin A0
WE = ADC(0)
AE = ADC(1)

# calibration constants
WE_0 = 356.
AE_0 = 354.
WE_sensitivity = 0.305

# "temperature"
#temp = 25
n = 1

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service(
        server_sock,
        "BluetoothServer",
        service_id = uuid,
        service_classes = [uuid, SERIAL_PORT_CLASS],
        profiles = [SERIAL_PORT_PROFILE]
)

print "Waiting for connection on RFCOMM channel {0}".format(port)

client_sock, client_info = server_sock.accept()
client_addr = client_info[0]
print "Accepted connection from {0}".format(client_addr)

try:
        while True:
                data = client_sock.recv(1024).replace("\r\n","")
                if len(data) == 0: break
                print "Received from [{0}]: {1}".format(client_addr, data)
                if data == "send":
                        #read voltage from ADC for WE and AE
                        WE_mV = WE.get_mvolts()
                        AE_mV = AE.get_mvolts()

                        #calculate ppb using Alphasense formula
                        ppb = ((WE_mV - WE_0) - n * (AE_mV * AE_0)) / WE_sensitivity

                        #send ppb value to client
                        send_string = '"SO2": {0}\r\n'.format(ppb)
                        print "Sent to [{0}]: {1}".format(client_addr,
                                send_string.replace("\r\n",""))
                        client_sock.send(send_string)
except Exception as e:
        print "Error: {0}".format(repr(e))

print "Connection terminated. Disconnected!"
client_sock.close()
server_sock.close()
print "Sockets closed successfully. Bye!"

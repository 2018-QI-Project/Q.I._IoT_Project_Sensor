from neo_adc import ADC
from bluetooth import *
import json
from collections import OrderedDict
from time import sleep
from neo import easyGpio

A0 = ADC(0)

mux = [
        easyGpio(24),
        easyGpio(25),
        easyGpio(26),
        easyGpio(27)
]

for sel in mux:
        sel.pinOUT()

def set_mux_channel(ch):
        bits = "{0:04b}".format(ch)
        for i in range(0, 4):
                bit = int(bits[i])
                sel = mux[i]
                sel.on() if bit else sel.off()

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service(
        server_sock,
        "BluethoothServer",
        service_id = uuid,
        service_classes = [uuid, SERIAL_PORT_CLASS],
        profiles = [SERIAL_PORT_PROFILE]
        )

print "Waiting for connection of RFCOMM channel {0}".format(port)

client_sock, client_info = server_sock.accept()
client_addr = client_info[0]
print "Accepted connection from {0}".format(client_addr)

try:
        while True:
                set_mux_channel(0)
                sleep(0.05)
                NO2_WE = A0.get_mvolts()

                set_mux_channel(1)
                sleep(0.05)
                NO2_AE = A0.get_mvolts()

                set_mux_channel(2)
                sleep(0.05)
                O3_WE = A0.get_mvolts()

                set_mux_channel(3)
                sleep(0.05)
                O3_AE = A0.get_mvolts()

                set_mux_channel(4)
                sleep(0.05)
                CO_WE = A0.get_mvolts()

                set_mux_channel(5)
                sleep(0.05)
                CO_AE = A0.get_mvolts()

                set_mux_channel(6)
                sleep(0.05)
                SO2_WE = A0.get_mvolts()

                set_mux_channel(7)
                sleep(0.05)
                SO2_AE = A0.get_mvolts()

                NO2 = ((NO2_WE - 287) - 1.18 * (NO2_AE - 292)) / 0.258
                O3 = ((O3_WE - 418) - 0.18 * (O3_AE - 404)) / 0.393
                CO = ((CO_WE - 345) - 0.03 * (O3_AE - 315)) / 0.292
                SO2 = ((SO2_WE - 333) - 1.15 * (SO2_AE - 274)) / 0.288

                print {
                        "03_WE": O3_WE,
                        "03_AE": O3_AE,
                        "CO_WE": CO_WE,
                        "CO_AE": CO_AE
                }
                
                clien_sock.send(real+"wn")
                sleep(3)

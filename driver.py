import sqlite3
import asyncore
from threading import Thread
from time import sleep
from btserver import BTServer
from sensor import SensorServer

if __name__ == "__main__":
    # create BT server
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    service_name = "Air Pollution Sensor"
    bt_server = BTServer(uuid, service_name)

    # create BT server thread
    bt_server_thread = Thread(target=asyncore.loop, name="BT Server Thread")
    bt_server_thread.daemon = True
    bt_server_thread.start()

    # create sensor server thread
    sensor_server = SensorServer()
    sensor_server.daemon = True
    sensor_server.start()

    try:
        db_conn = sqlite3.connect("blue.db")
        db_cur = db_conn.cursor()
    except Exception as e:
        # print out error using repr(e)
	print "ERROR (sensor.py): {}".format(repr(e))

    while True:
        for client_handler in bt_server.get_active_client_handlers():
           # command = client_handler.get_command()
            sleep(9)

            sensor_output = sensor_server.get_recent_sensor_output()
 	    formatted_sensor_output = str(sensor_output)
            client_handler.send(formatted_sensor_output + "\r\n")
		
        sleep(1) 

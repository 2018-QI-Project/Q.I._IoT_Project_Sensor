import asyncore
from bluetooth import *
from btclienthandler import BTClientHandler

class BTServer(asyncore.dispatcher):
    "An asynchronous Bluetooth server"

    def __init__(self, uuid, service_name, port = PORT_ANY):
        asyncore.dispatcher.__init__(self)

        if not is_valid_uuid(uuid):
            raise ValueError("The UUID {0} is not valid".format(uuid))

        self.uuid = uuid
        self.service_name = service_name
        self.port = port

        # create the Bluetooth server socket
        self.set_socket(BluetoothSocket(RFCOMM))
        self.bind(("", self.port))
        self.listen(1)

        # initialize a set to track the active client-side handlers
        self.active_client_handlers = set()

        # advertise the Bluetooth server
        advertise_service(
            self.socket,
            self.service_name,
            service_id = self.uuid,
            service_classes = [self.uuid, SERIAL_PORT_CLASS],
            profiles = [SERIAL_PORT_PROFILE]
        )
        
        # update port number
        self.port = self.socket.getsockname()[1]

        print "Waiting for connection on RFCOMM channel {0}".format(self.port)

    def handle_accept(self):
        # get the client-sided Bluetooth socket
        client_pair = self.socket.accept()

        if client_pair is not None:
            client_sock, client_info = client_pair
            client_mac = client_info[0]
            client_handler = BTClientHandler(
                socket = client_sock,
                mac_addr = client_mac,
                server = self
            )
            self.active_client_handlers.add(client_handler)

            num_clients = len(self.active_client_handlers)
            print "Accepted connection from {0}".format(client_mac)
            print "Number of active connections: {0}".format(num_clients)

    def get_active_client_handlers(self):
	return self.active_client_handlers.copy()

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

if __name__ == "__main__":
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    service_name = "AsyncBTServer"

    server = BTServer(uuid, service_name)
    asyncore.loop()

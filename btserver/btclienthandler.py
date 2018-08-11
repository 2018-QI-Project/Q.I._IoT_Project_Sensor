import asyncore
from bterror import BTError

class BTClientHandler(asyncore.dispatcher_with_send):
    "A Bluetooth handler for a client-sided socket"

    def __init__(self, socket, mac_addr, server):
        asyncore.dispatcher_with_send.__init__(self, socket)
        self.mac_addr = mac_addr
        self.server = server
        self.data = ""

    def handle_read(self):
        try:
            data = self.recv(1024)
            if not data: return

            ln_char_index = data.find("\n")

            if ln_char_index < 0:
                # no newline in data, append to current buffer
                self.data += data
            else:
                # newline found, so append, send, and clear the buffer
                self.data += data[:ln_char_index]
                print "Received [{0}]: {1}".format(self.mac_addr, self.data)
                
                self.send(data + "\n")
                self.data = ""
        except Exception as e: 
                BTError.print_error(
                    handler = self,
                    error = BTError.ERR_READ,
                    message = repr(e)
                )
                self.data = ""
                self.handle_close()

    def handle_close(self):
        # flush the buffer
        while self.writable():
            self.handle_write()

        self.server.active_client_handlers.remove(self)
        self.close()

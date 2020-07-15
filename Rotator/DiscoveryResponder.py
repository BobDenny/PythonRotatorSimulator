# =======================
# DISCOVERY API RESPONDER
# =======================
# 15-Jul-2020   rbd     Final V4-only discovery responder. IPV6 would be in another
#                       thread. 
import os
import socket                                           # for discovery responder
from threading import Thread                            # Same here

class DiscoveryResponder(Thread):
    def __init__(self, ADDR, PORT):
        Thread.__init__(self)
        self.device_address = (ADDR, 32227) #listen for any IP on Alpaca disc. port
        self.alpaca_response  = "{\"alpacaport\": " + str(PORT) + "}"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #share address
        if os.name != 'nt':
            # needed on Linux and OSX to share port with net core. Remove on windows
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) 
        try:
            self.sock.bind(self.device_address)
        except:
            print('Discovery responder: failure to bind')
            self.sock.close()
            self.sock = 0
            raise
        # OK start the listener
        self.daemon = True
        self.start()
    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            datascii = str(data, 'ascii')
            print('Disc rcv ' + datascii + ' from ' + str(addr))
            if 'alpacadiscovery1' in datascii:    
                self.sock.sendto(self.alpaca_response.encode(), addr)


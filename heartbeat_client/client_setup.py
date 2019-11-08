#!/usr/bin/env python3

import socket
import time
import sys
import logging


class HeartbeatClient:
    TCP_PORT = 5000
    BUFFER_SIZE = 1024
    HEARTBEAT_INCREMENT = 1

    def __init__(self):
        self.heartbeat_counter = 0

        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

    def start_client(self):
        while 1:
            try:
                self.set_connection(server_list=sys.argv[1:])
            except ConnectionRefusedError:
                pass
            except KeyboardInterrupt:
                break

            time.sleep(self.HEARTBEAT_INCREMENT)
            self.heartbeat_counter += 1

    def set_connection(self, server_list):
        for server in server_list:
            logging.debug("INITIALISING CONNECTION TO " + str(server))
            self.send_data(server=server)

    def send_data(self, server):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server, self.TCP_PORT))
            s.send(int.to_bytes(self.heartbeat_counter, byteorder="little", length=8))
            s.close()
        except ConnectionAbortedError:
            pass


if __name__ == "__main__":
    client = HeartbeatClient()
    client.start_client()

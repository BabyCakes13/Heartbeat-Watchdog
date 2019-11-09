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
        self.heartbeat_counter = {}
        self.server_list = sys.argv[1:]
        for server in self.server_list:
            self.heartbeat_counter[server] = 0
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

    def start_client(self):
        while 1:
            self.set_connection()

            time.sleep(self.HEARTBEAT_INCREMENT)

    def set_connection(self):
        for server in self.server_list:
            logging.debug("INITIALISING CONNECTION TO " + str(server))
            try:
                self.send_data(server=server)
            except ConnectionRefusedError:
                self.heartbeat_counter[server] = 0

    def send_data(self, server):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server, self.TCP_PORT))
            s.send(int.to_bytes(self.heartbeat_counter[server], byteorder="little", length=8))
            s.close()
            self.heartbeat_counter[server] += 1

        except ConnectionAbortedError:
            pass


if __name__ == "__main__":
    client = HeartbeatClient()
    client.start_client()

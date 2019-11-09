#!/usr/bin/env python3

import socket
import time
import sys
import logging


class HeartbeatClient:
    """
    Class which handled the client instance.
    """
    TCP_PORT = 5000
    BUFFER_SIZE = 1024
    HEARTBEAT_INCREMENT = 1

    def __init__(self):
        """
        Constructor of the class. Initialises the object variables, while also taking the server request lists for the
        client to connect to.
        """
        self.heartbeat_counter = {}  # remember the heartbeat counter for each server in the server list separately
        self.server_list = sys.argv[1:]
        for server in self.server_list:
            self.heartbeat_counter[server] = 0

        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

    def start_client(self):
        """
        Function which calls the set up connection one to take care of data handling, while also incrementing the
        heartbeat.
        :return: None
        """
        while 1:
            self.set_connection()
            time.sleep(self.HEARTBEAT_INCREMENT)

    def set_connection(self):
        """
        Function which for each server in the server list, tries to send it the heartbeat.
        Since the client may try to connect to a server without the server being already up, each time the connection
        fails, the heartbeat is returned to 0. Otherwise, the first heartbeat caught by the server would not be 0.
        :return: None
        """
        for server in self.server_list:
            logging.debug("INITIALISING CONNECTION TO " + str(server))
            try:
                self.send_heartbeat(server=server)
            except ConnectionRefusedError:
                self.heartbeat_counter[server] = 0

    def send_heartbeat(self, server):
        """
        Function which connects to the server by the given socket, and sends the heartbeat, updating its value for the
        current server in the server dictionary.
        :param server: The current server which needs connection.
        :return: None
        """
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

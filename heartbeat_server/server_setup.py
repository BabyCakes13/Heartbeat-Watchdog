#!/usr/bin/env python3


import socket
import logging
import time


class HeartbeatServer:
    TCP_IP = ''
    TCP_PORT = 5000
    BUFFER_SIZE = 1024
    TIMEOUT = 0.5
    HEARTBEAT_DISCONNECT_TIME = 3

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.TCP_IP, self.TCP_PORT))
        self.socket.listen(5)
        self.socket.settimeout(self.TIMEOUT)

        self.heartbeats = {}
        self.timestamps = {}

        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

    def start_server(self):
        while 1:
            try:
                while 1:
                    self.set_connection()
            except socket.timeout:
                self.check_heartbeats()

    def set_connection(self):
        connection, addrport = self.socket.accept()
        connection.settimeout(self.TIMEOUT)
        address = addrport[0]

        if address not in self.timestamps:
            self.timestamps[address] = time.time()
            logging.info("FIRST CONNECTION " + str(address) + " ( " + str(self.timestamps[address]) + ")")

        logging.debug("Timestamp addresses: " + str(self.timestamps.keys()))

        while 1:
            data = self.receive_data(connection=connection)
            if not data:
                break
            received_heartbeat = int.from_bytes(data, byteorder="little")

            self.handle_reconnect(received_heartbeat=received_heartbeat, address=address)
            self.heartbeats[address] = received_heartbeat
            logging.info("HEARTBEAT: " + str(address) + " (" + str(self.heartbeats.get(address)) + ")")

        connection.close()

    def receive_data(self, connection):
        data = None
        try:
            data = connection.recv(self.BUFFER_SIZE)
        except socket.timeout:
            logging.critical("TIMEOUT ", self.TIMEOUT, " seconds.")
        return data

    def handle_reconnect(self, received_heartbeat, address):
        try:
            if self.heartbeats[address] > received_heartbeat:
                self.timestamps[address] = time.time()
                logging.info("Reconnected " + str(address) + " at time: " + str(self.timestamps[address]))
        except KeyError:
            logging.debug("No key with address " + str(address))

    def check_heartbeats(self):
        logging.debug("Checking all the client heartbeats.")

        for address, heartbeat_counter in self.heartbeats.items():
            logging.debug("Checking " + str(address) + " with current heartbeat " + str(heartbeat_counter))

            time_difference = time.time() - self.timestamps[address]

            logging.debug("TIME DIFFERENCE: " + str(time_difference) + " HEARTBEATS: " + str(heartbeat_counter))
            logging.debug("HEARTBEAT DIFFERENCE: " + str(heartbeat_counter + self.HEARTBEAT_DISCONNECT_TIME))

            if time_difference > heartbeat_counter + self.HEARTBEAT_DISCONNECT_TIME:
                logging.debug("FOUND")
                logging.critical("DISCONNECTED: " + str(address))


if __name__ == "__main__":
    server = HeartbeatServer()
    server.start_server()

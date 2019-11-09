#!/usr/bin/env python3


import socket
import logging
import time


class HeartbeatServer:
    """
    Class which handled the server instance.
    """
    TCP_IP = ''
    TCP_PORT = 5000
    BUFFER_SIZE = 1024
    TIMEOUT = 0.1
    HEARTBEAT_DISCONNECT_TIME = 3

    def __init__(self):
        """
        Constructor of the class, which sets up the socket to listen to the clients.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.TCP_IP, self.TCP_PORT))
        self.socket.listen(5)
        self.socket.settimeout(self.TIMEOUT)

        self.heartbeats = {}  # heartbeats where key:address, value:heartbeats
        self.timestamps = {}  # timestamps where key:address, value:timestamp

        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

    def start_server(self):
        """
        Function which sets up the connection so it listens continuously for new clients, while also always checking that
        there was no one disconnected.
        :return: None
        """
        while 1:
            try:
                self.set_connection()
            except socket.timeout:
                pass
            self.check_heartbeats()

    def set_connection(self):
        """
        Function which accept clients based on address, verifies if they exist, and keep track of the timestamp
        of the connection, so it can be tracked in case of disconnection between the heartbeat and the timestamp.
        It receives the data, if the address was reconnected, and updates the heartbeat received
        from the address (client).
        :return: None
        """
        connection, addrport = self.socket.accept()
        connection.settimeout(self.TIMEOUT)
        address = addrport[0]

        if address not in self.timestamps:
            self.timestamps[address] = time.time()
            logging.info("First connection of " + str(address) + " ( " + str(self.timestamps[address]) + ").")
            logging.info("Currently connected clients: " + str(self.timestamps.keys()))

        logging.debug("Timestamps: " + str(self.timestamps.keys()))

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
        """
        Function which handles data receiving, checks its validity and handles timeout.
        :param connection: The connection to the server.
        :return: The heartbeat.
        """
        data = None
        try:
            data = connection.recv(self.BUFFER_SIZE)
        except socket.timeout:
            logging.critical("TIMEOUT:receive data from client. (", self.TIMEOUT, " seconds.)")
        return data

    def handle_reconnect(self, received_heartbeat, address):
        """
        Function which checks if the address reconnected to the server after a crash.
        :param received_heartbeat: If the address reconnected, the received heartbeat will begin from 0 again.
        :param address: The address which is checked for reconnect.
        :return: None
        """
        try:
            if self.heartbeats[address] > received_heartbeat:
                self.timestamps[address] = time.time()
                logging.info("Reconnected:" + str(address) + " at time: " + str(self.timestamps[address]))
        except KeyError:
            logging.debug("No key with address:" + str(address))

    def check_heartbeats(self):
        """
        Function which checks for disconnected addresses by checking the time difference between the current time
        and the time it connected + the seconds we consider a client to be disconnected.
        :return: None
        """
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

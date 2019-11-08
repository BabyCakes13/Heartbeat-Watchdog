import socket
import logging
import time


class HeartbeatServer:
    TCP_IP = ''
    TCP_PORT = 5000
    BUFFER_SIZE = 1024
    TIMEOUT = 0.1
    HEARTBEAT_FAILURE_TIME = 3

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
                    self.check_heartbeats()
            except socket.timeout:
                logging.critical("Could not connect.")

    def set_connection(self):
        connection, addrport = self.socket.accept()
        address = addrport[0]

        if address not in self.timestamps:
            self.timestamps[address] = time.time()
            logging.info("FIRST CONNECTION " + str(address) + " ( " + str(self.timestamps[address]) + ")")

        logging.debug("Timestamp addresses: " + str(self.timestamps.keys()))

        data = 0
        while data:
            data = self.receive_data(connection=connection, address=address)
            received_heartbeat = int.from_bytes(data)

            self.handle_reconnect(received_heartbeat=received_heartbeat, address=address)
            self.heartbeats[address] = received_heartbeat
            logging.info("HEARTBEAT: " + str(address) + " (" + str(self.heartbeats.get(address)) + ")")

        # connection.close()

    def receive_data(self, connection, address):
        connection.settimeout(self.TIMEOUT)

        data = None
        try:
            data = connection.recv(self.BUFFER_SIZE)
        except socket.timeout:
            logging.critical("TIMEOUT ", self.TIMEOUT, " seconds.")

        if not data:
            logging.info("No data received.")
            return None

        logging.debug("Address: " + str(address) + "; raw data: " + str(data))
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
            time_difference = time.time() - self.timestamps[address]
            logging.debug("TIME DIFFERENCE: " + str(time_difference) + " HEARTBEATS: " + str(heartbeat_counter))

            if time_difference > heartbeat_counter + self.HEARTBEAT_FAILURE_TIME:
                logging.critical("DISCONNECTED: " + str(address))

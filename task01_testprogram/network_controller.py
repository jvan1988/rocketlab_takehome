import socket
import codecs
import threading


class NetworkController:
    _instance_lock = threading.Lock()
    _instance = None

    @classmethod
    def instance(cls, parent):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = cls(parent)
            return cls._instance

    def __init__(self, parent):
        self.receive_thread = None
        if NetworkController._instance:
            raise RuntimeError("DeviceCommunication is a singleton class, use 'instance()' method to get the instance.")
        self.parent = parent
        self.sock = None
        self.test_running = False
        self.test_start_lock = threading.Lock()
        self.test_started = False
        self.duration = None

    def connect_device(self, ip, port):
        if self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.connect((ip, port))
            except (socket.error, socket.timeout) as e:
                # Handle connection error
                self.parent.show_message_box("Connect Failed", f"Failed to connect to device: {str(e)}")
                return
            print(f"Socket Connected to {ip}:{port}")
            self.test_running = True

            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.start()

            # Discovery message
            command = "ID;"
            self.send_receive_data(command)

    def start_test(self, duration):
        with self.test_start_lock:
            if self.test_started:
                # Test already started, do nothing
                self.parent.show_message_box("Test Started", "Test has already started.")
                return

            self.parent.plotter.x_data = []
            self.parent.plotter.y_data = []
            self.duration = duration
            command = f"TEST;CMD=START;DURATION={duration};RATE=1000;"
            self.send_receive_data(command)

            self.test_started = True

            self.parent.start_button.setEnabled(False)
            self.parent.stop_button.setEnabled(True)

    def stop_test(self):
        with self.test_start_lock:
            if self.test_running:
                command = "TEST;CMD=STOP;"
                self.send_receive_data(command)

    def receive_data(self):
        while self.test_running:
            try:
                data = self.sock.recv(1024).decode("ISO-8859-1")
                self.process_data(data)
            except socket.timeout:
                continue
            except ConnectionRefusedError:
                self.parent.show_message_box("Connection refused!", "Unable to receive data.")
                break

        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def process_data(self, data):
        print(f"Received: {data}")

        data_info = data.split(";")
        data_values = {}

        for entry in data_info:
            if "=" in entry:
                key, value = entry.split("=")
                data_values[key] = value

        if data_info[0] == "STATUS":
            if all(key in data_values for key in ["TIME", "MV", "MA"]):
                time = 0
                mv = 0
                ma = 0

                try:
                    time = int(data_values["TIME"]) / 1000
                except ValueError:
                    self.parent.show_message_box("STATUS ERROR!", "Time is invalid")

                try:
                    mv = int(data_values["MV"])
                except ValueError:
                    self.parent.show_message_box("STATUS ERROR!", "MV is invalid")

                try:
                    ma = int(data_values["MA"])
                except ValueError:
                    self.parent.show_message_box("STATUS ERROR!", "MA is invalid")

                if time and mv and ma:
                    self.parent.plotter.update_data(time, mv, ma)

            elif "STATE" in data_values:
                if data_values["STATE"] == "IDLE":
                    self.parent.show_message_box("STATE IDLE", "Test has ended")
                    self.restart_app()
                else:
                    self.parent.show_message_box("STATE UNKNOWN!", data_values["STATE"])

            else:
                self.parent.show_message_box("STATUS ERROR!", "Unhandled Status")

        elif data_info[0] == "ID":
            if all(key in data_values for key in ["MODEL", "SERIAL"]):
                model = data_values["MODEL"]
                serial = data_values["SERIAL"]

                self.parent.show_message_box("Connection Established!",
                                             f"MODEL:{model} SERIAL:{serial}")

                self.parent.start_button.setEnabled(True)
                self.parent.connect_button.setEnabled(False)
                self.parent.save_button.setEnabled(False)
                self.parent.plotter.clear_data()

            else:
                self.parent.show_message_box("ID ERROR!", "Unhandled ID")

        elif data_info[0] == "TEST":
            if "RESULT" in data_values:
                if data_values["RESULT"] == "STARTED":
                    print("Test Started")
                elif data_values["RESULT"] == "STOPPED":
                    self.parent.show_message_box("TEST STOPPED", "The test has been stopped.")
                elif data_values["RESULT"] == "error":
                    if "MSG" in data_values:
                        reason = data_values["MSG"]
                        self.parent.show_message_box("TEST ERROR!", f"Reason: {reason}")
                    else:
                        self.parent.show_message_box("RESULT ERROR!", "Error with no reason")
                else:
                    self.parent.show_message_box("TEST ERROR!", "Unknown Result")

        else:
            print(f"Received Unhandled Message: {data}")

    def restart_app(self):
        self.test_running = False
        self.test_started = False
        self.parent.stop_button.setEnabled(False)
        self.parent.save_button.setEnabled(True)
        self.parent.connect_button.setEnabled(True)

    def send_command(self, command):
        if self.sock:
            self.sock.send(codecs.encode(command, "ISO-8859-1"))
        else:
            self.parent.show_message_box("Send Command Failed",
                                         "Socket is not initialized or connection is not established.")

    def send_receive_data(self, command):
        send_thread = threading.Thread(target=self.send_command, args=(command,))
        send_thread.start()

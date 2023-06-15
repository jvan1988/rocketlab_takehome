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
        self.duration = 0

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

        if data.startswith("STATUS;"):
            status_data = data.split(";")[1:]
            # Extract relevant information from status_data

            if status_data[0].startswith("TIME"):
                time = int(status_data[0].split('=')[1]) / 1000
                mv = int(status_data[1].split('=')[1])
                ma = int(status_data[2].split('=')[1])

                self.parent.plotter.update_data(time, mv, ma)
            elif status_data[0].startswith("STATE"):
                if status_data[0].split('=')[1] == "IDLE":
                    self.parent.show_message_box("Test Ended", "STATE IS IDLE")
                    self.restart_app()

        elif data.startswith("ID;"):
            self.parent.start_button.setEnabled(True)
            self.parent.connect_button.setEnabled(False)
            self.parent.save_button.setEnabled(False)
            self.parent.plotter.clear_data()

            model_data = data.split(";")[1:]
            model = model_data[0].split('=')[1]
            serial = model_data[1].split('=')[1]
            self.parent.show_message_box("Connection Established!",
                                         f"MODEL:{model} SERIAL:{serial}")

        elif data.startswith("TEST;RESULT"):
            result_data = data.split(";")[1:]
            result = result_data[0].split('=')[1]
            # Start a timer to track the test duration
            if result == "STARTED":
                # threading.Timer(int(self.duration), self.stop_test).start()
                print("Test Started")
            elif result == "STOPPED":
                self.parent.show_message_box("Test Stopped", "The test has been stopped.")
                # self.test_running = False
                # self.parent.stop_button.setEnabled(False)
                # self.parent.save_button.setEnabled(True)
            else:
                reason = result_data[1].split('=')[1]
                self.parent.show_message_box("Connection ERROR!",
                                             f"Error: {result} reason: {reason}")

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

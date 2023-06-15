from PyQt5.QtWidgets import QPushButton


def is_valid_ip(ip):
    # Validate IP address
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            value = int(part)
            if value < 0 or value > 255:
                return False
        except ValueError:
            return False
    return True


def is_valid_port(port):
    # Validate port number
    try:
        value = int(port)
        if value < 0 or value > 65535:
            return False
    except ValueError:
        return False
    return True


def is_valid_duration(duration):
    # Validate test duration
    try:
        value = int(duration)
        if value <= 0:
            return False
    except ValueError:
        return False
    return True


class ConnectButton(QPushButton):
    def __init__(self, parent):
        super().__init__("Connect")
        self.parent = parent
        self.clicked.connect(self.connect_device)

    def connect_device(self):
        ip = self.parent.ip_edit.text()
        if not self.parent.port_edit.text():
            self.parent.show_message_box("Connect Failed", "Port is empty")
            return
        try:
            port = int(self.parent.port_edit.text())
        except ValueError:
            self.parent.show_message_box("Connect Failed", "Port is not an integer")
            return

        if is_valid_ip(ip) and is_valid_port(port):
            self.parent.device_communication.connect_device(ip, port)
        else:
            self.parent.show_message_box("Connect Failed", "Invalid IP or Port.")


class StartButton(QPushButton):
    def __init__(self, parent):
        super().__init__("Start")
        self.parent = parent
        self.clicked.connect(self.start_test)
        self.setEnabled(False)

    def start_test(self):
        duration = self.parent.duration_edit.text()

        if is_valid_duration(duration):
            self.parent.device_communication.start_test(duration)
        else:
            self.parent.show_message_box("Start Failed", "Invalid Duration.")


class StopButton(QPushButton):
    def __init__(self, parent):
        super().__init__("Stop")
        self.parent = parent
        self.clicked.connect(self.stop_test)
        self.setEnabled(False)

    def stop_test(self):
        self.parent.device_communication.stop_test()
        self.parent.save_button.setEnabled(True)



class SaveButton(QPushButton):
    def __init__(self, parent):
        super().__init__("Save")
        self.parent = parent
        self.clicked.connect(self.save_results)
        self.setEnabled(False)

    def save_results(self):
        self.parent.save_results()

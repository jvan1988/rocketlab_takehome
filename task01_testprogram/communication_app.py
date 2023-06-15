from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QMessageBox, QLabel
from plotter import Plotter
from network_controller import NetworkController
from buttons import ConnectButton, StartButton, StopButton, SaveButton
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pdf_exporter import PDFExporter


class CommunicationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.start_button = None
        self.connect_button = None
        self.stop_button = None
        self.save_button = None
        self.ip_edit = None
        self.port_edit = None
        self.duration_edit = None

        self.setWindowTitle("Test Program")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self.central_widget)

        self.layout.addWidget(self.canvas)
        self.create_input_fields()
        self.create_buttons()

        self.device_communication = NetworkController.instance(self)
        self.plotter = Plotter(self.figure, self.canvas)
        self.pdf_exporter = PDFExporter()

        self.show()

    def create_buttons(self):
        self.connect_button = ConnectButton(self)
        self.start_button = StartButton(self)
        self.stop_button = StopButton(self)
        self.save_button = SaveButton(self)
        self.layout.addWidget(self.connect_button)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.save_button)

    def create_input_fields(self):
        ip_label = QLabel("IP Address:")
        self.ip_edit = QLineEdit()
        self.layout.addWidget(ip_label)
        self.layout.addWidget(self.ip_edit)

        port_label = QLabel("Port Number:")
        self.port_edit = QLineEdit()
        self.layout.addWidget(port_label)
        self.layout.addWidget(self.port_edit)

        duration_label = QLabel("Test Duration (seconds):")
        self.duration_edit = QLineEdit()
        self.layout.addWidget(duration_label)
        self.layout.addWidget(self.duration_edit)

    @staticmethod
    def show_message_box(title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def save_results(self):
        self.pdf_exporter.export_to_pdf(self.figure, "test_results.pdf")

    def closeEvent(self, event):
        self.device_communication.test_running = False
        event.accept()

# Test Program

This is a Python 3 and PyQt5-based graphical user interface (GUI) program for interacting with a test device over a network connection. The program allows you to connect to a test device at a specified IP address and port, define a test duration, start test, force a test to stop early, see a live plot of measured values during the test, and write test results to a PDF report.

## Requirements

    Python 3.x
    PyQt5
    Matplotlib

## Installation

1. Clone or download this repository to your local machine.
2. Install the required dependencies using pip:
```
pip install -r requirements.txt
```

## Usage

1. Run the program using the following command:

```
python main.py
```

2. The Test Program GUI window will appear.
3. Enter the IP address and port of the test device.
4. Specify the test duration in seconds.
5. Click the "Connect" button to connect to the device. Confirmation popup will confirmed device discovery.
6. Click the "Start" button to start the test.
7. During the test, you will see a live plot of the measured values of MV and MA.
8. To stop the test prematurely, click the "Stop" button.
9. After the test has finished or been stopped successfully, you will be notified via popup, you may save the live plot to PDF with the button "Save". The file can be found under "test_results.pdf"

## Troubleshooting

Qt platform plugin "xcb" may be missing or not properly configured.
To resolve this problem, try the following solutions to install the required dependencies:

### On Ubuntu or Debian-based systems, run the following command:
```
sudo apt-get install libxcb-xinerama0
```
### On Fedora or Red Hat-based systems, run the following command:
```
sudo dnf install libxcb-xinerama
```
### On Arch Linux-based systems, run the following command:
```
sudo pacman -Sy xcb-util-xrm
```
## Considerations

Matplotlib is a 3rd-party library that was used. Matplotlib is a commonly used plotting library in Python. It is an open-source library that is easy to use, highly customizable and integrates well with Python. It also includes functionality such as exporting plots to PDF format which was also required for the Test Program.

## Acknowledgements
This program was developed using Python 3 and the following libraries: PyQt5, Matplotlib.

The device protocol and behavior information provided in the appendix were taken into account while designing the program.

## Appendix: Device protocol and behaviour
The device listens for UDP packets. Unknown messages are ignored by the device.
    
The device sends responses to the IP address and port number from which the request was received.
    
All messages are strings consisting of keywords and values separated by semicolons. All numerical values are integers. The strings are encoded using ISO-8859-1 (Latin 1).

Packet descriptions are as follows (uppercase indicates literal values, lowercase indicates values to be filled in as appropriate):

### A. Discovery
A discovery message is sent to the address:port of a specific device:

    "ID;”
        
Any device that receives a discovery message will respond with its model ID and serial number:

    "ID;MODEL=m;SERIAL=n;“

### B. Testing
Start a test of the given duration, with status reporting at the specified rate:

    "TEST;CMD=START;DURATION=s;RATE=ms;"

DURATION is test duration, in seconds
        
RATE is how often the device should report status during the test, in milliseconds
        
The test will stop after the given duration, or when device receives the stop command:

    "TEST;CMD=STOP;"
        
The start and stop commands will result in one of the following responses:

    "TEST;RESULT=STARTED;" - the test was started successfully
        
    "TEST;RESULT=STOPPED;" - the test was stopped successfully
        
    "TEST;RESULT=error;MSG=reason;" - a test was already running, or was already stopped

### C. Status
While the test is running, the device will send status messages at the specified rate:

    "STATUS;TIME=ms;MV=mv;MA=ma;"
        
TIME is milliseconds since test start

MV, MA are millivolts and milliamps, respectively.
        
After the test has finished (or if the test was stopped), the device will send one final status message:

    "STATUS;STATE=IDLE;"

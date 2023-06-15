# Simulator

The Simulator is a program that simulates a device and responds to commands sent over a network connection. It provides functionalities such as device discovery, starting and stopping tests, and sending status updates. Please refer to the Appendix for Device protocol and behavior 

## Prerequisites

    C++ compiler with support for C++11 or later.
    GNU Make.

## Compilation
    
Run 
    
    make
    
After successful compilation, you will find the simulator executable in the project directory.

## Usage
Open a terminal and navigate to the directory where the simulator executable is located.

Run the following command to start the simulator:

        ./simulator [port]

Replace **[port]** with the desired port number (e.g., 12345). If no port is specified, the default port **8888** will be used.

The Simulator will start and display a message indicating that it is listening for commands.

Send commands to the Simulator from another application or script over the network. The Simulator expects commands in a specific format. Here are some example commands:

Discovery command: Send a command with the format _ID;_ to discover the device.

Start test command: Send a command with the format _CMD=START;DURATION=10;RATE=100;_ to start a test. Adjust the DURATION and RATE values as needed.

Stop test command: Send a command with the format _CMD=STOP;_ to stop a running test.

The Simulator will respond to each command with the appropriate status or error message.

Monitor the output of the Simulator in the terminal to see the received commands and their responses.

To stop the Simulator, press **Ctrl+C** in the terminal.

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

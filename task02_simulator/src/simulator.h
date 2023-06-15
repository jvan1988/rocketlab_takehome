#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <string>
#include <unordered_map>
#include <mutex>
#include <netinet/in.h>

const int BUFFER_SIZE = 1024;
const int MAX_COMMAND_LENGTH = 256;
const int DEFAULT_PORT = 8888;

using namespace std;

class Simulator {
private:
    int socketfd;
    int port;
    unordered_map<string, bool> started;
    unordered_map<string, mutex> startedMutex;

public:
    // Constructor
    Simulator(int port);

    // Destructor
    ~Simulator();

    // Function to send a UDP response
    void sendResponse(const string& response, const sockaddr_in& clientAddr);

    // Function to send IDLE message
    void sendIdle(const sockaddr_in& clientAddr);

     // Function to parse a command and extract key-value pairs   
    void parseCommand(const string& command, unordered_map<string, string>& params);

    // Function to handle the discovery command
    void handleDiscovery(const sockaddr_in& clientAddr);

    // Function to handle the start test command
    void handleStartTest(const sockaddr_in& clientAddr, const unordered_map<string, string>& params);

    // Helper function for test handling
    void testHelper(const sockaddr_in& clientAddr, const unordered_map<string, string>& params, int time, int duration, int rate);

    // Function to handle the stop test command
    void handleStopTest(const sockaddr_in& clientAddr);

    // Function to handle the received command
    void handleCommand(const string& command, const sockaddr_in& clientAddr);

    // Function to start listening for commands
    void start();
};

#endif  // SIMULATOR_H
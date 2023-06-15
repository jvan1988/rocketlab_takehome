#include "simulator.h"
#include <iostream>
#include <sstream> 
#include <cstring>
#include <chrono>
#include <thread>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <random>

Simulator::Simulator(int port) : socketfd(-1) 
{
    this->port = port;

    // Create socket
    socketfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (socketfd < 0) 
    {
        cerr << "Error creating socket" << endl;
        return;
    }

    // Bind socket to the specified port
    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(port);
    if (bind(socketfd, reinterpret_cast<const sockaddr*>(&serverAddr), sizeof(serverAddr)) < 0) 
    {
        cerr << "Error binding socket to port " << port << endl;
        return;
    }

    started.clear();
}

Simulator::~Simulator() 
{
    // Close socket
    if (socketfd >= 0) 
    {
        close(socketfd);
    }
}

void Simulator::sendResponse(const string& response, const sockaddr_in& clientAddr) 
{
    sendto(socketfd, response.c_str(), response.length(), 0,
           reinterpret_cast<const sockaddr*>(&clientAddr), sizeof(clientAddr));
}

void Simulator::sendIdle(const sockaddr_in& clientAddr)
{
    string response = "STATUS;STATE=IDLE;";
    sendResponse(response, clientAddr);
}

void Simulator::parseCommand(const string& command, unordered_map<string, string>& params) 
{
    istringstream iss(command);
    string token;
    while (getline(iss, token, ';')) 
    {
        string key = token;
        string value = "";
        
        size_t pos = token.find('=');
        if (pos != string::npos) 
        {
            key = token.substr(0, pos);
            value = token.substr(pos + 1);
        }

        params[key] = value;
    }
}

void Simulator::handleDiscovery(const sockaddr_in& clientAddr) 
{
    // Set bool started to false during discovery stage
    string ipAddress = inet_ntoa(clientAddr.sin_addr);

    lock_guard<mutex> lock(startedMutex[ipAddress]);
    started[ipAddress] = false;

    string response = "ID;MODEL=ROCKET;SERIAL=888;";
    sendResponse(response, clientAddr);
}

void Simulator::handleStartTest(const sockaddr_in& clientAddr, const unordered_map<string, string>& params) 
{
    string ipAddress = inet_ntoa(clientAddr.sin_addr);

    {
        lock_guard<mutex> lock(startedMutex[ipAddress]);
        if (params.count("CMD") && params.at("CMD") == "START" && started[ipAddress]) 
        {
            string response = "TEST;RESULT=error;MSG=Test already running;";
            sendResponse(response, clientAddr);
            return;
        }
    }

    string response = "TEST;RESULT=STARTED;";
    sendResponse(response, clientAddr);

    {
        lock_guard<mutex> lock(startedMutex[ipAddress]);
        started[ipAddress] = true;
    }

    int duration = 0;
    if (params.count("DURATION")) 
    {
        duration = stoi(params.at("DURATION")) * 1000;
    }

    int rate = 0;
    if (params.count("RATE")) 
    {
        rate = stoi(params.at("RATE"));
    }

    testHelper(clientAddr, params, 0, duration, rate);
}

void Simulator::testHelper(const sockaddr_in& clientAddr, const unordered_map<string, string>& params, int time, int duration, int rate) 
{
    string ipAddress = inet_ntoa(clientAddr.sin_addr);

    if (time > duration) 
    {
        lock_guard<mutex> lock(startedMutex[ipAddress]);
        started[ipAddress] = false;
        sendIdle(clientAddr);
        return;
    }
    else
    {
        lock_guard<mutex> lock(startedMutex[ipAddress]);
        if (!started[ipAddress]) 
        {
            sendIdle(clientAddr);
            return;
        }

        int millivolt = rand() % 101;
        int milliamp = rand() % 51;
        string response = "STATUS;TIME=" + to_string(time) + ";MV=" + to_string(millivolt) + ";MA=" + to_string(milliamp) + ";";
        sendResponse(response, clientAddr);
    }

    this_thread::sleep_for(chrono::milliseconds(rate));
    testHelper(clientAddr, params, time + rate, duration, rate);
}

void Simulator::handleStopTest(const sockaddr_in& clientAddr) 
{
    string ipAddress = inet_ntoa(clientAddr.sin_addr);

    lock_guard<mutex> lock(startedMutex[ipAddress]);
    started[ipAddress] = false;
    string response = "TEST;RESULT=STOPPED;";
    sendResponse(response, clientAddr);
}

void Simulator::handleCommand(const string& command, const sockaddr_in& clientAddr) 
{
    unordered_map<string, string> params;
    parseCommand(command, params);

    if (params.count("ID")) 
    {
        handleDiscovery(clientAddr);
    } 
    else if (params.count("CMD") && params.at("CMD") == "START") 
    {
        thread startTestThread(&Simulator::handleStartTest, this, clientAddr, params);
        startTestThread.detach();
    } 
    else if (params.count("CMD") && params.at("CMD") == "STOP") 
    {
        handleStopTest(clientAddr);
    }
}

void Simulator::start() 
{
    cout << "Device simulation started. Listening on port: " << port << endl;

    while (true) 
    {
        sockaddr_in clientAddr{};
        socklen_t clientAddrLen = sizeof(clientAddr);
        char buffer[BUFFER_SIZE];

        ssize_t numBytes = recvfrom(socketfd, buffer, sizeof(buffer) - 1, 0,
                                    reinterpret_cast<sockaddr*>(&clientAddr), &clientAddrLen);

        if (numBytes > 0) 
        {
            buffer[numBytes] = '\0';
            string command(buffer);
            cout << "Received command: " << command << endl;

            handleCommand(command, clientAddr);
        }
    }
}

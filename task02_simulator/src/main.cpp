#include "simulator.h"

int main(int argc, char* argv[]) {
    int port = DEFAULT_PORT;
    if (argc > 1) {
        port = std::stoi(argv[1]);
    }

    Simulator simulator(port);
    simulator.start();

    return 0;
}

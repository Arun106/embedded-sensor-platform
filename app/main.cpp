#include "thermal_control.hpp"
#include <iostream>
#ifndef APP_VERSION
#define APP_VERSION "unknown"
#endif
int main(int argc, char* argv[]) {
    if (argc == 2 && std::string(argv[1]) == "--version") {
        std::cout << APP_VERSION << '\n'; return 0;
    }
    if ((argc != 3 && argc != 4) || std::string(argv[1]) != "read") {
        std::cerr << "Usage: sensor-gateway read TEMPERATURE [THRESHOLD] | --version\n";
        return 2;
    }
    try {
        const double value = thermal_control::parse(argv[2]);
        const double threshold = argc == 4 ? thermal_control::parse(argv[3]) : 80.0;
        const auto state = thermal_control::classify(value, threshold);
        std::cout << "{\"module\":\"temperature_input\",\"state\":\"" << state
                  << "\",\"value\":" << value << ",\"threshold\":" << threshold << "}\n";
        return state == "INVALID" ? 2 : 0;
    } catch (const std::exception&) {
        std::cerr << "Invalid sensor input or threshold\n"; return 2;
    }
}

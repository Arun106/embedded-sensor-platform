#include "thermal_control.hpp"
#include <iostream>
int main() {
    int failed = 0;
    const auto check = [&](bool ok) { if (!ok) ++failed; };
    check(thermal_control::classify(-40) == "NORMAL");
    check(thermal_control::classify(79.99) == "NORMAL");
    check(thermal_control::classify(80) == "OVERHEAT");
    check(thermal_control::classify(125) == "OVERHEAT");
    check(thermal_control::classify(125.01) == "INVALID");
    check(!thermal_control::valid_threshold(126));
    std::cout << "Failed boundary assertions: " << failed << '\n';
    return failed == 0 ? 0 : 1;
}

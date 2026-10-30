#include "sensor.hpp"
#include <iostream>
int main() {
    int failed = 0;
    const auto check = [&](bool ok) { if (!ok) ++failed; };
    check(sensor::classify(-40) == "NORMAL");
    check(sensor::classify(79.99) == "NORMAL");
    check(sensor::classify(80) == "OVERHEAT");
    check(sensor::classify(125) == "OVERHEAT");
    check(sensor::classify(125.01) == "INVALID");
    check(!sensor::valid_threshold(126));
    std::cout << "Failed boundary assertions: " << failed << '\n';
    return failed == 0 ? 0 : 1;
}

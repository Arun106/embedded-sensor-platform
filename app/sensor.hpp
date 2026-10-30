#pragma once
#include <cmath>
#include <stdexcept>
#include <string>
#include <string_view>
namespace sensor {
inline double parse(const std::string& input) {
    std::size_t consumed = 0;
    const double value = std::stod(input, &consumed);
    if (consumed != input.size() || !std::isfinite(value))
        throw std::invalid_argument("invalid numeric input");
    return value;
}
inline bool valid_threshold(double threshold) {
    return std::isfinite(threshold) && threshold >= -40.0 && threshold <= 125.0;
}
inline std::string_view classify(double value, double threshold = 80.0) {
    if (!valid_threshold(threshold)) throw std::invalid_argument("invalid threshold");
    if (!std::isfinite(value) || value < -40.0 || value > 125.0) return "INVALID";
    return value >= threshold ? "OVERHEAT" : "NORMAL";
}
}

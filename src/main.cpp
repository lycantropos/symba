#include <pybind11/pybind11.h>

namespace py = pybind11;

#define MODULE_NAME _symba
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#ifndef VERSION_INFO
#define VERSION_INFO "dev"
#endif

using Int = unsigned long long;

static int log2floor(Int value) {
  int result = 0;
  while (value >>= 1) ++result;
  return result;
}

static uint64_t _approximate_integer_sqrt(uint64_t value) {
  uint32_t result = 1 + (value >> 62);
  result = (result << 1) + (value >> 59) / result;
  result = (result << 3) + (value >> 53) / result;
  result = (result << 7) + (value >> 41) / result;
  return (result << 15) + (value >> 17) / result;
}

static Int sqrt_floor(Int value) {
  int result_bits_width = (log2floor(value)) / 2;
  Int result =
      _approximate_integer_sqrt(value << (62 - 2 * result_bits_width)) >>
      (31 - result_bits_width);
  return result - ((result * result - 1) >= value);
}

static Int to_square_free(Int value) {
  while (!(value % 4)) value /= 4;
  Int value_sqrt = sqrt_floor(value);
  for (Int factor_candidate = 3; factor_candidate < value_sqrt;
       factor_candidate += 2) {
    Int factor_candidate_squared = factor_candidate * factor_candidate;
    while (!(value % factor_candidate_squared))
      value /= factor_candidate_squared;
  }
  return value;
}

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(`symba` package utilities.)pbdoc";

  m.def("sqrt_floor", [](const py::object& value) {
    return py::reinterpret_steal<py::object>(PyLong_FromUnsignedLongLong(
        sqrt_floor(PyLong_AsUnsignedLongLong(value.ptr()))));
  });

  m.def("to_square_free", [](const py::object& value) {
    return py::reinterpret_steal<py::object>(PyLong_FromUnsignedLongLong(
        to_square_free(PyLong_AsUnsignedLongLong(value.ptr()))));
  });

  m.attr("__version__") = C_STR(VERSION_INFO);
}

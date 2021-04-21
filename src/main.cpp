#include <pybind11/pybind11.h>

namespace py = pybind11;

#define MODULE_NAME _symba
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#ifndef VERSION_INFO
#define VERSION_INFO "dev"
#endif

using Int = long long;

static int log2floor(Int value) {
  int result = 0;
  while (value >>= 1) ++result;
  return result;
}

static Int sqrt_floor(Int value) {
  Int candidate = 1 << ((log2floor(value) + 2) >> 1);
  while (true) {
    Int next_candidate = (candidate + value / candidate) >> 1;
    if (next_candidate >= candidate) return candidate;
    candidate = next_candidate;
  }
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

  m.def("sqrt_floor", [](py::object value) {
    return py::reinterpret_steal<py::object>(PyLong_FromLongLong(
        sqrt_floor(PyLong_AsLongLong(value.ptr()))));
  });

  m.def("to_square_free", [](py::object value) {
    return py::reinterpret_steal<py::object>(PyLong_FromLongLong(
        to_square_free(PyLong_AsLongLong(value.ptr()))));
  });

  m.attr("__version__") = C_STR(VERSION_INFO);
}

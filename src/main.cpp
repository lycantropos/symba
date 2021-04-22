#include <pybind11/pybind11.h>

namespace py = pybind11;

#define MODULE_NAME _symba
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#ifndef VERSION_INFO
#define VERSION_INFO "dev"
#endif

using Int = unsigned long long;

static Int to_square_free(Int value) {
  while (!(value % 4)) value /= 4;
  for (Int factor_candidate = 3, factor_candidate_squared = 9;
       factor_candidate_squared < value;
       factor_candidate_squared += 2 * factor_candidate + 1,
           factor_candidate += 2) {
    while (!(value % factor_candidate_squared))
      value /= factor_candidate_squared;
  }
  return value;
}

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(`symba` package utilities.)pbdoc";

  m.def("to_square_free", [](const py::object& value) {
    return py::reinterpret_steal<py::object>(PyLong_FromUnsignedLongLong(
        to_square_free(PyLong_AsUnsignedLongLong(value.ptr()))));
  });

  m.attr("__version__") = C_STR(VERSION_INFO);
}

#define PY_SSIZE_T_CLEAN
#include <Python.h>

static long to_square_free_long(long value) {
  while (!(value % 4)) value /= 4;
  for (long factor_candidate = 1, factor_candidate_squared = 9;
       factor_candidate_squared < value; factor_candidate += 2,
            factor_candidate_squared += 4 * factor_candidate + 4) {
    while (!(value % factor_candidate_squared))
      value /= factor_candidate_squared;
  }
  return value;
}

static long long to_square_free_long_long(long long value) {
  while (!(value % 4)) value /= 4;
  for (long long factor_candidate = 1, factor_candidate_squared = 9;
       factor_candidate_squared < value; factor_candidate += 2,
                 factor_candidate_squared += 4 * factor_candidate + 4) {
    while (!(value % factor_candidate_squared))
      value /= factor_candidate_squared;
  }
  return value;
}

static PyObject* to_square_free(PyObject* self, PyObject* integer) {
  int overflow_flag;
  long value = PyLong_AsLongAndOverflow(integer, &overflow_flag);
  if (value == -1) {
    if (PyErr_Occurred())
      return NULL;
    else if (overflow_flag) {
      long long value = PyLong_AsLongLong(integer);
      if (value == -1 && PyErr_Occurred()) return NULL;
      return PyLong_FromLongLong(to_square_free_long_long(value));
    }
  }
  return PyLong_FromLong(to_square_free_long(value));
}

static PyMethodDef _symba_methods[] = {
    {"to_square_free", (PyCFunction)to_square_free, METH_O, NULL},
    {NULL, NULL} /* sentinel */
};

static PyModuleDef _symba_module = {
    PyModuleDef_HEAD_INIT,
    .m_doc = PyDoc_STR("`symba` package utilities."),
    .m_methods = _symba_methods,
    .m_name = "_symba",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit__symba(void) { return PyModule_Create(&_symba_module); }

#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* to_square_free_PyLong(PyObject* value) {
  PyObject* four = PyLong_FromLong(4);
  PyObject *remainder, *tmp, *other_tmp;
  Py_INCREF(value);
  while (1) {
    tmp = PyNumber_Divmod(value, four);
    if (!tmp) {
      Py_DECREF(four);
      return NULL;
    }
    remainder = PyTuple_GET_ITEM(tmp, 1);
    if (PyObject_IsTrue(remainder)) {
      Py_DECREF(tmp);
      break;
    }
    other_tmp = value;
    value = PyTuple_GET_ITEM(tmp, 0);
    Py_INCREF(value);
    Py_DECREF(tmp);
    Py_DECREF(other_tmp);
  }
  PyObject *factor_candidate_squared, *factor_candidate;
  PyObject* two = PyLong_FromLong(2);
  for (factor_candidate = PyLong_FromLong(1),
      factor_candidate_squared = PyLong_FromLong(9);
       PyObject_RichCompareBool(factor_candidate_squared, value, Py_LT);) {
    tmp = factor_candidate;
    factor_candidate = PyNumber_InPlaceAdd(factor_candidate, two);
    Py_DECREF(tmp);
    if (!factor_candidate) {
      value = NULL;
      Py_DECREF(factor_candidate_squared);
      goto end;
    }
    tmp = PyNumber_Multiply(four, factor_candidate);
    if (!tmp) {
      value = NULL;
      Py_DECREF(factor_candidate_squared);
      Py_DECREF(factor_candidate);
      goto end;
    }
    other_tmp = PyNumber_Add(tmp, four);
    Py_DECREF(tmp);
    if (!other_tmp) {
      value = NULL;
      Py_DECREF(factor_candidate_squared);
      Py_DECREF(factor_candidate);
      goto end;
    }
    tmp = factor_candidate_squared;
    factor_candidate_squared =
        PyNumber_InPlaceAdd(factor_candidate_squared, other_tmp);
    Py_DECREF(tmp);
    Py_DECREF(other_tmp);
    if (!factor_candidate_squared) {
      value = NULL;
      Py_DECREF(factor_candidate);
      goto end;
    }
    while (1) {
      tmp = PyNumber_Divmod(value, factor_candidate_squared);
      if (!tmp) {
        value = NULL;
        break;
      }
      remainder = PyTuple_GET_ITEM(tmp, 1);
      if (PyObject_IsTrue(remainder)) {
        Py_DECREF(tmp);
        break;
      }
      other_tmp = value;
      value = PyTuple_GET_ITEM(tmp, 0);
      Py_INCREF(value);
      Py_DECREF(tmp);
      Py_DECREF(other_tmp);
    }
  }
  Py_DECREF(factor_candidate_squared);
  Py_DECREF(factor_candidate);
end:
  Py_DECREF(two);
  Py_DECREF(four);
  return value;
}

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
      long long value = PyLong_AsLongLongAndOverflow(integer, &overflow_flag);
      if (overflow_flag) return to_square_free_PyLong(integer);
      return PyLong_FromLongLong(to_square_free_long_long(value));
    }
  }
  return PyLong_FromLong(to_square_free_long(value));
}

static PyMethodDef _symba_methods[] = {
    {"to_square_free", to_square_free, METH_O, NULL},
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

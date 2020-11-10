#include "ffi/ffi.h"

#include "ffi/prep_cif.c"
#include "ffi/ffi.c"


//#include <dlfcn.h>

extern void stdio_append(int fdno, const char *data);

extern int prompt_request ;

EM_JS(void, js_jseval, (char* str), {
  eval(UTF8ToString(str)) ;
  return;
});

EM_JS(int, js_getc, (), {
    if (!window.stdin.length)
        return 0;
    const retval = window.stdin.charCodeAt(0);
    window.stdin = window.stdin.substr(1);
    return retval;
});

EM_JS(void, js_demux_fd, (int fdno, char * str), {
    vm.stdio_process(fdno, UTF8ToString(str));
});

//vm.aio.demux_fd(UTF8ToString(str));



static PyObject *
embed_log(PyObject * self, PyObject * args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    int rx = EM_ASM_INT({ return Module.printErr(UTF8ToString($0));
                        }
                        , logstr);
    Py_RETURN_NONE;
}


static PyObject *
embed_stdio_append(PyObject * self, PyObject * args) {
    int fdnum = -1;
    char *str = NULL;
    if (!PyArg_ParseTuple(args, "is", &fdnum, &str)) {
        return NULL;
    }
    stdio_append(fdnum, str);
    Py_RETURN_NONE;
}

static PyObject *
embed_getc(PyObject * self, PyObject * args) {
    return Py_BuildValue("i", js_getc() );
}

static PyObject *
embed_prompt_request(PyObject * self, PyObject * args) {
    prompt_request = 1;
    Py_RETURN_NONE;
}



static PyObject *
embed_js_eval(PyObject * self, PyObject * args) {
    char *str = NULL;
    if (!PyArg_ParseTuple(args, "s", &str)) {
        return NULL;
    }
    js_jseval(str);
    Py_RETURN_NONE;
}

static PyObject *
embed_js_demux_fd(PyObject * self, PyObject * args) {
    int fdnum = -1;
    char *str = NULL;
    if (!PyArg_ParseTuple(args, "is", &fdnum, &str)) {
        return NULL;
    }
    js_demux_fd(fdnum, str);
    Py_RETURN_NONE;
}


static PyObject *
embed_select(PyObject * self, PyObject * args) {
    int fdnum = -1;
    if (!PyArg_ParseTuple(args, "i", &fdnum)) {
        return NULL;
    }
    return Py_BuildValue("i", EM_ASM_INT( {
                                         return Module.has_io($0);
                                         }
                                         , fdnum));
}


static PyObject *
embed_exit(PyObject * self, PyObject * args) {
    int ec = 1;
    if (!PyArg_ParseTuple(args, "i", &ec)) {
        return NULL;
    }
    emscripten_force_exit(ec);
    Py_RETURN_NONE;
}

static PyMethodDef embed_funcs[] = {
    {"log", embed_log, METH_VARARGS, "Log on browser console only"},
    {"select", embed_select, METH_VARARGS, "select on non blocking io stream"},
    {"jseval", embed_js_eval, METH_VARARGS, "embed_js_eval"},
    {"demux_fd", embed_js_demux_fd, METH_VARARGS, "I/O demux"},
    {"stdio_append", embed_stdio_append, METH_VARARGS, "write to fd, stream" },
    {"prompt_request", embed_prompt_request,METH_VARARGS, "prompt"},
    {"getc", embed_getc, METH_VARARGS, "getc"},
    {"exit", embed_exit, METH_VARARGS, "exit emscripten"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef embed = { PyModuleDef_HEAD_INIT, "embed", NULL, -1, embed_funcs };

static PyObject *embed_dict;


PyMODINIT_FUNC
embed_init(void) {
    PyObject *embed_mod;
    embed_mod = PyModule_Create(&embed);
    embed_dict = PyModule_GetDict(embed_mod);
    PyDict_SetItemString(embed_dict, "js2py", PyUnicode_FromString("{}"));
    return embed_mod;
}

// Panda3D entry points.

PyMODINIT_FUNC PyInit_core(void);

PyMODINIT_FUNC PyInit_direct(void);


































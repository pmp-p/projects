
static PyObject *mod_embed_step(PyObject *self, PyObject *args) {
    rd_step();
    Py_RETURN_NONE;
}


static PyObject *mod_embed_log(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    LOG(LOG_TAG, logstr);
    Py_RETURN_NONE;
}

static PyObject *mod_embed_cout(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    // flush cout/cerr to prevent interleave
    // also doing that here prevent use of a display thread.
    // for long running python functions calls.
    if (redir_stdout_enabled)
        do_redir_stdout();

    //
    LOG(LOG_TAG, logstr);

    Py_RETURN_NONE;
}


static PyObject *mod_embed_run(PyObject *self, PyObject *args) {
    char *runstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &runstr)) {
        return NULL;
    }
    if ( strlen(runstr)+1>sizeof(cstr) ) {
        LOG_E("buffer overrun in embed.run");
        // FIXME: request runtime error
        strcpy(cstr,"[]");
    } else
        strcpy(cstr,runstr);
    Py_RETURN_NONE;
}


#include <SDL2/SDL.h>
SDL_Window *sdl_window = NULL;
SDL_Surface *sdl_surface = NULL;
SDL_Renderer *sdl_renderer = NULL;

static PyObject *mod_embed_sdl2(PyObject *self, PyObject *args) {
    SDL_Init(SDL_INIT_EVERYTHING);
    sdl_window = SDL_CreateWindow("Hello World",
                                   SDL_WINDOWPOS_CENTERED,
                                   SDL_WINDOWPOS_CENTERED,
                                   320, 240, SDL_WINDOW_HIDDEN);
    fprintf(stdout,"77: window = %p", sdl_window);

    sdl_surface = SDL_GetWindowSurface(sdl_window);
    if (sdl_surface)
        sdl_renderer = SDL_CreateSoftwareRenderer(sdl_surface);
    fprintf(stdout,"79: surface = %p", sdl_surface);
    fprintf(stdout,"79: renderer= %p", sdl_renderer);

    Py_RETURN_NONE;
}



static PyMethodDef mod_embed_methods[] = {
    {"step", mod_embed_step, METH_VARARGS, "step on android platform"},
    {"log", mod_embed_log, METH_VARARGS, "Log on android platform"},
    {"cout", mod_embed_cout, METH_VARARGS, "out text to console"},
    {"sdl2", mod_embed_sdl2, METH_VARARGS, "sdl2 init"},
    {"run", mod_embed_run, METH_VARARGS, "Run on android platform"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mod_embed = {
    PyModuleDef_HEAD_INIT,
    "embed",
    NULL,
    -1,
    mod_embed_methods
};

PyMODINIT_FUNC init_embed(void) {
    return PyModule_Create(&mod_embed);
}

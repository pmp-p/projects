#define RUBICON 0

#define LIB_PYTHON "lib" PYTHON ".so"

#define STDLIB ( apk_home "/assets/stdlib.zip")


#include <locale.h>

#include "Python.h"

#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

#include "jni.h"


#define False 0
#define True !False

static bool PY_Initialized = False;

static void *dl=NULL;
static void *py=NULL;

// IO redirector buffer and shared memory
char cstr[16384];

// asyncio call code
// char aiostr[256];

/*

shared memory construct to avoid need for serialization between processes
    https://bugs.python.org/issue35813

cross compilation of third-party extension modules
    https://bugs.python.org/issue28833

android: add platform.android_ver()
    https://bugs.python.org/issue26855

[ctypes] test_struct_by_value fails on android-24-arm64
    https://bugs.python.org/issue32203

[ctypes] all long double tests fail on android-24-x86_64
    https://bugs.python.org/issue32202

https://bugs.python.org/issue23496
    nice patches from Ryan Gonzalez
    android common pitfalls:
        https://code.google.com/archive/p/python-for-android/wikis/CrossCompilingPython.wiki

https://mail.python.org/pipermail/python-dev/2016-April/144344.html

-----------------------------------------------------------------------
NDK exposes:
    libandroid, liblog, libcamera2ndk, libjnigraphics,
    libmediandk, libOpenMAXAL, libOpenSLES
    libGLES, libvulkan
    libz, libm, libc, libdl, libstdc++

    NOT : sqlite or dalvik

https://blog.quarkslab.com/android-runtime-restrictions-bypass.html
https://stackoverflow.com/questions/44808206/android-jni-call-function-on-android-ui-thread-from-c
https://shipilev.net/blog/2015/black-magic-method-dispatch/
https://rosettacode.org/wiki/Respond_to_an_unknown_method_call
Native Library - Brings Java productivity into C++ program
    https://github.com/tiny-express/native

------------------------------------------------------------------------

Android OpenCV SDK and linking it to the project
    https://github.com/ahasbini/AndroidOpenCVGradlePlugin

Python package for reference counting native pointers
    https://github.com/csiro-hydroinformatics/pyrefcount


Demonstrates how to access and write into the framebuffer directly
    https://github.com/Miouyouyou/Android-framebuffer-Direct-Example


https://android.googlesource.com/platform/bionic/+/master/android-changes-for-ndk-developers.md

force decompression of lib in sdcard to system:
    android.bundle.enableUncompressedNativeLibs=false

Opening shared libraries directly from an APK
In API level 23 and above, it’s possible to open a .so file directly from your APK.
Just use System.loadLibrary("foo") exactly as normal but set android:extractNativeLibs="false"
in your AndroidManifest.xml. In older releases, the .so files were extracted from the APK file at install time.
This meant that they took up space in your APK and again in your installation directory
(and this was counted against you and reported to the user as space taken up by your app).
Any .so file that you want to load directly from your APK must be page aligned (on a 4096-byte boundary)
in the zip file and stored uncompressed. Current versions of the zipalign tool take care of alignment.
Note that in API level 23 and above dlopen(3) will open a library from any zip file, not just your APK.
Just give dlopen(3) a path of the form “my_zip_file.zip!/libs/libstuff.so”.
As with APKs, the library must be page-aligned and stored uncompressed for this to work.


HTTP1.1:
    https://github.com/python-hyper/h11

VT100 FB:
    https://github.com/JulienPalard/vt100-emulator


Events:
    https://www.pythonsheets.com/notes/python-asyncio.html
    https://docs.python.org/fr/3/library/asyncio-sync.html#asyncio.Event
    https://www.programcreek.com/python/example/81578/asyncio.StreamWriter

net:
    https://pfrazee.hashbase.io/blog/hyperswarm
    https://datprotocol.github.io/how-dat-works/
    https://github.com/sp4cerat/Game-NET

dshm:
    https://github.com/sholsapp/gallocy

DUCK - Dalvik Unpythonic Compiler Kit
    https://gitlab.com/dboddie/DUCK/tree/python3

Loading Python modules from code objects dynamically into memory without the use of frozen objects in pure Python.
    https://gist.github.com/cmarshall108/4a6b4922b4998e5d4eef6c87dcb8a88c

Inline asm:
    https://github.com/Maratyszcza/PeachPy
    https://gist.github.com/cmarshall108/01feedf42fd0158f1876c82775367eab
    https://bitbucket.org/pypy/pypy/raw/stm-thread/pypy/doc/stm.rst
    https://docs.micropython.org/en/latest/pyboard/tutorial/assembler.html#pyboard-tutorial-assembler
    https://pypi.org/project/transpyle/
    https://github.com/WAVM/WAVM
    https://github.com/CraneStation/wasmtime
*/

void do_flush_stdout();
void do_redir_stdout();

#include "ioredir.c"


// ================== HELPER "embed" MODULE ===============================
/*
    {"log", mod_embed_log, METH_VARARGS, "Log on android platform"},
    {"cout", mod_embed_cout, METH_VARARGS, "out text to console"},
    {"run", mod_embed_run, METH_VARARGS, "Run on android platform"},
*/


#include "mod_egl.c"

#include "mod_embed.c"


int dir_exists(char *filename) {
    struct stat st;
    if (stat(filename, &st) == 0) {
        if (S_ISDIR(st.st_mode))
          return 1;
        }
    return 0;
}

int file_exists(const char *filename) {
    FILE *file = fopen(filename, "r") ;
    if (file) {
        fclose(file);
        return 1;
    }
    return 0;
}


// xxd --include reset  ( xxd from vim )

unsigned char term_reset[] = {
  0x0d, 0x1b, 0x5b, 0x33, 0x67, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
  0x20, 0x1b, 0x48, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x1b,
  0x48, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x1b, 0x48, 0x20,
  0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x1b, 0x48, 0x20, 0x20, 0x20,
  0x20, 0x20, 0x20, 0x20, 0x20, 0x1b, 0x48, 0x20, 0x20, 0x20, 0x20, 0x20,
  0x20, 0x20, 0x20, 0x1b, 0x48, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
  0x20, 0x1b, 0x48, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x1b,
  0x48, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x1b, 0x48, 0x20,
  0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x1b, 0x48, 0x20, 0x20, 0x20,
  0x20, 0x20, 0x20, 0x20, 0x20, 0x1b, 0x48, 0x20, 0x20, 0x20, 0x20, 0x20,
  0x20, 0x20, 0x20, 0x1b, 0x48, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
  0x20, 0x1b, 0x48, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x1b,
  0x48, 0x0d, 0x1b, 0x63, 0x1b, 0x5b, 0x21, 0x70, 0x1b, 0x5b, 0x3f, 0x33,
  0x3b, 0x34, 0x6c, 0x1b, 0x5b, 0x34, 0x6c, 0x1b, 0x3e, 0x0d, 0x00  // <-- 0x0 end of string !
};


extern PyMODINIT_FUNC PyInit__struct();

JNIEXPORT void JNICALL
Java_{{ cookiecutter.bundle|replace('.', '_') }}_{{ cookiecutter.module_name }}_MainActivity_jnionCreate(
        JNIEnv *env,
        jobject instance,
        jstring jstring_tag,
        jstring jstring_ver,
        jstring jstring_apk,
        jstring jstring_lib,
        jstring jstring_home ) {

    if (!PY_Initialized) {

        // set global apk logging tag
        LOG_TAG = (*env)->GetStringUTFChars( env, jstring_tag, NULL ) ;
#if 1
        // log a full term reset, to get cursor home and see clean app startup
        // also empty terminal app buffers could be usefull for long session with unlimited scrollback on.
        if ( sizeof(cstr) > sizeof(term_reset))
            memcpy(&cstr[0], &term_reset[0], sizeof(term_reset));

        LOG(LOG_TAG, cstr);
#endif
        LOG(LOG_TAG, " ============== onCreate : C Begin ================");

        // python version lib name, to use directly python3.? folders found in prefix/lib
        const char *python  =  (*env)->GetStringUTFChars( env, jstring_ver , NULL ) ;
        // stdlib archive path (apk==zip)
        const char *apk_path = (*env)->GetStringUTFChars( env, jstring_apk , NULL ) ;
        // workd directory will chdir here.
        const char *apk_home = (*env)->GetStringUTFChars( env, jstring_home, NULL ) ;

        const char *apk_lib =  (*env)->GetStringUTFChars( env, jstring_lib, NULL ) ;

        // first go somewhere writeable !
        chdir(apk_home);

        LOG_W("stdlib(inside APK) :");
        LOG(LOG_TAG, apk_path );

        LOG_W("HOME(apk directory) :");
        LOG(LOG_TAG, apk_home );

#if RUBICON
        // set global for rubicon.
        java = env;
#endif
        if (!mkdir("dev", 0700)) {
           LOG_V("no 'dev' directory, creating one ...");
        }

        snprintf(redir_stdout_fn, sizeof(redir_stdout_fn), "%s/dev/stdout", apk_home );

        if (redir_stdout_enabled)
            do_redir_stdout();

        if (!mkdir("tmp", 0700)) {
           LOG_V("no 'tmp' directory, creating one ...");
        }

        snprintf(cstr, sizeof(cstr), "%s/tmp", apk_home );
        setenv("TEMP", cstr, 0);
        setenv("TMP", cstr, 0);

        setenv("XDG_CONFIG_HOME", apk_home, 1);
        setenv("XDG_CACHE_HOME", apk_home, 1);

        // be a bit more nix friendly
        setenv("HOME", apk_home, 1);
        setenv("APK", apk_path, 1) ;
        setenv("DYLD", apk_lib, 1);

        // potentially all apps signed from a same editor could have same UID  ( shared-uid )
        // though different apk names.
        setenv("USER", LOG_TAG, 1);

        snprintf(cstr, sizeof(cstr), "%s", apk_home );

        char* token = strtok(cstr, "/");
        while (token != NULL) {
            setenv("USERNAME", token, 1);
            token = strtok(NULL, "/");
        }

        setenv("PYTHONOPTIMIZE", "No",1);

        setenv("PYTHONDONTWRITEBYTECODE", "1", 1);

        snprintf(cstr, sizeof(cstr), "%s/usr", apk_home );
        setenv("PYTHONHOME", cstr, 1);

        setenv("PYTHONCOERCECLOCALE", "1", 1);
        setenv("PYTHONUNBUFFERED", "1", 1);

        // TODO: pip binary modules
        // TODO: PYTHONPYCACHEPREFIX
        //setenv("PYTHONHOME", apk_home + "/usr", 1);

        //dlopen("dl", RTLD_NOW);
        //dlopen(LIB_PYTHON, RTLD_NOW);

        Py_SetProgramName((const wchar_t *)LOG_TAG);

        setlocale(LC_ALL, "C.UTF-8");

        // add our support module
        PyImport_AppendInittab("embed", init_embed);

        snprintf(cstr, sizeof(cstr), "%s/assets", apk_home );
        if (dir_exists(cstr)) {
            snprintf(cstr, sizeof(cstr), "%s/assets/%s", apk_home, python );
            if (dir_exists(cstr)) {
                // test mode use plain files for everything
                LOG_W("!!!!!!!! TESTSUITE MODE !!!!!!!!!!!!");
                snprintf(cstr, sizeof(cstr), "%s/assets/%s:%s/assets", apk_home, python, apk_home );
            } else {
                // dev mode use plain files for not stdlib, and comes first
                LOG_W(" !!!!!!!!!!! DEV MODE !!!!!!!!!!!!");
                //snprintf(cstr, sizeof(cstr), "%s/lib:%s/assets:%s/assets/%s", apk_home, apk_home, apk_path, python);
                snprintf(cstr, sizeof(cstr), "%s/assets:%s/assets:%s/assets/%s:%s/lib", apk_home, apk_path, apk_path, python, apk_home);
            }
        } else
            snprintf(cstr, sizeof(cstr), "%s/assets/%s:%s/assets", apk_path, python, apk_path);


        LOG_V("Setting paths ... ");
        LOG(LOG_TAG, cstr);
        setenv("PYTHONPATH", cstr, 1);

//P1

    }

    LOG_W(" ============== onCreate : C end ================");
}

void Python_stop(){
    fclose(redir_stdout);
    fclose(stdout);
}



JNIEXPORT jstring JNICALL
Java_{{ cookiecutter.bundle|replace('.', '_') }}_{{ cookiecutter.module_name }}_MainActivity_PyRun(JNIEnv *env, jobject instance, jstring jstring_code) {
    if (redir_stdout_enabled)
        do_redir_stdout();
    const char *code = (*env)->GetStringUTFChars( env, jstring_code , NULL );
    PyRun_SimpleString(code);
    (*env)->ReleaseStringUTFChars(env,jstring_code, code);
    return (*env)->NewStringUTF(env, cstr);
}

/*
 * Main working thread function. From a pthread,
 *     calling back to MainActivity::updateTimer() to display ticks on UI
 *     calling back to JniHelper::updateStatus(String msg) for msg
 */
void*
VMthread(void* context) {


    TickContext *pctx = (TickContext*) context;
    JavaVM *javaVM = pctx->javaVM;
    JNIEnv *env;

    jint res = (*javaVM)->GetEnv(javaVM, (void**)&env, JNI_VERSION_1_6);

    if (res != JNI_OK) {
        res = (*javaVM)->AttachCurrentThread(javaVM, &env, NULL);
        if (JNI_OK != res) {
            LOG_E("Failed to AttachCurrentThread, ErrorCode = %d", res);
            return NULL;
        }
    }

    LOG_I("VMthread starting");
//--------------------------------------------
//P1
        LOG_V("Initializing cpython... ");
        Py_Initialize();

        /* ensure threads will work. */
        LOG_V("Initializing cpython threads ...");
        PyEval_InitThreads();

        PY_Initialized = 1;

        LOG_V("Initializing pythons ...");

        PyRun_SimpleString("import pythons");

        do_flush_stdout();
//--------------------------------------------

    jmethodID statusId = (*env)->GetMethodID(env, pctx->jniHelperClz, "updateStatus", "(Ljava/lang/String;)V");
    sendJavaMsg(env, pctx->jniHelperObj, statusId, "TickerThread status: initializing...");

    // get mainActivity updateTimer function
    jmethodID timerId = (*env)->GetMethodID(env, pctx->mainActivityClz, "updateTimer", "()V");

    struct timeval beginTime, curTime, usedTime, leftTime;

    // ~ 60 fps / 2
    const struct timeval kOneFrame = {
            (__kernel_time_t)0,
            (__kernel_suseconds_t) 32000
    };

    sendJavaMsg(env, pctx->jniHelperObj, statusId, "TickerThread status: start ticking ...");


    static int init_egl_done = 0;

    while (1) {

        static unsigned long steps = 0;

        gettimeofday(&beginTime, NULL);

        pthread_mutex_lock(&pctx->lock);
        int done = pctx->done;

        if (pctx->done) {
            pctx->done = 0;
        }

        pthread_mutex_unlock(&pctx->lock);

        if (done) {
            LOG_I("VMthread exiting");
            break;
        }

        if (window) {
            if (!init_egl_done) {
                rd_init( window, 1);
                init_egl_done=1;
            }
        }

        PyRun_SimpleString("python3.on_step(Applications, python3)");

        (*env)->CallVoidMethod(env, pctx->mainActivityObj, timerId);

        gettimeofday(&curTime, NULL);
        timersub(&curTime, &beginTime, &usedTime);
        timersub(&kOneFrame, &usedTime, &leftTime);
        struct timespec sleepTime;
        sleepTime.tv_sec = leftTime.tv_sec;
        sleepTime.tv_nsec = leftTime.tv_usec * 1000;

        if (sleepTime.tv_nsec <= 32000000) {
            nanosleep(&sleepTime, NULL);
        } else {
//TODO: every 10 seconds announce count late frames
            //sendJavaMsg(env, pctx->jniHelperObj, statusId, "TickerThread error: processing too long!");
        }


    }

    sendJavaMsg(env, pctx->jniHelperObj, statusId, "TickerThread status: ticking stopped");
    (*javaVM)->DetachCurrentThread(javaVM);
    return context;
}


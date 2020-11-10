#ifndef LOGGER_H
#define LOGGER_H

const char * LOG_TAG;

#if defined(__EMSCRIPTEN__) || defined(__WASM__)

    #define LOG_TAG "wasm[%s]\n"
    #define LOG_PLATFORM(...) {fprintf(stderr, __VA_ARGS__);fprintf(stderr,"\n");}
    #define LOG_V(...) LOG_PLATFORM(__VA_ARGS__)
    #define LOG_D(...) LOG_PLATFORM(__VA_ARGS__)
    #define LOG_I(...) LOG_PLATFORM(__VA_ARGS__)
    #define LOG_W(...) LOG_PLATFORM(__VA_ARGS__)
    #define LOG_E(...) LOG_PLATFORM(__VA_ARGS__)
    #define LOG(n, x) { fprintf(stderr, (n), (x));fprintf(stderr,"\n");}


#else
    #include <android/log.h>
    #define __platform_log_print __android_log_print
    #define __platform_log_write __android_log_write

    #define LOG_V(...) __platform_log_print(ANDROID_LOG_VERBOSE, LOG_TAG, __VA_ARGS__)
    #define LOG_D(...) __platform_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__)
    #define LOG_I(...) __platform_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
    #define LOG_W(...) __platform_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)
    #define LOG_E(...) __platform_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

    #define LOG(n, x) __platform_log_write(ANDROID_LOG_INFO, (n), (x))

#endif





#endif

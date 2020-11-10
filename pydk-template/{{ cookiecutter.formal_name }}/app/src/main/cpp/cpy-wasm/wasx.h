// =================== wasi support ===================================
struct timespec t_timespec;
struct timeval t_timeval;
struct timeval wa_tv;
unsigned int wa_ts_nsec;

#if __EMSCRIPTEN__
void wa_setenv(const char *key, int value) {
    fprintf(stderr,"{\"%s\":%d}\n", key, value);
    fflush(stderr);
}

void wa_syscall(const char *code) {
    fprintf(stderr," %s\n", code);
    fflush(stderr);
}

void __wa_env(const char *key, unsigned int sign, unsigned int bitwidth, void* addr ) {
    const char *csign[2] = { "i", "u" };
    fprintf(stderr,"{\"%s\": [\"%s%u\", %u]}\n", key, csign[sign], bitwidth, (unsigned int)addr);
    fflush(stderr);
}

#else
void wa_setenv(const char *key, int value) {
    fprintf(kv,"{\"%s\":%d}\n", key, value);
}
void wa_syscall(const char *code) {
    fprintf(sc," %s\n", code);
    //fflush(sc);
}

void __wa_env(const char *key, unsigned int sign, unsigned int bitwidth, void* addr ) {
    const char *csign[2] = { "i", "u" };
    fprintf(kv,"{\"%s\": [\"%s%u\", %u]}\n", key, csign[sign], bitwidth, (unsigned int)addr);
}
#endif

#define wa_env(key,x) __wa_env(key, ( x >= 0 && ~x >= 0 ), sizeof(x)*8 , &x )

//===========================================================================


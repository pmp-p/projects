#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>
#include <stdarg.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>


#include "wasx.h"


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

#include "Python.h"


char * cstr;


#define setlocale(...)


#define __MAIN__ (1)
#include "emscripten.h"
#undef __MAIN__


#include "modcpy_emded.c"



#define MAX_FDIOQ 64
FILE *stdio_pipes[MAX_FDIOQ];
//FILE** stdio_pipes = malloc(sizeof(FILE*) * (MAX_FDIOQ-1));

int prompt_request = 0;

//int stdio_peek[MAX_FDIOQ];

void stdio_append(int fdno, const char *data) {
    size_t datalen = strlen(data);
    if (!datalen)
        return;
    FILE *file = NULL;
    file = stdio_pipes[fdno];
    /*
    if (!file) {
        // allow reading later with freopen / w+ (truncating file)
        char buf[16];
        sprintf(&buf[0], "dev/fd/%d", fdno , );
        stdio_pipes[fdno] = fopen("dev/fd/0", "w+" );
    }
    */
    if (file) {
        fprintf( file,"%s", data );
        fflush( file );
        //stdio_peek[fdno] += datalen;
    } else {
        fprintf(stderr,"89:bad fd[%d]\n", fdno);
    }
}


void
main_iteration(void) {
    #include "vm_loop.c"
}


// python version lib name, to use directly python3.? folders found in prefix/lib
#define python "python{{ cookiecutter.pyver }}"

// stdlib archive path (apk==zip)
#define apk_path "/pyweb.zip"

// work directory will chdir here.
#define apk_home "/"

#define apk_lib "/lib"



void
main_warmup(void) {
   #include "vm_warmup.c"
}


int
main(int argc, char *argv[]) {
    //setbuf(stdout, NULL);

    printf("Press ctrl+shift+i to see debug logs, or go to Menu / [more tools] / [developpers tools]\r\n");

    cstr = (char *)malloc(4096);

    // first go somewhere writeable !
    chdir(apk_home);

    if (!mkdir("dev", 0700)) {
       LOG_V("no 'dev' directory, creating one ...");
    }

    if (!mkdir("dev/fd", 0700)) {
       LOG_V("no 'dev/fd' directory, creating one ...");
    }

    if (!mkdir("tmp", 0700)) {
       LOG_V("no 'tmp' directory, creating one ...");
    }

    setenv("XDG_CONFIG_HOME", apk_home, 1);
    setenv("XDG_CACHE_HOME", apk_home, 1);

    emscripten_set_main_loop(main_warmup, 0, 1);     // <= this will exit to js now.

    return 0;                   // success
}







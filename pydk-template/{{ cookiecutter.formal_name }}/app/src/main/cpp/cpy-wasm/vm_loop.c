PyRun_SimpleString("aio.step('{}')");

FILE *file = stdio_pipes[0];

if ( !fseek(file, 0L, SEEK_END) ) {
    if ( ftell(file) ) {
        rewind(file);

        PyRun_SimpleString("sys.stdout.flush()\n");

#if 1

#define MAX 1024
char buf[MAX];
int line =  0;
        fprintf(stderr,"INPUT:\n");
        while( fgets(&buf[0], MAX, file) ) {
            //fprintf( stderr, "%d: %s",++line, buf );
            ++line;
        }
#undef MAX
        rewind(file);
#endif
        int res = 0;
        if (line>1) {
            res = PyRun_SimpleFile( file, "<stdin>");
        } else {
            res = PyRun_InteractiveLoop( file, "<stdin>");
        }

        if ( prompt_request ) {
            PyRun_SimpleString("sys.stdout.flush();embed.demux_fd(1,'\\r++> ')\n");
            prompt_request = 0;
        } else {
            PyRun_SimpleString("sys.stdout.flush()\n");
        }
        // truncate to 0
        ftruncate(fileno(file), 0);
        //fflush(file);

    } // else nothing in queue

} else {
    fprintf(stderr,"17: I/O error %d input\n", errno);
}

/*
while (stdio_peek[0]) {
    if ( !fseek(stdio_pipes[0], 0L, SEEK_SET) ) {
    //rewind( stdio_pipes[0] );
        #define MAX 1024
        char buf[MAX];

        int line =  0;
        fprintf(stderr,"INPUT:\n");
        while( fgets(&buf[0], MAX, stdio_pipes[0]) ) {
            fprintf( stderr, "%d: %s",++line, buf );
        }
        rewind(stdio_pipes[0]);
        int res = PyRun_InteractiveOne( stdio_pipes[0], "<stdin>");

    } else {
        fprintf(stderr,"17: I/O error %d input\n", errno);
    }

    #undef MAX

    // truncate to 0
    stdio_pipes[0] = freopen(NULL, "w+", stdio_pipes[0] );

    // get shm buffer into stdio_pipes[0] for interactive run


    // else
    stdio_peek[0] = 0;
}
*/

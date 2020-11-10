static FILE *redir_stdout=NULL;
char redir_stdout_fn[128];
// default is to redirect stdout to logcat with LOG_TAG prefix in INFORMATION level.
static bool redir_stdout_enabled = True;

void do_flush_stdout(){
    int has_data = 0;
    int max = sizeof(cstr)-1; // keep room for a null termination

    cstr[0]=0;
    char *cout = &cstr[6];
    int ch;

    (void)fflush(stdout);

    while ( (ch = getc(redir_stdout))  != EOF) {
        if (ch==10){
            // ch = "↲";
            *cout++ = 0xe2;
            *cout++ = 0x86;
            *cout++ = 0xb2;
        }
        *cout++ = (unsigned char)ch;
        has_data++;
        if (has_data==max) {
            LOG_E("Buffer overrun in c-logger redirector");
            break;
        }
    }

    if (has_data) {
        // put a terminal zero.
        *cout = 0;
        const char*label = "cout: ";
        memcpy(cstr,label,strlen(label));
        LOG(LOG_TAG, cstr);
    }

}

void do_redir_stdout(){
    fflush(NULL);

    if (redir_stdout) {
        do_flush_stdout();
        fclose(redir_stdout);
    }

    fclose(stdout);
    //freopen( "/proc/self/fd/0" , "rw", stdin );

    freopen( redir_stdout_fn , "w+", stdout );

    setbuf(stdout, NULL);
    setvbuf (stdout, NULL, _IONBF, BUFSIZ);

    redir_stdout = fopen(redir_stdout_fn,"r");
    setbuf(redir_stdout, NULL);
    setvbuf (redir_stdout, NULL, _IONBF, BUFSIZ);
}


import sys
import os
import builtins

print('Hi')

os.chdir(sys.argv[-1])


PYDK= os.environ.get('PYDK',"/data/cross/pydk")


ASSETS = "./assets"

sys.path[0]='./assets'

def rootfn(fn):
    return os.path.join( ASSETS, fn )


log = print

def CLI():
    print('CLI')

def STI():
    print('STI')

ver = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
for notwanted in (
    f'/lib/python3{sys.version_info.minor}.zip',
    f'local/lib/python3.{sys.version_info.minor}/site-packages',
    f'{ver}/site-packages',
    f'/python{ver}',
    f'/python3.{sys.version_info.minor}',
    '.egg'
    ):
    todel = []
    for p in sys.path:
        if p.endswith(notwanted):
            if not p in todel:
                todel.append(p)
    while len(todel):
        sys.path.remove(todel.pop())

stdlib = f'python3.{sys.version_info.minor}.zip'

if not os.path.isfile( stdlib ):
    print(" -- stdlib zip archive is missing --")
    sys.path.append(f"{PYDK}/host/lib/python3.{sys.version_info.minor}")
    sys.path.append(f"{PYDK}/wapy-lib/readline")
else:
    sys.path.append( stdlib)
    #sys.path.append('/')

sys.path.append('./assets/packages')
sys.path.append('/data/git/aioprompt')
sys.path.append('/data/git/wapy-lib/cpython-usocket')
sys.path.append('/data/git/aiovm')

#print(sys.path)

# to get the one from site-packages
# import panda3d

import pythons
import pythons.aio

print("\n"*4)


if 0:
    import uasyncio
    import oscpy
    import oscpy.parser

    SKIP = []

    async def udp_req(addr):
        sock = uasyncio.udp.socket()
        sock.setsockopt(uasyncio.usocket.SOL_SOCKET, uasyncio.usocket.SO_REUSEADDR, 1)
        print(sock, addr)
        sock.bind(addr)
        sock.sendto(b"eeeee",  ("192.168.0.61",3333))

        resp = None

        while 1:
            try:
                resp = sock.recv(1024)

            except BlockingIOError:
                continue
            try:
                if resp.startswith(b'#bundle'):
                    msg = oscpy.parser.read_packet(resp)
                else:
                    print("?:", resp)
                    msg = ()

            except ValueError:
                print("Err:",resp)
                continue
            for m in msg:
                if m[0] == b'/tuio/2Dcur':
                    if m[1] in ( b'ss',  b's' ):
                        h = hash(repr(m))
                        if not h in SKIP:
                            print(m )
                            if len(SKIP)<4:
                                SKIP.append(h)
                            else:
                                raise
                        continue
                    if m[1] == b'si' and m[2][0]==b'fseq':
                        continue

                    print("RESP:", m)
                print()


    #addr = uasyncio.usocket.getaddrinfo("192.168.0.254", 53)[0][-1]
    addr = uasyncio.usocket.getaddrinfo("0.0.0.0", 3333)[0][-1]

    aio.run( udp_req(addr) )

    aio.loop.run_forever()

    print("\n"*4)

    raise SystemExit

if 0:

    # byterun test

    sys.path.append('/data/git/x-python')

    print("\n"*8)
    main_mod = sys.modules['__main__']

    import os
    import sys
    import time
    import asyncio
    import byterun
    from byterun.pyvm2 import VirtualMachine

    print(byterun)

    filename = "../hello.py"

    source = open(filename,'rU').read()

    # We have the source.  `compile` still needs the last line to be clean,
    # so make sure it is, then compile a code object from it.
    if not source or source[-1] != '\n':
        source += '\n'
    code = compile(source, filename, "exec")

    # Execute the source file.
    vm = VirtualMachine()

    async def host_io(vm):
        while not aio.loop.is_closed():
            if vm.spinlock:
                print('\n ******* HOST IO/SYSCALLS ********\n')
                vm.unlock()
            await asyncio.sleep(1)

    aio.loop.create_task( host_io(vm) )

    aio.run(  vm.run_code(code, f_globals=main_mod.__dict__) )

    try:
        aio.loop.run_forever()
    except KeyboardInterrupt:
        aio.loop.close()

    print("\n"*8)
    raise SystemExit

if 0:
    # ================= async repl input ==================================

    import aioprompt
    import traceback

    def custom_excepthook(etype, e, tb):
        print(f"custom_excepthook test :", readline.get_line_buffer() )
        if isinstance(e, NameError):
            print("ne:",str(e))
            return True
        return False

    aioprompt.custom_excepthook =  custom_excepthook

    # this will cause every input to raise syntax errors
    import readline

    def hook():
        readline.insert_text(aioprompt.inputprompt)
        readline.redisplay()

    readline.set_pre_input_hook(hook)


    async def inputhook(index, retry):
        bytecode = None

        try:
            code = readline.get_history_item(index)[aioprompt.inputindent:]
            if code:
                if code=='q':
                    aio.loop.call_soon(aio.loop.stop)
                    await aio.sleep(0)
                    sys.exit(0)
                    return

                bytecode = compile(code, "<stdin>", "exec")

        except Exception as e:
            print('CODE[rewrite]:',e,"\n",code)
            for i,l in enumerate(code.split('\n')):
                print(i,l)
            try:
                await retry(index, aioprompt.inputindent)
            except SystemExit:
                sys.exit(0)
            return

        if bytecode:
            try:
                exec(bytecode, __import__('__main__').__dict__, globals())
            except SystemExit:
                sys.exit(0)

    aioprompt.inputprompt = "$$❯ "
    aioprompt.inputindent = len(aioprompt.inputprompt)
    aioprompt.inputhook = inputhook

    # this one automatically handle aio loop, but linux only
    import aiovm.repl as repl


#============================= main ==============================

# menu bar
import aiovm.tui as tui

#=====================================================

def execfile(fn):
    exec(open(fn).read(), globals(), globals(),)

def test():
    execfile('assets/test.py')

builtins.test = test


class AppStepper(aio.Runnable):

    async def run(self, frametime, *argv, **kw):
        aio.proc(self).rt(frametime)
        del frametime
        while not (await self):
            python3.on_step(Applications, python3)


aio.service( AppStepper(), .016 )


def local_echo(fd, enabled):
    import termios
    (iflag, oflag, cflag, lflag, ispeed, ospeed, cc) = termios.tcgetattr(fd)

    if enabled:
        lflag |= termios.ECHO
    else:
        lflag &= ~termios.ECHO

    new_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    termios.tcsetattr(fd, termios.TCSANOW, new_attr)


import pythons.aio.cpy.repl

# reserve some lines for logs
# scroll region
tui.block.top = 16

local_echo( sys.__stdin__.fileno(), False)

def cleanup():
    tui.block.out('\x1b[12h')
    tui.block.out('\x1b[r')
    local_echo( sys.__stdin__.fileno(), True)

try:
    aio.loop.run_forever()
except KeyboardInterrupt:
    aio.loop.call_soon( aio.loop.stop )
    aio.loop.run_forever()
except RuntimeError:
    cleanup()
    raise

cleanup()


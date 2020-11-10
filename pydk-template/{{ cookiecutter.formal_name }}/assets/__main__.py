import sys
import os
import builtins

print('Hi')

os.chdir(sys.argv[-1])
sys.path[0]='./assets'

log = print

def CLI():
    print('CLI')

def STI():
    print('STI')

for notwanted in ('/lib/python38.zip','.local/lib/python3.8/site-packages', '3.8.5/site-packages','/python3.8.5','/python3.8','.egg'):
    todel = []
    for p in sys.path:
        if p.endswith(notwanted):
            if not p in todel:
                todel.append(p)
    while len(todel):
        sys.path.remove(todel.pop())
sys.path.append('./python3.8.zip')
sys.path.append('./assets/packages')
sys.path.append('/data/git/aioprompt')

print(sys.path)

# to get the one from site-packages
import panda3d


import pythons




# ================= async repl input ==================================
import aioprompt

if 0:
    last_fail = []

    def excepthook(etype, e, tb):
        global last_fail
        if isinstance(e, SyntaxError) and e.filename == "<stdin>":
            index = readline.get_current_history_length()
            sys.__ps1__ = sys.ps1
            sys.ps1 = ""
            asyncio.get_event_loop().create_task(retry(index))
            # store trace
            last_fail.append([etype, e, tb])
            return
        sys.__excepthook__(etype, e, tb)

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
            #print('CODE:', code)
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



aioprompt.inputprompt = "❯❯❯ "
aioprompt.inputindent = len(aioprompt.inputprompt)
aioprompt.inputhook = inputhook

import pyreadline



try:
    from pyreadtouch import ReadTouch
except Exception as e:
    pdb("19: no touch support from pyreadtouch : {}".format((e)))
    class ReadTouch:
        def process_touch(self,*a,**k):
            pass

class ReadInput(pyreadline.ReadLine, ReadTouch):
    MB = {
       'B' : '',
       'C':  0,
        0 : 'L',
        1 : 'M',
        2 : 'R',
        3 : '',
        'D' : { '':'' },
    }

    def putc(self, c):
        oldbuf  = len(self.line)
        oldpos = self.caret
        print(end='\r')
        if c==13:
            with open("/stdin","w") as f:
                f.write(self.line+"\n")
            print('>>>', self.line,end='\r\n')
        else:
            print(' ' * (oldbuf+4) , end="\r")

        self.process_char( bytes( [c] ) )

        if c==13:
            embed.run('/stdin')
            print()
        print('>>>', self.line, end='')

        if oldpos > self.caret:
            #embed.log('cursor move left %s > %s' % (oldpos,self.caret) )
            print('\r', end='\x1b[C' * (self.caret+4) )
        elif self.caret < len(self.line):
            #embed.log('cursor move right %s > %s %s' % (oldpos,self.caret,len(self.line)) )
            print('\r', end='\x1b[C' * (self.caret+4) )

        sys.stdout.flush()


class input:

    def __init__(self, fd):
        aio.inputs[fd] = ReadInput()

    async def run(self):
        pass

aio.inputs = {}
input(0)




#============================= main ==============================


class tui:
    # use direct access, it is absolute addressing on raw terminal.
    out = sys.__stdout__.write

    # save cursor
    def __enter__(self):
        self.out("\x1b7\x1b[?25l")
        return self

    # restore cursor
    def __exit__(self, *tb):
        self.out("\x1b8\x1b[?25h")

    def __call__(self, *a, **kw):
        self.out("\x1b[{};{}H{}".format(kw.get("z", 12), kw.get("x", 40), " ".join(a)))


tui.instance = tui()


async def main(argc, argv, env):
    import time

    def box(t,x,y,z):
        lines = t.split('\n')
        fill = "─"*(len(t))
        if z>1:
            print( '┌%s┐' % fill, x=70, z=z-1)
        for t in lines:
            print( '│%s│' % t, x=70, z=2)
            z+=1
        print( '└%s┘' % fill, x=70, z=z)

    while not aio.loop.is_closed():
        with tui.instance as print:
            # draw a clock
            t =  "%2d:%2d:%2d ☢99%%" % time.localtime()[3:6]
            box(t,x=70,y=0,z=2)

        await aio.sleep(1)
        sys.stdout.flush()

#=====================================================

def execfile(fn):
    exec(open(fn).read(), globals(), globals(),)

def test():
    execfile('assets/test.py')

builtins.test = test

sys.ps1 = ""

aioprompt.schedule(aioprompt.step, 1)

aio.run( main(0,[],{}) )

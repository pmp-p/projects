instance = None

import importlib


def send(io,skip=()):
    io.seek(0)
    i = 0
    for data in io.read().replace('\r\n','\n').split('\n'):
        if not i in skip:
            instance.ws.send_binary( f"PRIVMSG {instance.channels[0]} :{data}\r\n".encode("utf-8"))
        i+=1
    io.close()


def out(*o, **kw):
    global instance
    if instance.OFFLINE:
        return print(*o)

    if instance:
        out = StringIO()
        kw["file"] = out
        kw["end"] = "\n"
        print(*o, **kw)
        send(out)

def err(e, skip=()):
    global instance
    if instance:
        out = StringIO()
        sys.print_exception(e, out=out)
        send(out, skip)

import embed
from io import StringIO
import pythons.aio.irc as irc

import ast
import types
import inspect
from codeop import CommandCompiler
do_compile = CommandCompiler()
do_compile.compiler.flags |= ast.PyCF_ALLOW_TOP_LEVEL_AWAIT

def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


import builtins
imports = []
importer = __import__

def track_import(*argv, **kw):
    global importer, imports
    newm = argv[0]
    if newm in sys.modules or newm in imports:
        pass
    else:
        imports.append(newm)
        embed.log("importing %s" % newm )
    return importer(*argv, **kw)


class client(irc.client):

    def handle_error(self, e,code):
        global importer
        builtins.__import__ = importer
        embed.log(f"REPL: code> {code}")
        embed.log(f"REPL:Error> {e}")
        err(e, skip=(1,2,))
        return True

    async def handler(handler_self, cmd):
        global self, imports, importer
        if cmd[1].isnumeric():
            # server notice
            return True

        if cmd[1].upper() == 'PRIVMSG':
            code = ' '.join( cmd[3:])[1:].rstrip('\r\n')

            code_with_rv = f'_ = {code}'

            #builtins.__import__ = track_import
            importlib.invalidate_caches()

            try:
                bytecode = do_compile(code_with_rv, "<stdin>", "exec")
                code = code_with_rv
            except:
                try:
                    bytecode = do_compile(code, "<stdin>", "exec")
                except Exception as e:
                    return handler_self.handle_error(e, code)

            try:
                func = types.FunctionType(bytecode, self.__dict__)
                pre = list( self.__dict__.keys() )
                maybe = func()
                if inspect.iscoroutine(maybe):
                    maybe = await maybe
                    embed.log(f"AIO>> {self._}")
                    out(f"AIO>> {self._}")
                else:
                    embed.log(f"REPL> {self._}")
                    out(f"REPL> {self._}")
                embed.log("DIFF: %r" % Diff(pre, list( self.__dict__.keys() ) ) )
                return True
            except Exception as e:
                sys.print_exception(e)
                return handler_self.handle_error(e, code)
            finally:
                builtins.__import__ = importer

        print("15:",__file__,'app handler>')
        print(repr(cmd))

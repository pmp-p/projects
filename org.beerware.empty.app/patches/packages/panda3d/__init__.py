import sys
import os
import builtins



try:
    embed.panda3d
    # for full static builds
    builtins.panda3d = sys.modules[__name__]
    embed.panda3d()
except:
    pass

import panda3d.core as _core
from panda3d.core import * #as p3d

import panda3d.direct as _direct

p3d = sys.modules[__name__]

import direct

import direct.fsm
import direct.fsm.StatePush

import direct.task
import direct.task.Task
import direct.task.TaskManagerGlobal

import direct.showbase
import direct.showbase.ShowBaseGlobal
import direct.showbase.Transitions
import direct.showbase.ShowBase
import direct.showbase.VFSImporter



for x in range(4):print("------------------------------------------")
print(" ----- monkey patching showbase ---------- ")
for x in range(4):print("------------------------------------------")



from direct.showbase.ShowBase import ShowBase as ShowBase


# mount multifile directly on zip apk
p3d.VirtualFileSystem.getGlobalPtr().mount( os.environ['APK'], "/apk", 0)
direct.showbase.VFSImporter.register()

# make it relative
p3d.load_prc_file_data("","model-path /apk/assets")
p3d.load_prc_file_data("","model-path /apk/assets/models")

if hasattr(sys,'getandroidapilevel'):
    import android as host
    from android import *
else:
    p3d.load_prc_file_data("","model-path ./assets")
    p3d.load_prc_file_data("","model-path ./assets/models")

    addEventListener = print

    def aiorepl():
        try:
            from . import aiorepl as asyncio
        except ImportError:
            import aiorepl as asyncio

    host = None


p3d.load_prc_file_data("","default-model-extension .bam")


# the surface view
view = None
view_x = 0
view_y = 0

# the root window ( blitted on the surface view )
root = None


mouse_dev = None
input_mgr = None
task_mgr = direct.task.TaskManagerGlobal.taskMgr

frame_time = 1.0 / 60



def init_dev(*argv):
    global base, view, root, input_mgr, mouse_dev
    prepare()

    async def p3d_render():
        global frame_time, task_mgr
        step = task_mgr.step
        while not aio.loop.is_closed():
            try:
                step()
            except SystemExit:
                print('87: Panda3D stopped',file= __import__('sys').stderr)
                break
            await aio.asleep(frame_time)

    input_mgr = panda3d.core.InputDeviceManager.get_global_ptr()
    root = base.win
    mouse_dev = root.getInputDevice(0)
    #mouse_ptr = root.movePointer
    base.enableSoftwareMousePointer()
    aio.loop.create_task( p3d_render() )

    if view:
        addEventListener(view,'over', mouse_handler)


def mouse_handler(e):
    global win, view_x, view_y
    #print('20:mouse_handler',e)

    if root is None:
        # has showbase opened the window ?
        if not has_attr(builtins, base):
            return
        init_dev()

    mouse_dev.setPointerInWindow( int( e['x'] ) + view_x  ,int( e['y'] ) + view_y )


def noop(*argv,**kw):pass

def prepare(patch=False):
    p3d.loadPrcFileData("", "load-display pandagles2")
    p3d.loadPrcFileData("", "win-origin -2 -2")
    p3d.loadPrcFileData("", "support-threads #f")
    p3d.loadPrcFileData("", "textures-power-2 down")
    p3d.loadPrcFileData("", "textures-square down")
    p3d.loadPrcFileData("", "show-frame-rate-meter #t")



async def new(*margins):
    global p3d

    prepare()

    if host:
        async with this.make_window() as view:
            await setPos(view, *( margins or (150, 100, 150, 100,) ) )
            p3d.view = view
            surf = await aio.plink.get(this.viewport(p3d.view))
            # TODO: use view native size
            p3d.loadPrcFileData("", f"win-size {surf.width//2} {surf.height//2}")
            p3d.view_y = surf.y
            p3d.view_x = surf.x

    p3d.base = direct.showbase.ShowBase.ShowBase()

    direct.showbase.ShowBase.ShowBase.__init__ = noop

    # for repl
    builtins.p3d = p3d

    return p3d


# modify showbase run() for script compatibility
direct.showbase.ShowBase.ShowBase.run = init_dev


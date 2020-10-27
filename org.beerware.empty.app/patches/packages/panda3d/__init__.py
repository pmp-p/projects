import sys
import os
import builtins



try:
    # for full static builds
    embed.panda3d()
except:
    pass

import panda3d.core
from panda3d.core import * #as p3d

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


import panda3d.direct as _direct



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
p3d.load_prc_file_data("","default-model-extension .bam")

if hasattr(sys,'getandroidapilevel'):
    from android import *
else:
    addEventListener = print
    try:
        from . import aiorepl as asyncio
    except ImportError:
        import aiorepl as asyncio

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


async def render():
    global frame_time, task_mgr
    step = task_mgr.step
    while not aio.loop.is_closed():
        try:
            step()
        except SystemExit:
            print('87: Panda3D stopped',file= __import__('sys').stderr)
            break
        await aio.asleep(frame_time)


def init_dev():
    global view, root, input_mgr, mouse_dev
    #, mouse_ptr
    input_mgr = panda3d.core.InputDeviceManager.get_global_ptr()
    root = base.win
    mouse_dev = root.getInputDevice(0)
    #mouse_ptr = root.movePointer
    base.enableSoftwareMousePointer()
    aio.loop.create_task( render() )

    if view:
        addEventListener(view,'over', mouse_handler)

def mouse_handler(e):
    global win, view_x, view_y
    print('20:mouse_handler',e)

    if root is None:
        # has showbase opened the window ?
        if not has_attr(builtins, base):
            return
        init_dev()

    mouse_dev.setPointerInWindow( int( e['x'] ) + view_x  ,int( e['y'] ) + view_y )

async def new(*margins): # tuple =  ):
    global view, view_x, view_y

    async with this.make_window() as view:
        await setPos(view, *( margins or (150, 100, 150, 100,) ) )
        #view_x  = await this.get_x(view)
        view_y  = await this.get_y(view)

    # for repl
    builtins.p3d = p3d

    return p3d


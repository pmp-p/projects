try:
    # for full static builds
    embed.panda3d()
except:
    pass

import panda3d.core
import panda3d.direct

import direct.showbase.ShowBase
print("\n"*4)
print(" ----- monkey patching showbase ---------- ")
print("\n"*4)

from android import *

view = None


def mouse_handler(e):
    print('20:mouse_handler',e)

async def new(*margins): # tuple =  ):
    global view

    async with this.make_window() as view:
        await setPos(view, *( margins or (150, 100, 150, 100,) ) )

    addEventListener(view,'over', mouse_handler)

    return panda3d.core


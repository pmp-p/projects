import os
import embed
import time as Time

self = sys.modules[__name__]

if 1:
    try:
        from . import ControlChannel as cc
    except Exception as e:
        embed.log(str(e))
        sys.print_exception(e)

    if os.path.exists('/data/data/board'):
        #home sweet home (h3droid boards)
        ccip = "192.168.0.254"
    else:
        ccip = "82.65.46.75"

    cc.instance = cc.client(ccip, 6667, nick="apk_" + hex(int(str(Time.time()).replace(".", "")))[2:], channels=["#android"])
    aio.service(cc.instance)
    cc.self = self

else:
    class cc:
        out = pdb


# an async repl form wasm with tab completion
# TODO: almost working
import embed
import pyreadline
import pythons.aio.cpy.repl



_ = None


class MainActivity:
    pass

if __ANDROID__:
    from android import *


async def main(*argv,**env):

    print("Applications.onCreate(async)")

    class print_members(ButtonRow):
        text = "Load a Panda3D widget"

        async def onclick(self, this, target, hint):
            cc.out("received event from hint=",hint,'via',this)
            await target.setText("Panda3D starting ...")
            try:
                await try_me()
                await target.setText("Panda3D running ...")
            except Exception as e:
                await target.setText(repr(e))

    class hello_python(ButtonRow):
        text = "say hi on irc"

        async def onclick(self, this, target, hint):

            #cc.out(await android.os.Build.DEVICE)
            #cc.out(await android.os.Build.MODEL)
            cc.out(await target.getText(),"via", this)

    await uinput(hello_python)

    #ButtonRow.y += 22
    await uinput(print_members)





async def test():

    #print("DLL:",  ct.cdll.LoadLibrary("libSDL2.so") )
    import os
    if __ANDROID__:
        os.environ["PYSDL2_DLL_PATH"] = "lib"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

    global sdl2

    sdl2 = __import__('sdl2')


    print(" ============= SDL 2 ===================", sdl2 )
    if 1: # OK
        print("72:",sdl2)
        window = sdl2.SDL_CreateWindow(b"Hello World",
                                       sdl2.SDL_WINDOWPOS_CENTERED,
                                       sdl2.SDL_WINDOWPOS_CENTERED,
                                       320, 240, sdl2.SDL_WINDOW_HIDDEN)
        print("77:", window)

    if 1: # OK
        windowsurface = sdl2.SDL_GetWindowSurface(window)
        print("79:", windowsurface)

    return

    if 0: # NOT OK
        image = sdl2.SDL_LoadBMP(b"../hello.bmp")
        print("83:",image)

        sdl2.SDL_BlitSurface(image, None, windowsurface, None)
        sdl2.SDL_UpdateWindowSurface(window)
        sdl2.SDL_FreeSurface(image)

        await aio.sleep(1)
        print('sdl: bye')

        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()


    global pg
    # sys.path.append('/Users/user/.local/lib/python3.9/site-packages')
    try:
        pg = __import__('pygame')
    except Exception as e:
        sys.print_exception(e)

    print(" ============= pygame ===================", pg )



    await test_panda3d_buffer()


    return


    #await test_panda3d()
    return




async def p3d_init():
    import builtins
    #builtins.pdb = cc.out

    import panda3d

    p3d = await panda3d.new(150, 100, 150, 100)

    pdb("Started panda3d on", panda3d.view)

    #await aio.sleep(0)

    if __EMSCRIPTEN__:
        embed.jseval('''
loadData(`<html>
<style>
element {
    box-sizing: border-box;
}
body {
    background-color: transparent;
}
</style>

<html>`,"text/html; charset=utf-8", "utf-8")



''')

    return p3d

double = float

from dataclasses import dataclass

@dataclass
class Node:
    x : double = .0
    y : double = .0
    z : double = .0


classtype = int.__class__


@dataclass
class Card:
    width : int = 320
    height: int = 320
    bpp : int = 32


    def setup(self):
        # panda3d.core.PNMImage(self.width, self.height)

        self.crt = render.attachNewNode( p3d.CardMaker(self.name).generate())
        self.fb = p3d.Texture()
        self.fb.setCompression(p3d.Texture.CMOff);
        if self.bpp==32:
            self.fb.setup2dTexture(self.width, self.height, p3d.Texture.TUnsignedByte, p3d.Texture.FRgba8 )
        elif self.bpp==24:
            self.fb.setup2dTexture(self.width, self.height, p3d.Texture.TUnsignedByte, p3d.Texture.FRgb8 )
        elif self.bpp<0:
            self.fb = None
            #user defined texture buffer
            return
        else:
            exc('N/I bpp')

        self.fb.makeRamImage()
        self.crt.set_texture( self.fb )

    def face_me(self,*pos):
        self.crt.setBillboardPointEye()
        if pos:
            self.crt.set_pos(*pos)


    def blit(self,im):
        try:
            mismatch = float(self.fb.getRamImageSize()) / im.size
        except AttributeError:
            #not opencv, maybe pg.image.tostring that can be set directly
#FIXME: RGB BGR
            if im :
                return self.fb.setRamImage(im)

            return err('invalid frame type %s',im)

        if mismatch==1:
            #ok :)
            self.fb.setRamImage(im)
            return

        if mismatch==4:
            self.fb.setRamImage( cv.cvtColor( im, cv.COLOR_GRAY2RGBA ))
            return

        if mismatch<2: # 1.3333
            self.fb.setRamImage( cv.cvtColor( im, cv.COLOR_RGB2RGBA ))
            return

        print("139:BLIT: %s"%mismatch,self.fb.getRamImageSize(), im.size)


    def set_framebuffer(self,guest):
        if self.fb is None:
            self.fb = guest
            self.crt.set_texture( self.fb )
            return self.fb

        self.fb = guest
        self.crt.set_texture( self.fb, 1 )
        print('113: Collecting: ', p3d.core.TexturePool.garbageCollect(), 'textures from the pool.')

    set_texture = set_framebuffer


ecount = 0

def entity(*compo, **kw):
    global ecount
    ecount+=1
    e = type(sys)(f"{kw['name']}:{ecount}")
    e.name = kw['name']
    for c in compo:
        if c.__class__ is classtype:
            instance = c()
            cname = c.__name__
        else:
            instance = c
            cname = c.__class__.__name__

        instance.parent = e
        setattr( instance, "name", f"{e.name}:{cname}" )
        if hasattr(instance,"setup"):
            instance.setup()
        setattr(e, cname, instance )
    return e


async def test_panda3d_buffer():
    global p3d, pg, screen


    os.environ["SDL_VIDEODRIVER"] = "dummy"

    print('------------- 1 ------------')
    await aio.sleep(1)

    try:
        pg.display.init()
    except Exception as x:
        sys.print_exception(x)

    print('------------- 2 ------------')
    await aio.sleep(1)

    screen = pg.display.set_mode( [320, 200,], pg.FULLSCREEN, 32 )


    print('------------- 3 ------------')
    await aio.sleep(1)

    #screen = pg.display.set_mode( [e.Card.width,e.Card.height,], pg.FULLSCREEN, e.Card.bpp )

    screen.set_colorkey((0, 0, 0))
    screen.set_alpha(0)
    screen.fill( (0,0,0,) )

    LINE_COLOR = (0, 255, 0)
    pg.draw.line(screen, LINE_COLOR, (0,0) , (e.Card.width//2,e.Card.height//2) )

    return

    p3d = await p3d_init()

    e = entity( Node, Card(width=320,height=200,bpp=32), name = "card")

    base.cam.setPos(0, -10, 0)
    base.cam.lookAt(0, 0, 0)

    e.Card.face_me( 0,-4, 0)


    e.Card.blit( pg.image.tostring(screen, 'RGBA') )


    base.run()



async def test_panda3d():
    global p3d

    p3d = await p3d_init()


    def Cube(size=1.0, geom_name="CubeMaker", gvd_name="Data", gvw_name="vertex"):
        from panda3d.core import (
            Vec3,
            GeomVertexFormat,
            GeomVertexData,
            GeomVertexWriter,
            GeomTriangles,
            Geom,
            GeomNode,
            NodePath,
            GeomPoints,
            loadPrcFileData,
        )

        format = GeomVertexFormat.getV3()
        data = GeomVertexData(gvd_name, format, Geom.UHStatic)
        vertices = GeomVertexWriter(data, gvw_name)

        size = float(size) / 2.0
        vertices.addData3f(-size, -size, -size)
        vertices.addData3f(+size, -size, -size)
        vertices.addData3f(-size, +size, -size)
        vertices.addData3f(+size, +size, -size)
        vertices.addData3f(-size, -size, +size)
        vertices.addData3f(+size, -size, +size)
        vertices.addData3f(-size, +size, +size)
        vertices.addData3f(+size, +size, +size)

        triangles = GeomTriangles(Geom.UHStatic)

        def addQuad(v0, v1, v2, v3):
            triangles.addVertices(v0, v1, v2)
            triangles.addVertices(v0, v2, v3)
            triangles.closePrimitive()

        addQuad(4, 5, 7, 6)  # Z+
        addQuad(0, 2, 3, 1)  # Z-
        addQuad(3, 7, 5, 1)  # X+
        addQuad(4, 6, 2, 0)  # X-
        addQuad(2, 6, 7, 3)  # Y+
        addQuad(0, 1, 5, 4)  # Y+

        geom = Geom(data)
        geom.addPrimitive(triangles)

        node = GeomNode(geom_name)
        node.addGeom(geom)

        return NodePath(node)


    class MyApp(p3d.ShowBase):

        # add some colored cubes

        def build(self):
            base.cam.reparent_to(render)
            from random import random

            cube = Cube(size=1.0)

            cubes = render.attachNewNode("cubes")
            cubes.set_pos(0, 0, 0)

            for x in range(5):
                for y in range(5):
                    for z in range(5):
                        instance = cube.copyTo(cubes)
                        instance.setPos(x - 2, y - 2, z - 2)
                        instance.setColor(random(), random(), random(), 1)

            base.cam.set_pos(16, 12, 30)
            base.cam.look_at(0, 0, 0)

            self.cubes = cubes
            return self

        # cube spinner

        async def update(self, dt=0):
            while not aio.loop.is_closed():
                group = self.cubes
                h, p, r = group.get_hpr()
                d = .5
                group.setH(h + d)
                group.setP(p + d)
                group.setY(r + d)
                await aio.asleep(p3d.frame_time)

    self.sb = MyApp().build()
    aio.loop.create_task( self.sb.update() )
    return self.sb.run()


print("Applications.MainActivity loaded")

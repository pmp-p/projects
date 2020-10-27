import os
import embed
import time as Time

try:
    from . import ControlChannel as cc
except Exception as e:
    #sys.print_exception(e)
    embed.log(str(e))


if os.path.exists('/data/data/board'):
    #home sweet home (h3droid boards)
    ccip = "192.168.0.254"
else:
    ccip = "82.65.46.75"


cc.instance = cc.client(ccip, 6667, nick="apk_" + hex(int(str(Time.time()).replace(".", "")))[2:], channels=["#android"])

aio.service(cc.instance)

_ = None

class MainActivity:
    pass


from android import *


async def test_ui():

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


async def __main__():
    global self, cc

    self = sys.modules['Applications.MainActivity']
    cc.self =  self

    await test_ui()


async def try_me():

    import builtins
    #builtins.pdb = cc.out

    import panda3d

    p3d = await panda3d.new(150, 100, 150, 100)

    pdb("Started panda3d on", panda3d.view)

    await aio.sleep(.5)

    p3d.loadPrcFileData("", "load-display pandagles2")
    p3d.loadPrcFileData("", "win-origin -2 -2")
    p3d.loadPrcFileData("", "win-size 848 480")
    p3d.loadPrcFileData("", "support-threads #f")
    p3d.loadPrcFileData("", "textures-power-2 down")
    p3d.loadPrcFileData("", "textures-square down")
    p3d.loadPrcFileData("", "show-frame-rate-meter #t")


    await aio.sleep(.5)





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
        instance = None
        frame_time = 1.0 / 60

        async def async_loop(self):
            self.build()
            aio.loop.create_task( self.update() )
            while not aio.loop.is_closed():
                try:
                    p3d.task_mgr.step()
                    #embed.step()
                    #await aio.asleep(self.frame_time)
                except SystemExit:
                    print('87: Panda3D stopped',file= __import__('sys').stderr)
                    break
                await aio.asleep(self.frame_time)

        def async_run(self):
            self.__class__.instance = self
            run(self.async_loop)

        # patch the sync run which would prevent to enter interactive mode
        run = async_run

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

        # cube spinner

        async def update(self, dt=0):
            while not aio.loop.is_closed():
                group = self.cubes
                h, p, r = group.get_hpr()
                d = .5
                group.setH(h + d)
                group.setP(p + d)
                group.setY(r + d)
                await aio.asleep(self.frame_time)


    MyApp.instance = MyApp()

    aio.loop.create_task( MyApp.instance.async_loop() )
    self.sb = MyApp.instance

    p3d.init_dev()

    return 1

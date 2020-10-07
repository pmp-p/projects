print('Hello Panda3D')

view = None


import builtins
#builtins.pdb = cc.out
pdb("Starting panda3d on", view)

import panda3d

import panda3d.core as p3d

p3d.loadPrcFileData("", "load-display pandagles2")
p3d.loadPrcFileData("", "win-origin -2 -2")
p3d.loadPrcFileData("", "win-size 848 480")
p3d.loadPrcFileData("", "support-threads #f")
p3d.loadPrcFileData("", "textures-power-2 down")
p3d.loadPrcFileData("", "textures-square down")
p3d.loadPrcFileData("", "show-frame-rate-meter #t")

import direct
import direct.task
import direct.task.TaskManagerGlobal

import direct.showbase
from direct.showbase.ShowBase import ShowBase as ShowBase



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


class MyApp(ShowBase):
    instance = None
    frame_time = 1.0 / 60

    async def async_loop(self):
        self.build()
        #aio.loop.create_task( self.update() )
        while not aio.loop.is_closed():
            try:
                self.spin()
                direct.task.TaskManagerGlobal.taskMgr.step()
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
    def spin(self):
        group = self.cubes
        h, p, r = group.get_hpr()
        d = .5
        group.setH(h + d)
        group.setP(p + d)
        group.setY(r + d)


    async def update(self, dt=0):
        while not aio.loop.is_closed():
            self.spin()
            await aio.asleep(self.frame_time)


MyApp.instance = MyApp()

aio.loop.create_task( MyApp.instance.async_loop() )



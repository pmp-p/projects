# https://developer.android.com/guide/components/activities/activity-lifecycle


import os
import sys


def onCreate(self, pyvm):
    print("Applications.onCreate(Begin)", pyvm)
    aio.loop.create_task(MainActivity.main(*sys.argv,**os.environ))
    print("Applications.onCreate(End)", pyvm)

def onStart(self, pyvm):
    print("Applications.onStart", pyvm)


def onPause(self, pyvm):
    print("Applications.onPause", pyvm)


def onResume(self, pyvm):
    print("Applications.onResume", pyvm)


def onStop(self, pyvm):
    print("Applications.onStop", pyvm)


def onDestroy(self, pyvm):
    print("Applications.onDestroy", pyvm)

print('Applications.MainActivity loading')

from . import MainActivity

print('Applications ready')



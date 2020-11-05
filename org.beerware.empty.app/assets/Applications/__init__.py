# https://developer.android.com/guide/components/activities/activity-lifecycle


def onCreate(self, pyvm):
    print("Applications.onCreate", pyvm)
    from . import MainActivity


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

print('Applications ready')



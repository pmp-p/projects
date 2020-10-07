#from . import widget

from pythons.aio import plink

#androidx = plink.androidx

android = plink.android
this = plink.this
layout = plink.layout
widgets = plink.android.widgets


# Button, Checkbutton, Entry, Frame, Label, LabelFrame
# Menubutton, PanedWindow, Radiobutton, Scale, Scrollbar, and Spinbox.
# The other six are new: Combobox, Notebook, Progressbar, Separator, Sizegrip and Treeview.



# LayoutParams.WRAP_CONTENT == -2
async def setPos(view, left, top, right, bottom):
    global android, layout


    async with android.widget.RelativeLayout__LayoutParams.newInstance(-2,-2) as params:
        params.setMargins( left, top, right, bottom)
    await layout.addView(view, params)

def set_text(wdg, data):
    getattr(wdg,"setText")(data)
    getattr(wdg,"setWidth")(len(data)*Widgets.cell)


# tag using the hex java pointer memory address string converted to int
def tag(wdg,target=None,handler=None, hint=""):
    global tags
    tag_id = int( str(wdg).rsplit(':',1)[-1], 16 )
    wdg.setId( tag_id )
    Events.ld[tag_id] = [wdg, target or wdg, handler, hint or str(tag_id)]



class Widgets:
    cell = 11

class Events:
    ld = {}
    ev = {}

    #EventListener.handleEvent()
    async def handleEvent(self, e):
        print("51:handleEvent",e)


class Button(Events,Widgets):
    pass

class ButtonRow(Button):
    y = 2 * Widgets.cell
    spacing = 1 * Widgets.cell
    x = spacing
    width = 0

    def __init__(self):
        cls = ButtonRow
        cls.width = cls.cell * len(self.text)

    @staticmethod
    def left():
        return ButtonRow.x

    @staticmethod
    def right(decal=0):
        cls = ButtonRow
        try:
            cls.x += cls.width + cls.spacing
            return cls.x
        finally:
            if decal:
                cls.x += (4+decal)*cls.cell + cls.spacing
            cls.width = 0



def add(ct):
    return getattr( android.widget, ct ).newInstance(this)


async def uinput(cls):
    global widgets

    async with add('Button') as button, add('EditText') as text:
        set_text(text, cls.text)
        button.setText(f"↲")

        button.setOnClickListener(this)

        i=0
        tag(button, text, cls().onclick, f"{i}")

        await setPos(text,  cls.left(), cls.y, 0, 0)
        await setPos(button, cls.right(2), cls.y, 0, 0)

# https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
def addEventListener(target, etype, listener, **kw):
    listeners = Events.ev.setdefault(etype.lower(), {} )
    tid = int( str(target).rsplit(':',1)[-1] , 16 )

    clients = listeners.setdefault(tid, [] )

    if hasattr( listener , "handleEvent"):
        if not listener.handleEvent in clients:
            clients.append( listener.handleEvent )
    else:
        clients.append( listener )


__ALL__ = ['widgets', 'this', 'uinput', 'ButtonRow', 'setPos', 'Events']


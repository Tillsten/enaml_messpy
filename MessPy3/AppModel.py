from os import path
import atom.api as a
import enamlx
import numpy as np
import pyqtgraph as pg
from enaml import imports
from enaml.application import deferred_call, timed_call
from enaml.qt.qt_application import QtApplication
import pathlib, os
os.environ['CONF_DIR'] = str(pathlib.Path('config/').absolute())

enamlx.install()
pg.setConfigOption('useOpenGL', False)

from Instruments.interfaces import Device, TuneableCam, DelayLine
from Instruments.mocks import (Cam, DelayLine, MockCam, MockDelayLine,
                               TuneableMockCam)

class HardwareManager(a.Atom):
    instruments = a.List(Device)


    def register(self, kind):
        pass

class AppState(a.Atom):
    cams = a.List(Cam)
    hardware = a.Typed(HardwareManager, args=())
    current_plan = a.Value()
    delay_line = a.Typed(DelayLine)
    available_plans = a.List()
    state = a.Enum('plan', 'paused', 'noplan')

    def start_plan(self, Plan):
        pass


if __name__ == '__main__':

    import qt_material

    #from qt_material import apply_stylesheet
    app = QtApplication()
    #apply_stylesheet(app._qapp, theme='light_blue.xml')
    #import qdarkstyle
    #app._qapp.setStyleSheet(qdarkstyle.load_stylesheet())
    with imports():
        from AppView import MessPy3

    cam = TuneableMockCam()
    cam.read_cam()
    hw = HardwareManager()
    hw.register(cam)
    delay_line=MockDelayLine()
    hw.register(delay_line)

    state = AppState(cams=[cam], delay_line=delay_line)
    mw = MessPy3(app=state)
    mw.show()
    app.start()




import atom.api as a
from atom.atom import observe
import enamlx
import numpy as np
import pyqtgraph as pg
from enaml import imports
from enaml.application import deferred_call, timed_call
from enaml.qt.qt_application import QtApplication
import pathlib, os

os.environ['CONF_DIR'] = str(pathlib.Path(__file__).parent/'config')
enamlx.install()
pg.setConfigOption('useOpenGL', False)

from Instruments.interfaces import Device, TuneableCam, DelayLine
from Instruments.mocks import (Cam, DelayLine, MockCam, MockDelayLine,
                               TuneableMockCam)
from Plans.common import Plan
from Plans.ScanSpectrum import ScanSpectrum, ScanSpectrumSettings


class AppState(a.Atom):
    cams = a.List(Cam)
    #hardware = a.Typed(HardwareManager, args=())
    current_plan = a.Typed(Plan)
    delay_line = a.Typed(DelayLine)
    available_plans = a.List()
    state = a.Enum('no_plan','running', 'paused', 'finished', 'stopping')
    is_not_stopping = False

    def stop_plan(self, change=None):
        self.state = 'stopping'
        self.current_plan.stop_next = True
        self.current_plan.stopped = True
        self.current_plan = None
        self.state = 'no_plan'

    @observe('state')
    def handle_pause(self, change):
        if self.state == 'paused':
            self.current_plan.paused = True

    def start_plan(self, plan: Plan):
        if self.current_plan is not None:
            self.current_plan.stop_next = True
            self.current_plan.step()
        self.current_plan = plan
        #plan.observe('stopped', self.stop_plan)
        self.state = 'running'
        plan.plan_finnished.bind(lambda x: setattr(self, 'state', 'finished'))

    def loop(self):
        if self.state in ['running', 'stopping']:
            try:
                self.current_plan.step()
            except StopIteration:
                self.state = 'finished'
        elif self.state in ['paused', 'no_plan']:
            for c in self.cams:
                if not c.reading:
                    c.start_read()



if __name__ == '__main__':

    import qt_material

    #from qt_material import apply_stylesheet
    app = QtApplication()
    #apply_stylesheet(app._qapp, theme='light_blue.xml')
    import qdarkstyle
    app._qapp.setStyleSheet(qdarkstyle.load_stylesheet())
    with imports():
        from AppView import MessPy3

    cam = TuneableMockCam()
    cam.read_cam()
    #hw = HardwareManager()
    #hw.register(cam)
    delay_line=MockDelayLine()
    #hw.register(delay_line)

    state = AppState(cams=[cam], delay_line=delay_line)
    mw = MessPy3(app=state)
    mw.show()
    app.start()




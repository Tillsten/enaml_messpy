from atom.api import set_default, Float, Bool, Typed
from .interfaces import Cam, CamRead, DelayLine, TuneableCam, RotationStage, Device
import numpy as np
import time
from enaml.application import deferred_call, timed_call

class MockCam(Cam):
    name = set_default('MockCam')
    pixel = set_default(400)
    lines = set_default(['probe', 'ref'])
    std_lines = set_default(['probe', 'ref'])
    sig_lines = set_default(['probe'])
    freqs = set_default(np.arange(400))
    reading = set_default(False)

    def start_read(self):
        import threading
        self.reading = True
        t = threading.Thread(target=self.read_cam)
        t.start()

    def read_cam(self) -> CamRead:
        #print('read')
        x = np.arange(128)
        data = np.random.randn(2, x.size, self.num_shots)
        y = 1/(1+((x-200)/50)**2)
        data += y[None, :, None]
        lines = data.mean(-1)
        std = data.std(-1)
        signal = lines[:1, :]
        time.sleep(self.num_shots*1e-3)
        #self.num_reads += 1
        deferred_call(setattr, self, 'reading', False)
        last_read = CamRead(lines=lines,
                reading=self.num_reads, std=std, sig=signal)
        deferred_call(setattr, self, 'last_read', last_read)
        return last_read

class TuneableMockCam(TuneableCam):
    name = set_default('TuneableMockCam')
    pixel = set_default(400)
    lines = set_default(['probe', 'ref'])
    std_lines = set_default(['probe', 'ref'])
    sig_lines = set_default(['probe'])
    freqs = set_default(np.arange(400))
    reading = set_default(False)
    current_wl = set_default(500)
    _wl = Float(300)

    def start_read(self):
        import threading
        self.reading = True
        t = threading.Thread(target=self.read_cam)
        t.start()

    def read_cam(self) -> CamRead:
        #print('read')
        x = np.arange(400)
        data = np.random.randn(2, x.size, self.num_shots)
        y = 1/(1+((x-200)/50)**2)
        data += y[None, :, None]
        lines = data.mean(-1)
        std = data.std(-1)
        signal = lines[:1, :]
        time.sleep(self.num_shots*1e-3)
        #self.num_reads += 1
        deferred_call(setattr, self, 'reading', False)
        last_read = CamRead(lines=lines,
                reading=self.num_reads, std=std, sig=signal)
        deferred_call(setattr, self, 'last_read', last_read)
        return last_read

    def set_wavelength(self, pos):
        self.state = 'moving'
        def cb():
            self.current_wl = pos
            self.state = 'idle'
        timed_call(1000, cb)



ps_per_second = 2

class MockDelayLine(DelayLine):
    name = set_default('MockDelayLine')
    fs_pos = Float(0)
    target_pos = Float()
    cur_pos = Float()
    last_call_time = Float()
    moving = Bool()
    state = set_default('idle')

    def set_pos_fs(self, pos: float):
        self.target_pos = pos
        self.moving = True
        self.state = 'busy'
        self.last_call_time = time.time()

    def get_pos_fs(self) -> float:
        if self.moving:
            dt = time.time()-self.last_call_time
            ds = self.target_pos - self.cur_pos
            new_pos = dt*ps_per_second*1000.
            if abs(new_pos / ds) > 1:
                self.moving = False
                self.state = 'idle'
                self.cur_pos = self.target_pos
                return self.target_pos
            else:
                return dt*ps_per_second*1000.*np.sign(ds)+self.cur_pos
        else:
            return self.cur_pos

    def is_moving(self):
        return self.moving

    def get_pos(self) -> float:
        return self.position


class PulsShaper(Device):
    grating_1 = Typed(RotationStage, kwargs=dict(name='grating_1'))
    grating_2 = Typed(RotationStage, kwargs=dict(name='grating_2'))
    


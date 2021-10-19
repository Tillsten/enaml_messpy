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


    def read_cam(self) -> None:
        #print('read')
        x = np.arange(128)
        data = np.random.randn(self.num_shots, x.size, 2)
        y = 1/(1+((x-200)/50)**2)
        data += y[None, :, None]
        lines = data.mean(0)
        std = data.std(0)
        signal = lines[:, :1]
        time.sleep(self.num_shots*1e-3)
        #self.num_reads += 1
        last_read = CamRead(lines=lines,
                reading=self.num_reads, std=std, sig=signal)
        deferred_call(setattr, self, 'last_read', last_read)
        deferred_call(setattr, self, 'reading', False)
        return last_read

class TuneableMockCam(TuneableCam):
    name = set_default('TuneableMockCam')
    pixel = set_default(400)
    lines = set_default(['probe', 'ref'])
    std_lines = set_default(['probe', 'ref'])
    sig_lines = set_default(['probe'])

    reading = set_default(False)
    current_wl = set_default(500)
    freqs = set_default((np.arange(400)-200)+500)
    _wl = Float(500)

    def start_read(self):
        import threading
        self.reading = True
        t = threading.Thread(target=self.read_cam)
        t.start()

    def read_cam(self) -> CamRead:
        x = self.freqs
        data = np.random.randn(self.num_shots, x.size, 2)
        y = 1/(1+((x-300)/50)**2)
        data += y[None, :, None]
        lines = data.mean(0)
        std = data.std(0)
        signal = lines[:, :1]
        time.sleep(self.num_shots*1e-3)
        deferred_call(setattr, self, 'reading', False)
        last_read = CamRead(lines=lines,
                reading=self.num_reads, std=std, sig=signal)
        deferred_call(setattr, self, 'last_read', last_read)
        return last_read

    def set_wavelength(self, pos):
        self.state = 'moving'
        def cb():
            self.current_wl = pos
            self.freqs = (np.arange(400)-200) + self.current_wl
            self.state = 'idle'
        timed_call(100, cb)



ps_per_second = 2

class MockDelayLine(DelayLine):
    name : str = set_default('MockDelayLine')
    fs_pos = Float(0)
    _target_pos = Float()
    _cur_pos = Float()
    _last_call_time = Float()
    moving = Bool()
    state : str = set_default('idle')

    def set_pos_fs(self, pos: float):
        self._target_pos = pos
        self.state = 'moving'
        self._last_call_time = time.time()

    def get_pos_fs(self) -> float:
        if self.state == 'moving':
            dt = time.time()-self._last_call_time
            ds = self._target_pos - self._cur_pos
            new_pos = dt*ps_per_second*1000.
            if abs(new_pos / ds) > 1:
                self.state = 'idle'
                self._cur_pos = self._target_pos
                return self._target_pos
            else:
                return dt*ps_per_second*1000.*np.sign(ds)+self._cur_pos
        else:
            return self._cur_pos

    def is_moving(self):
        return self.state == 'moving'

    def get_pos(self) -> float:
        return self.get_pos_fs()*1e-15*3e8/1000/2


class PulsShaper(Device):
    grating_1 = Typed(RotationStage, kwargs=dict(name='grating_1'))
    grating_2 = Typed(RotationStage, kwargs=dict(name='grating_2'))



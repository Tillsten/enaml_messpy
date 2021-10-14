
from atom.api import *
import numpy as np
from scipy.ndimage import uniform_filter
win_fcn = np.hanning

class View(Atom):
    data = Value()
    data_fft = Value()
    taus = Value()

    def _default_data_fft(self):
        win = win_fcn(2 * len(self.taus))
        d = self.data.copy()
        d[0, :] *= 0.5
        return np.fft.rfft(d*win[len(self.taus):, None], n=self.data.shape[0]*2, axis=0)

    @classmethod
    def from_file(cls, path):
        data = np.loadtxt(path)[:-1, :]
        taus = data[:, 0]
        data= uniform_filter(data[:, 1:], (1, 2))

        return cls(data=data, taus=taus)

class DemoModel(Atom):
    path = Str(r'D:\boxup\AG Mueller-Werkmeister\2DIR\Yannik\20211004#91\20211004#92_T09_PAR#001.scan')
    data = Typed(View)

    def _default_data(self):
        return View.from_file(self.path)






from atom.api import *
from Plans.common import SampleInfo
from Plans.common import Plan, Meta
import numpy as np

class ScanSpectrumSettings(Meta):
    sample_info = Typed(SampleInfo)
    wl_min = Float(5000)
    wl_max = Float(1000)
    step = Float(10)
    shots = Int(30)
    linear_in = Enum('wl', 'wn')



class ScanSpectrum(Atom):
    settings : ScanSpectrumSettings = Typed(ScanSpectrumSettings, strict=True)
    points = List(Float)

    def _default_points(self):
        s = self.settings
        if s.linear_in == 'wl':
            return np.arange(s.wl_min, s.wl_max+1e-6, s.step)
        if s.linear_in == 'wn':
            return np.arange(1e7/s.wl_max+1e-6, 1e7/s.wl_min, s.step)




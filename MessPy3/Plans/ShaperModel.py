from atom.api import Enum, Value, Float, Int, Atom, Typed
import numpy as np

samples = 4096 * 3
AOM_acoustic_speed = 5500


class FreqCalibration(Atom):
    a = Float(0)
    b = Float(0)
    c = Float(0)


class AOM(Atom):
    xunit = Enum('S', 'x/cm', 'wl/nm', 't/mus')
    x = Value()
    t_arr = Value()
    x_pos_arr = Value()
    wl_arr = Value()
    rf = Value()
    samp_freq = Float(1200)
    freq = Float(75)
    amp = Value()
    phase = Value()
    default_mask = Value()
    calib = Typed(FreqCalibration)

    def _default_t_arr(self):
        dt = 1 / self.samp_freq
        return np.arange(samples) * dt

    def _default_amp(self):
        return np.ones(samples)

    def _default_phase(self):
        return np.zeros(samples)

    def _default_rf(self):
        return np.sin(self.t_arr * self.freq * 2 * np.pi)

    def _default_x_pos_arr(self):
        return self.t_arr / 1e6 * AOM_acoustic_speed * 100

    def _default_x(self):
        return np.arange(samples)

    def _default_default_mask(self):
        return np.sin(self.t_arr * self.freq * 2 * np.pi)

    def _default_wl_arr(self):
        x = self.x
        return self.calib.a*x**2+self.calib.b*x+self.calib.c*x

    def _observe_xunit(self, change):
        if self.xunit == 'S':
            self.x = np.arange(samples)
        elif self.xunit == 'x/cm':
            self.x = self.x_pos_arr
        elif self.xunit == 'wl/nm':
            self.x = np.arange(samples)
        elif self.xunit == 't/mus':
            self.x = self.t_arr

    def _observe_freq(self, change):
        self.rf = np.sin(self.t_arr * self.freq * 2 * np.pi)

    def amp_modulation(self, seperation=64, width=32):
        self.amp *= 0
        for i in np.arange(0, samples, seperation + width):
            self.amp[i:i + width] = 1
        self.rf = np.sin(self.t_arr * self.freq * 2 * np.pi) * self.amp

    def single_amp(self, position, width):
        pass


if __name__ == '__main__':
    from enaml import imports, qt
    from enaml.qt.qt_application import QtApplication
    import enamlx
    enamlx.install()
    app = QtApplication()
    with imports():
        from ShaperView import ShaperWindow

    model = AOM()
    sv = ShaperWindow(model=model)
    sv.show()
    app.start()

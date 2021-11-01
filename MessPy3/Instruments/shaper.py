import numpy as np
from atom.api import *
from .interfaces import Device
from utils import nm2THz, cm2THz
from scipy.constants import c


def double_pulse_mask(nu: np.ndarray, nu_rf: float, tau: float, phi1: float,
                      phi2: float):
    """
    Return the mask to generate a double pulse

    Parameters
    ----------
    nu : array
        freqs of the shaper pixels in THz
    nu_rf : float
        rotating frame freq of the scanned pulse in THz
    tau : float
        Interpulse distance in ps
    phi1 : float
        Phase shift of the scanned pulse
    phi2 : float
        Phase shift of the fixed pulse
    """
    double = 0.5 * (np.exp(-1j * (nu - nu_rf) * 2 * np.pi * tau) *
                    np.exp(+1j * phi1) + np.exp(1j * phi2))
    return double


class DoublePulseParams(Atom):
    delay = Float(4000)
    step = Float(50)
    rot_frame = Float(1500)
    phase_cycling = Enum(2, 4)

    def masks(self, nu):
        nu_rf = cm2THz(self.rot_frame)
        return double_pulse_mask()


class DispersionSettings(Device):
    cwl = Float(15000).tag(cfg=True)
    gvd = Float(-100_000).tag(cfg=True)
    tod = Float(3).tag(cfg=True)
    fod = Float(0).tag(cfg=True)  

    def dispersion(self, nu):
        """Calulates the dispersion for given frequencies"""
        x = nu - nm2THz(self.cwl)
        x *= (2 * np.pi)
        facs = np.array([self.gvd, self.tod, self.fod]) / np.array([2, 6, 24])
        return x**2 * facs[0] + x**3 * facs[1] + x**3  * facs[2]


class ShaperModel(Atom):
    power = Float(1)
    amplitude = Float(1).tag(cfg=True)
    running = Bool(True).tag(cfg=True)
    chopped = Bool(True).tag(cfg=True)
    dispersion_correct= Bool().tag(cfg=True)
    phase_cycle = Bool().tag(cfg=True)
    calibration = Tuple(float).tag(cfg=True)
    bragg_correction = Bool().tag(cfg=True)
    
    disp_settings = Typed(DispersionSettings,()).tag(cfg=True)

    def _observe_power(self, change):
        self.amplitude = self.power ** 0.5

    def _observe_amplitude(self, change):        
        self.power = self.amplitude ** 2

    @observe('amplitude', 'running', 'chopped', 'dispersion_correct',
             'phase_cycle', 'bragg_correction', 'calibration')
    def update_mask(self):
        pass



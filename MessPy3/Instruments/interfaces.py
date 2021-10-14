from atom.api import Bool, Float, Int, Typed, Str, List, Dict, Value, Atom, Enum, Event, Tuple, Range
from atom.atom import set_default
import numpy as np
from pathlib import Path
import pickle
import asyncio
import json
import atexit
from typing import ClassVar

def get_dir():
    import os
    return Path(os.environ['CONF_DIR'])


class Device(Atom):
    name = Str(strict=True)
    state = Enum('init', 'idle', 'busy', 'error', 'custom', 'moving')
    config = Dict()

    available_devices : 'list[Device]' = []

    def _config_default(self):
        conf_file = (get_dir() / self.name).with_suffix('.cfg')
        if conf_file.exists():
            json.load(conf_file.open('r'))
        else:
            return {}

    def __init__(self) -> None:
        super().__init__()
        for name, member in self.members().items():
            #print(name, member)
            if member.metadata and 'cfg' in member.metadata:
                if name in self.config:
                    setattr(self, name, self.config[name])
        atexit.register(self.on_exit)
        Device.available_devices.append(self)

    def on_exit(self):
        for name, member in self.members().items():
            if member.metadata and 'cfg' in member.metadata:
                self.config[name] = getattr(self, name)
        conf_file = (get_dir() / self.name).with_suffix('.cfg')
        with conf_file.open('w') as f:
            json.dump(self.config, f)



class CamRead(Atom):
    lines = Typed(np.ndarray)
    std = Typed(np.ndarray)
    sig = Typed(np.ndarray)
    sucess = Bool()
    reading = Int()


class Cam(Device):
    pixel = Int()
    lines = List(str)
    std_lines = List(str)
    sig_lines = List(str)
    num_shots = Int(40).tag(cfg=True)
    num_reads = Int(0)
    last_read = Typed(CamRead)
    freqs = Typed(np.ndarray)
    background = Value()
    reading = Bool()
    read_finished = Event()


    def __init__(self) -> None:
        super().__init__()


    async def async_read_cam(self) -> CamRead:
        pass

    def read_cam(self) -> CamRead:
        raise NotImplementedError

    def record_bg(self):
        raise NotImplementedError

    def delete_bg(self):
        raise NotImplementedError


class TuneableCam(Cam):
    current_wl: float = Float()
    moving: bool = Bool(False)
    has_turret: bool = Bool(False)

    def set_wavelength(self):
        raise NotImplementedError

    async def async_set_wavelength(self):
        raise NotImplemented

    def set_grating(self, i: Int):
        NotImplemented

    def get_grating(self) -> int:
        raise NotImplementedError

class MotorAxis(Device):
    position = Float()
    home_pos = Float().tag(cfg=True)
    unit = Str('mm')
    min_pos = Float(None, strict=False)
    max_pos = Float(None, strict=False)

    def set_pos(self, pos: float):
        pass

    def get_pos(self) -> float:
        pass

    def is_moving(self) -> bool:
        pass

    def set_home(self):
        self.home_pos = self.get_pos()


class RotationStage(MotorAxis):
    pos_dict = Dict(str, float).tag(cfg=True)
    unit = set_default(Str('deg'))
    min_pos = set_default(-360)
    max_pos = set_default(360)


class DelayLine(MotorAxis):
    direction = Enum(-1, 1)

    def set_pos_fs(self, fs: Float):
        pass

    def get_pos_fs(self) -> Float:
        pass


class Scanner(Device):
    x = Typed(MotorAxis)
    y = Typed(MotorAxis)


class Shutter(Device):
    is_open = Bool()

    def toggle(self):
        pass

    def open(self):
        if self.is_open:
            pass
        else:
            self.toggle()

    def close(self):
        if not self.is_open:
            pass
        else:
            self.toggle()



def dispersion(nu, nu0, GVD, TOD, FOD):
    """Calulates the dispersion for given frequencies"""
    x = nu - nu0
    x *= (2 * np.pi)
    facs = np.array([GVD, TOD, FOD]) / np.array([2, 6, 24])
    return x**2 * facs[0] + x**3 * TOD * facs[1] + x**3 * FOD * facs[2]

from scipy.constants import c

class DispParams(Atom):
    center_wl = Float(5000)
    gvd = Float(0)
    tod = Float(0)
    fod = Float(0)

    def phase(self, nu):
        nu0 = c / self.center_wl * 1000
        return dispersion(nu, nu0, self.gvd, self.tod, self.fod)

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
        nu_rf = rot_frame
        return double_pulse_mask()


class Shaper(Device):
    pixel = Int(4096*3)
    calibration = Tuple(Float).tag(cfg=True)
    amplitude = Range(0, 1, 0.2).tag(cfg=True)
    power = Range(0).tag(cfg=True)
    running = Bool(False).tag(cfg=True)
    chopping = Bool(False).tag(cfg=True)
    phase_cycling = Bool(False).tag(cfg=True)
    disp_correction = Bool(False).tag(cfg=True)
    disp_params = Typed(DispParams)

    @property
    def nu(self):
        return np.polyval(self.calibration, np.arange(self.pixel))







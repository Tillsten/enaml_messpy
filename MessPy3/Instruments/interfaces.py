from atom.api import Bool, Float, Int, Typed, Str, List, Dict, Value, Atom, Enum, Event, Tuple, Range
from atom.atom import set_default
import numpy as np
from pathlib import Path
import pickle
import asyncio
import json
import atexit
from typing import ClassVar, Protocol
import threading


def get_dir():
    import os
    return Path(os.environ['CONF_DIR'])


class Device(Atom):
    """
    Base clss for devices.

    Has two roles: It offers automatic saving of members with a tag `cfg=True`
    into a config file. It will also register the `on_exit` to be run at exit.
    By default, it just calls the config saving method. It also    

    """
    name = Str(strict=True)
    state = Enum('init', 'idle', 'busy', 'error', 'custom', 'moving')
    config = Dict()

    available_devices: 'list[Device]' = []

    def _config_default(self):
        conf_file = (get_dir() / self.name).with_suffix('.cfg')
        if conf_file.exists():
            json.load(conf_file.open('r'))
        else:
            return {}

    def __init__(self) -> None:
        super().__init__()
        self.load_config()
        atexit.register(self.on_exit)
        Device.available_devices.append(self)

    def load_config(self):
        for name, member in self.members().items():
            #print(name, member)
            if member.metadata and 'cfg' in member.metadata:
                if name in self.config:
                    setattr(self, name, self.config[name])

    def on_exit(self):
        self.save_config()

    def save_config(self):
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

    def start_read(self):
        self.reading = True
        t = threading.Thread(target=self.read_cam)
        t.start()

    async def async_read_cam(self) -> CamRead:
        pass

    def read_cam(self) -> None:
        raise NotImplementedError

    def record_bg(self):
        raise NotImplementedError

    def delete_bg(self):
        raise NotImplementedError


class TuneableCam(Cam):
    current_wl: float = Float()
    moving: bool = Bool(False)

    grating_list = List(str)
    grating_index: int = Int(0)

    def _default_grating_index(self):
        return self.grating_index

    def set_wavelength(self):
        raise NotImplementedError

    async def async_set_wavelength(self):
        raise NotImplemented

    def set_grating(self, i: Int):
        NotImplemented

    def get_grating(self) -> int:
        return 0

    def _observe_grating_index(self, change):
        self.set_grating(self.grating_index)


class MotorAxis(Device):
    position = Float()
    home_pos = Float().tag(cfg=True)
    last_target = Float().tag(cfg=True)
    unit = Str('mm')
    min_pos = Float(None, strict=False)
    max_pos = Float(None, strict=False)

    def set_pos(self, pos: float):
        pass

    def get_pos(self) -> float:
        pass

    def move_relative(self, val):
        cur_pos = self.get_pos()
        self.set_pos(cur_pos + val)

    def is_moving(self) -> bool:
        pass

    def set_home(self):
        self.home_pos = self.get_pos()


class RotationStage(MotorAxis):
    pos_dict = Dict(str, float).tag(cfg=True)
    unit = set_default(Str('deg'))
    min_pos = set_default(-360)
    max_pos = set_default(360)


class DualRotationStage(Device):
    rot_stage_0 = Typed(RotationStage)
    rot_stage_1 = Typed(RotationStage)


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
        raise NotImplementedError

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

from atom.api import *
from Plans.common import SampleInfo
from Plans.common import Plan, Meta
import numpy as np
from Instruments.interfaces import TuneableCam
from collections import defaultdict

class ScanSpectrumSettings(Meta):
    sample_info = Typed(SampleInfo)
    wl_min = Float(200)
    wl_max = Float(500)
    step = Float(1)
    shots = Int(200)
    linear_in = Enum('wl', 'wn')


class ScanSpectrum(Plan):
    settings: ScanSpectrumSettings = Typed(ScanSpectrumSettings)
    points = Typed(np.ndarray)
    tuneable_cam: TuneableCam = Typed(TuneableCam)
    specs = Typed(np.ndarray)
    cwl_data = Dict()
    reads = List()
    step = Value()
    initial_values = Dict()
    new_point = Event()

    @observe("stopped")
    def on_stopped(self):
        self.tuneable_cam.set_wavelength(self.initial_values['wl'])
        self.tuneable_cam.num_shots = self.initial_values['shots']

    def _default_cwl_data(self):
        return {i: list() for i in self.tuneable_cam.lines}

    def _default_step(self):
        return self.steps().__next__

    def _default_initial_wl(self):
        return dict(
            wl=self.tuneable_cam.current_wl,
            shots=self.tuneable_cam.num_shots
        )

    def _default_points(self):
        s = self.settings
        if s.linear_in == 'wl':
            return np.arange(s.wl_min, s.wl_max + 1e-6, s.step)
        if s.linear_in == 'wn':
            return np.arange(1e7 / s.wl_max + 1e-6, 1e7 / s.wl_min, s.step)

    def steps(self):
        print('step')
        cam = self.tuneable_cam
        for p in self.points:
            print('step2')
            self.tuneable_cam.set_wavelength(p)
            while self.tuneable_cam.state == 'moving':
                yield
            self.tuneable_cam.start_read()
            while self.tuneable_cam.reading:
                yield
            reading = self.tuneable_cam.last_read
            self.reads.append(reading.lines)
            for i, line in enumerate(cam.lines):
                cwl = cam.pixel // 2
                self.cwl_data[line].append(reading.lines[cwl, i])
            self.new_point(1)
            yield
        self.plan_finnished = True
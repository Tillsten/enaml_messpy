#from AppModel import HardwareManager
import atom.api as a
from atom.scalars import Str

from enaml import imports, qt
from enaml.core.api import d_
import time

class Meta(a.Atom):
    creation_time = a.Float(factory=time.time)
    operator = a.Str('')
    name = a.Str(strict=True)
    annotations = a.Str()
    filename = a.Str()

class SampleInfo(a.Atom):
    sample_name = a.Str('')
    solvent_name = a.Str('')
    thickness = a.Str('')
    annotations = a.Str('')

class FocusInfo(a.Atom):
    "All units are given in μm"
    pump_x = a.Int(0)
    pump_y = a.Int(0)
    probe_x = a.Int(0)
    probe_y = a.Int(0)
    ref_x = a.Int(0)
    ref_y = a.Int(0)

class SetupInfo(a.Atom):
    excitation_wavelength = a.Str("")
    excitation_energy_mw = a.Str('')
    focus = a.Typed(FocusInfo, factory=FocusInfo)
    shots = a.Int(1000)

class Plan(Meta):
    required_instruments = a.List(type)
    optional_instruments = a.List(type)

    stop_next = a.Bool(False)

    setup_finnished = a.Event()
    plan_finnished = a.Event()
    stopped = a.Event()
    paused = a.Event()

    #def check_instruments(self, hw: HardwareManager):
    #    for i in self.required_instruments:
    #        if i not in hw.instruments:
    #            raise ValueError('Plan requieres %s'%i)



class LastUsed(a.Atom):
    settings_list = a.List(a.Subclass(Meta))


def to_nested_dict(obj: a.Atom):
    d = obj.members()
    out = {}
    for k,v in d.items():
        attr = getattr(obj, k)
        if isinstance(attr, a.Atom):
            attr = to_nested_dict(attr)
        out[k] = attr# convertors[type(v)](getattr(a, k))
    return out
from typing import ForwardRef
import numpy as np
import atom.api as a

from enaml import imports, qt
from enaml.core.api import d_
import time

class Meta(a.Atom):
    creation_time = a.Float(factory=time.time)
    operator = a.Str('')

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

class ScanSpectrumSettings(a.Atom):
    wl_min = a.Float(400)
    wl_max = a.Float(2000)
    steps = a.Int(100)
    shots = a.Int(50)
    linear_in = a.Enum('wl', 'wn')
    path = a.Str('')

class PumpProbeCamSettings(a.Atom):
    center_wls = a.List(a.Float)
    cam = a.ForwardTyped('Cam')

class PumpProbeSettings(Meta):
    setup_info = a.Typed(SetupInfo, factory=SetupInfo)
    sample_info = a.Typed(SampleInfo, factory=SampleInfo)
    delay_times = a.List(a.Float)
    switch_pol = a.Bool(False)
    pol_list = a.List(a.Float)
    use_shutter = a.Bool(False)
    use_rot_stage = a.Bool(False)
    rot_stage_angles = a.List(a.Float)


convertors = {
    a.Float: float,
    a.Int: int,
    a.Str: str,
    a.Bool: bool,
    a.Typed: lambda x: to_nested_dict(x),
    a.ForwardTyped: lambda x: to_nested_dict(x),
    a.List: list
}

def to_nested_dict(obj: a.Atom):

    d = obj.members()
    out = {}
    for k,v in d.items():
        attr = getattr(obj, k)
        if isinstance(attr, a.Atom):
            attr = to_nested_dict(attr)
        out[k] = attr# convertors[type(v)](getattr(a, k))
    return out


if __name__ == '__main__':
    from enaml.qt.qt_application import QtApplication
    from qtpy import QtWidgets
    import json
    app = QtApplication()
    with imports():
        from scan_spectrum import ScanSettingsView, PumpProbeSettingsView
    w = QtWidgets.QMainWindow()
    pp = PumpProbeSettings()
    print(json.dumps(to_nested_dict(pp)))
    pv = PumpProbeSettingsView(pp=pp)
    pv.initialize()
    pv.activate_proxy()
    pv.proxy.widget.show()
    fv = ScanSettingsView(ss=ScanSpectrumSettings(), si=SampleInfo(), focus=FocusInfo())
    fv.initialize()
    fv.activate_proxy()
    w.setCentralWidget(fv.proxy.widget)
    w.show()
    app.start()



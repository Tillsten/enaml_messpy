from atom.api import List, Typed, Bool, Float, Value, Int, Enum, Atom, ForwardTyped, Instance, Event, List
from atom.atom import set_default
from numpy.core.arrayprint import SubArrayFormat
from .common import SampleInfo, SetupInfo, Meta, Plan
from Instruments.interfaces import Cam, TuneableCam, DelayLine, PolRotationStage, Shutter
import tables as tb
import zarr


class PumpProbeCamSettings(Atom):
    center_wls = List(Float)
    cam = ForwardTyped('Cam')    

class PumpProbeSettings(Meta):            
    setup_info = Typed(SetupInfo, factory=SetupInfo)
    sample_info = Typed(SampleInfo, factory=SampleInfo)
    delay_times = List(Float)    
    switch_pol = Enum('No', 'Para/Perp', 'custom')
    pol_list = List(Float)
    use_shutter = Bool(False)
    use_rot_stage = Bool(False)
    rot_stage_angles = List(Float) 
    interleave = Bool(False)

class PumpProbeCamData:
    cam: Cam = ForwardTyped('Cam')
    plan: 'PumpProbe' = ForwardTyped('PumpProbe')
    scans = Int(0)
    
    currect_scan = Value()
    all_scans = Value()
    data: zarr.Group = Value()

    def __init__(self):
        cam = self.cam
        self.data =self.plan.root.create_group(self.cam.name)
        self.data.zeros('sigals', shape=(0, len(cam.sig_lines), cam.pixel))
        self.data.zeros('stds', shape=(0, len(cam.std_lines), cam.pixel)) 
        self.data.zeros('lines', shape=(0, len(cam.lines), cam.pixel)) 
        self.data.attrs['names'] = dict(signals=cam.sig_lines, stds=cam.std_lines, lines=cam.lines)
    
    def read(self):
        lr = self.cam.read_cam()
        self.data['signals'].append(lr.sig)
        self.data['stds'].append(lr.std)
        self.data['lines'].append(lr.lines)


class PumpProbe(Plan):    
    required_instruments = set_default(List([DelayLine, Cam]))
    optional_instruments = set_default(List([Cam, PolRotationStage, Shutter]))
    
    cam_list: List = List(Instance(Cam))
    cam_results = Value()
    delay_line: DelayLine = Typed(DelayLine)
    rot_stage: PolRotationStage = Typed(PolRotationStage)
    shutter: Shutter = Typed(Shutter)
    settings: PumpProbeSettings = Typed(PumpProbeSettings)
    

    root = Typed(zarr.Group, factory=zarr.group())

    pre_scan = Event()
    pre_reading = Event()
    post_reading = Event()
    dl_scan_finnished = Event()

    def __init__(self):
        self.check_instruments()
        s = self.settings
        if s.use_shutter and self.shutter:
            self.pre_reading.bind(self.shutter.open)
            self.post_reading.bind(self.shutter.close)

        if s.use_rot_stage:
            self.pre_scan.bind(self.next_pol)

    
    def step(self):
        while not self.stop_next: 
            self.pre_scan.emit()
            yield from self.make_scan()

    def make_scan(self):        
        for t_idx, t in enumerate(self.settings.delay_times):
            self.delay_line.set_pos_fs(t)
            while self.delay_line.is_moving():
                yield 'Moving DL'
            self.pre_reading.emit()
            for c in self.cam_list: 
                c: Cam
                yield from c.read_cam()
            self.post_reading.emit()

    def next_pol(self):
        pass
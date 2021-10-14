from atom.api import List, Typed, Bool, Float, Value, Int, Enum, Atom, ForwardTyped, Instance, Event, List
from atom.atom import set_default
from numpy.core.arrayprint import SubArrayFormat
from .common import SampleInfo, SetupInfo, Meta, Plan
from Instruments.interfaces import Cam, TuneableCam, DelayLine, PolRotationStage, Shutter
import tables as tb
import zarr


class TwoDPlan(Plan):
    setup_info = Typed(SetupInfo, factory=SetupInfo)
    sample_info = Typed(SampleInfo, factory=SampleInfo)
    waiting_times = List(Float)
    rot_frame = Float()
    phase_cycling = Bool()





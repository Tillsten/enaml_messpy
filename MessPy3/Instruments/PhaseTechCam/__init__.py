from MessPy3.Instruments.interfaces import TuneableCam
from atom.api import *


class PhaseTechCam(TuneableCam):
    pixel = set_default(128)
    lines = set_default(['para', 'perp', 'ref'])
    std_lines = set_default(['para', 'perp', 'ref', 'norm'])
    
    def read_cam(self) -> None:

        return 

    def record_bg(self):                
        pass


    def delete_bg(self):
        return super().delete_bg()
    
    has_turret = set_default(True)


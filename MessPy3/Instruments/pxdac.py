import cppyy
import cppyy.ll as ll
import ctypes as ct
import ctypes.wintypes as wt
import numpy as np

# %%
cppyy.load_library(
    "C:\Program Files (x86)\Signatec\PXDAC4800\Lib64\PXDAC4800_64.dll")
cppyy.add_include_path(r'C:\Program Files (x86)\Signatec\PXDAC4800\Include')
cppyy.include('pxdac4800.h')

gbl = cppyy.gbl

MASK_SIZE = 4096


def ec(err):
    if err < 0:
        raise ValueError()


class PXDAC:
    def __init__(self) -> None:
        self.hdl = ct.pointer(ct.c_ulong())
        ec(gbl.ConnectToDeviceXD48(self.hdl, 1))

    def set_params(self):
        ec(gbl.SetActiveChannelMaskXD48(self.hdl, 0x1 | 0x2))
        ec(gbl.SetDacSampleFormatXD48(self.hdl, 1))
        ec(gbl.SetDacSampleSizeXD48(self.hdl, 2))

    def stop_playback(self):
        ec(gbl.EndRamPlaybackXD48(self.hdl))

    def load_masks(self, masks):
        self.stop_playback()
        if (masks.size % MASK_SIZE) != 0:
            raise ValueError('Mask size must be a multiple of 4096')
        if masks.dtype != np.int16:
            raise ValueError('dtype of mask array must be int16')
        ec(gbl.LoadRamBufXD48(self.hdl, 0, masks.size*2, masks.data, 0))

    def start_playback(self):
        ec(gbl.BeginRamPlaybackXD48(self.hdl, 0, MASK_SIZE))

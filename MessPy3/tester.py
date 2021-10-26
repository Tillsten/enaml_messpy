from enaml import imports


from enaml.qt.qt_application import QtApplication

app = QtApplication()

with imports():
    from Views.CustomWidgets import SettingsDialog, TestWindow
    from Plans.ScanSpectrumView import ScanSpectrumSettingsView
    from Plans.ScanSpectrum import ScanSpectrumSettings

tw = TestWindow(ScanSpectrumSettingsView)()[0]
tw.model = ScanSpectrumSettings()
tw.show()

async def test():
    return 5

#ScanSpectrumSettingsView().show()
import qasync
loop = qasync.QEventLoop(app._qapp)
import asyncio as aio
aio.set_event_loop(loop)
task = aio.create_task(test())

app.start()

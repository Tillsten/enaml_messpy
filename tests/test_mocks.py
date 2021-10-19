from MessPy3.Instruments import mocks

def test_delay_mock():
    dl = mocks.MockDelayLine()
    pos = dl.get_pos_fs()
    pos_mm = dl.get_pos()
    dl.set_pos_fs(2000)
    assert(dl.is_moving())
    while dl.is_moving():
        pass
    assert(dl.get_pos_fs() == 2000)

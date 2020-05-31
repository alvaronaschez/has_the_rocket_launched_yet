from src.video_utils import FrameX


def test_getitem():
    expected_result = (
        r"https://framex-dev.wadrid.net/api/video/"
        r"Falcon%20Heavy%20Test%20Flight%20%28Hosted%20Webcast%29-wbSwFU6tY1c"
        r"/frame/1695/")
    frames = FrameX()
    assert expected_result == frames[1695]


def test_len():
    frames = FrameX()
    assert len(frames) == 61696

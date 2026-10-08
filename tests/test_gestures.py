from types import SimpleNamespace

from src.gestures import DwellDetector, PinchDetector, pinch_ratio


def test_pinch_rising_edge():
    detector = PinchDetector(0.25, 0.35)
    assert detector.update(0.2)
    assert not detector.update(0.2)
    assert not detector.update(0.4)
    assert detector.update(0.2)


def test_pinch_ratio():
    points = [SimpleNamespace(x=0.0, y=0.0) for _ in range(10)]
    points[4] = SimpleNamespace(x=0.1, y=0.0)
    points[8] = SimpleNamespace(x=0.0, y=0.0)
    points[9] = SimpleNamespace(x=0.0, y=1.0)
    assert pinch_ratio(points) == 0.1


def test_dwell_detector():
    now = [0.0]
    detector = DwellDetector(1.0, clock=lambda: now[0])
    assert detector.update("7") == (False, 0.0)
    now[0] = 1.0
    assert detector.update("7") == (True, 0.0)
    assert detector.update(None) == (False, 0.0)

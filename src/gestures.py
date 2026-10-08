"""Gesture detectors and fingertip smoothing."""

from __future__ import annotations

import math
import time
from collections.abc import Callable


def pinch_ratio(landmarks: object) -> float:
    """Return normalized thumb-to-index distance for MediaPipe landmarks."""
    pinch = math.dist((landmarks[4].x, landmarks[4].y), (landmarks[8].x, landmarks[8].y))
    hand = math.dist((landmarks[0].x, landmarks[0].y), (landmarks[9].x, landmarks[9].y))
    return pinch / max(hand, 1e-6)


class PinchDetector:
    """Detect a single event when a pinch begins."""

    def __init__(self, on: float, off: float) -> None:
        self.on, self.off, self.pinched = on, off, False

    def update(self, ratio: float) -> bool:
        """Return true only on the open-to-pinched transition."""
        if not self.pinched and ratio < self.on:
            self.pinched = True
            return True
        if self.pinched and ratio > self.off:
            self.pinched = False
        return False

    def reset(self) -> None:
        """Reset the detector when no hand is visible."""
        self.pinched = False


class Smoother:
    """Exponential moving average for pixel coordinates."""

    def __init__(self, alpha: float) -> None:
        self.alpha, self.position = alpha, None

    def update(self, point: tuple[int, int]) -> tuple[int, int]:
        """Return a smoothed coordinate."""
        if self.position is None:
            self.position = point
        else:
            self.position = tuple(
                int(self.alpha * current + (1 - self.alpha) * previous)
                for current, previous in zip(point, self.position)
            )
        return self.position

    def reset(self) -> None:
        """Forget the previous coordinate."""
        self.position = None


class DwellDetector:
    """Fire after a cursor remains over one button for a duration."""

    def __init__(self, duration: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.duration, self.clock = duration, clock
        self.button_key, self.started = None, None

    def update(self, button_key: object | None) -> tuple[bool, float]:
        """Return whether dwell completed and its progress from zero to one."""
        now = self.clock()
        if button_key is None:
            self.reset()
            return False, 0.0
        if button_key != self.button_key:
            self.button_key, self.started = button_key, now
        progress = min(1.0, (now - self.started) / self.duration)
        if progress >= 1.0:
            self.started = now
            return True, 0.0
        return False, progress

    def reset(self) -> None:
        """Reset the dwell timer."""
        self.button_key, self.started = None, None

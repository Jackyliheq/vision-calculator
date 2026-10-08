"""OpenCV camera lifecycle helpers."""

from __future__ import annotations

import cv2

from . import config


def open_camera() -> cv2.VideoCapture:
    """Open the configured webcam or raise a clear error."""
    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError("Camera not found. Check that it is connected and not in use.")
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    return camera

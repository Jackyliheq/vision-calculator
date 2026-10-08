"""MediaPipe hand tracking wrapper."""

from __future__ import annotations

from dataclasses import dataclass

import cv2

from . import config


@dataclass(frozen=True)
class HandPoints:
    """Pixel coordinates and normalized landmarks for the tracked hand."""

    index_tip: tuple[int, int]
    landmarks: object


class HandTracker:
    """Track one hand and expose the index fingertip."""

    def __init__(self) -> None:
        import mediapipe as mp

        self._mp = mp
        if not config.MODEL_PATH.is_file():
            raise RuntimeError(f"Hand model not found: {config.MODEL_PATH}")
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(config.MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self._hands = mp.tasks.vision.HandLandmarker.create_from_options(options)

    def find(self, frame) -> HandPoints | None:
        """Return hand points for a BGR frame, or None when no hand is found."""
        height, width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        result = self._hands.detect(image)
        if not result.hand_landmarks:
            return None
        landmarks = result.hand_landmarks[0]
        return HandPoints((int(landmarks[8].x * width), int(landmarks[8].y * height)), landmarks)

    def close(self) -> None:
        """Release MediaPipe resources."""
        self._hands.close()

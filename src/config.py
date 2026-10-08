"""Application constants for the Vision Calculator."""

from pathlib import Path

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
WINDOW_NAME = "Vision Calculator"

PINCH_ON_RATIO = 0.25
PINCH_OFF_RATIO = 0.35
DEBOUNCE_SECONDS = 0.4
DWELL_SECONDS = 1.0
SMOOTHING_ALPHA = 0.4

PANEL_WIDTH = 430
PANEL_HEIGHT = 620
BUTTON_SIZE = 82
BUTTON_GAP = 8
PANEL_MARGIN = 24

PANEL_COLOR = (35, 35, 35)
BUTTON_COLOR = (65, 65, 65)
OPERATOR_COLOR = (80, 105, 155)
HOVER_COLOR = (100, 170, 90)
TEXT_COLOR = (240, 240, 240)
CURSOR_COLOR = (0, 220, 255)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

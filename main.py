"""Run the camera-driven Vision Calculator."""

from __future__ import annotations

import time

import cv2

from src import config
from src.calculator_logic import Calculator
from src.calculator_ui import CalculatorUI
from src.camera import open_camera
from src.gestures import DwellDetector, PinchDetector, Smoother, pinch_ratio
from src.hand_tracker import HandTracker


def run() -> None:
    """Run the calculator until the user presses q or the camera stops."""
    camera = open_camera()
    tracker = HandTracker()
    calculator = Calculator()
    ui = CalculatorUI(config.FRAME_WIDTH, config.FRAME_HEIGHT)
    pinch = PinchDetector(config.PINCH_ON_RATIO, config.PINCH_OFF_RATIO)
    dwell = DwellDetector(config.DWELL_SECONDS)
    smoother = Smoother(config.SMOOTHING_ALPHA)
    dwell_mode = False
    last_press = 0.0

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            points = tracker.find(frame)
            cursor = None
            hovered = None
            dwell_progress = 0.0
            if points is None:
                pinch.reset()
                dwell.reset()
                smoother.reset()
            else:
                cursor = smoother.update(points.index_tip)
                hovered = ui.hit_test(cursor)
                pressed = False
                if dwell_mode:
                    pressed, dwell_progress = dwell.update(hovered.action if hovered else None)
                elif pinch.update(pinch_ratio(points.landmarks)):
                    pressed = True
                now = time.monotonic()
                if pressed and hovered and now - last_press >= config.DEBOUNCE_SECONDS:
                    calculator.press(hovered.action)
                    last_press = now

            ui.draw(frame, calculator.expression, calculator.result, hovered)
            if cursor:
                cv2.circle(frame, cursor, 12, config.CURSOR_COLOR, 2)
                if dwell_mode and dwell_progress:
                    cv2.ellipse(frame, cursor, (20, 20), 0, 0, int(360 * dwell_progress),
                                config.HOVER_COLOR, 3)
            cv2.putText(frame, f"Dwell: {'ON' if dwell_mode else 'OFF'} (d to toggle)",
                        (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, config.TEXT_COLOR, 2)
            cv2.imshow(config.WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("d"):
                dwell_mode = not dwell_mode
                pinch.reset()
                dwell.reset()
    finally:
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        run()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

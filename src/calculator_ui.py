"""Calculator button layout, drawing, and hit-testing."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from . import config


@dataclass(frozen=True)
class Button:
    """A rectangular calculator button."""

    label: str
    action: str
    x: int
    y: int
    width: int
    height: int

    def contains(self, px: int, py: int) -> bool:
        """Return whether a point lies inside this button."""
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height


class CalculatorUI:
    """Create and render a fixed-size calculator panel."""

    def __init__(self, frame_width: int, frame_height: int) -> None:
        self.origin_x = max(config.PANEL_MARGIN, frame_width - config.PANEL_WIDTH - config.PANEL_MARGIN)
        self.origin_y = max(config.PANEL_MARGIN, (frame_height - config.PANEL_HEIGHT) // 2)
        self.buttons = self._make_buttons()

    def _make_buttons(self) -> list[Button]:
        labels = [
            [("7", "7"), ("8", "8"), ("9", "9"), ("/", "/")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("x", "*")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("-", "-")],
            [("0", "0"), (".", "."), ("=", "="), ("+", "+")],
            [("C", "C"), ("<-", "backspace")],
        ]
        buttons: list[Button] = []
        for row, items in enumerate(labels):
            for column, (label, action) in enumerate(items):
                buttons.append(
                    Button(
                        label,
                        action,
                        self.origin_x + 18 + column * (config.BUTTON_SIZE + config.BUTTON_GAP),
                        self.origin_y + 150 + row * (config.BUTTON_SIZE + config.BUTTON_GAP),
                        config.BUTTON_SIZE,
                        config.BUTTON_SIZE,
                    )
                )
        return buttons

    def hit_test(self, point: tuple[int, int] | None) -> Button | None:
        """Return the button under a point, if any."""
        if point is None:
            return None
        return next((button for button in self.buttons if button.contains(*point)), None)

    def draw(self, frame: np.ndarray, expression: str, result: str | None, hovered: Button | None) -> None:
        """Draw the calculator and its current display onto a frame."""
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (self.origin_x, self.origin_y),
            (self.origin_x + config.PANEL_WIDTH, self.origin_y + config.PANEL_HEIGHT),
            config.PANEL_COLOR,
            -1,
        )
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)
        display = expression or "0"
        cv2.putText(frame, display[-22:], (self.origin_x + 18, self.origin_y + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, config.TEXT_COLOR, 2, cv2.LINE_AA)
        if result is not None:
            cv2.putText(frame, f"= {result}", (self.origin_x + 18, self.origin_y + 92),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.HOVER_COLOR, 2, cv2.LINE_AA)
        for button in self.buttons:
            color = config.HOVER_COLOR if button == hovered else (
                config.OPERATOR_COLOR if button.action in "+-*/=" else config.BUTTON_COLOR
            )
            cv2.rectangle(frame, (button.x, button.y),
                          (button.x + button.width, button.y + button.height), color, -1)
            text_size = cv2.getTextSize(button.label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            text_x = button.x + (button.width - text_size[0]) // 2
            text_y = button.y + (button.height + text_size[1]) // 2
            cv2.putText(frame, button.label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.TEXT_COLOR, 2, cv2.LINE_AA)

import numpy as np

from src.calculator_ui import CalculatorUI


def test_hit_testing_and_edges():
    ui = CalculatorUI(1280, 720)
    button = next(button for button in ui.buttons if button.action == "7")
    assert ui.hit_test((button.x, button.y)) == button
    assert ui.hit_test((button.x + button.width, button.y + button.height)) == button
    assert ui.hit_test(None) is None


def test_draw():
    ui = CalculatorUI(1280, 720)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    ui.draw(frame, "1+2", "3", None)
    assert frame.any()

import pytest

from src.calculator_logic import Calculator, safe_eval


@pytest.mark.parametrize(("expression", "expected"), [("2+3", 5), ("10/4", 2.5), ("-5+2", -3)])
def test_safe_eval(expression, expected):
    assert safe_eval(expression) == expected


def test_rejects_unsafe_expression():
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('ls')")


def test_calculator_operations():
    calculator = Calculator()
    for button in "12+3":
        calculator.press(button)
    calculator.press("=")
    assert calculator.result == "15"


def test_division_by_zero_is_error():
    calculator = Calculator("1/0")
    calculator.press("=")
    assert calculator.result == "Error"


def test_decimal_and_backspace():
    calculator = Calculator()
    calculator.press(".")
    calculator.press("1")
    calculator.press(".")
    assert calculator.expression == "0.1"
    calculator.press("backspace")
    assert calculator.expression == "0."

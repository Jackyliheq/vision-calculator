"""Calculator state and safe arithmetic evaluation."""

from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}
_MAX_EXPRESSION_LENGTH = 100


def safe_eval(expression: str) -> float:
    """Evaluate a basic arithmetic expression without executing arbitrary code."""
    if not expression or len(expression) > _MAX_EXPRESSION_LENGTH:
        raise ValueError("Invalid expression")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Invalid expression") from exc

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](evaluate(node.operand))
        raise ValueError("Unsupported expression")

    return evaluate(tree)


@dataclass
class Calculator:
    """Manage calculator input, result, and error state."""

    expression: str = ""
    result: str | None = None

    def press(self, button: str) -> None:
        """Apply one calculator button action."""
        if button == "C":
            self.expression, self.result = "", None
        elif button == "backspace":
            self.expression = self.expression[:-1]
            self.result = None
        elif button == "=":
            self._calculate()
        elif button in "+-*/":
            self._press_operator(button)
        elif button == ".":
            self._press_decimal()
        elif button.isdigit():
            if self.result is not None:
                self.expression, self.result = "", None
            self.expression += button
        else:
            raise ValueError(f"Unknown button: {button}")

    def _press_operator(self, operator_symbol: str) -> None:
        if self.result is not None:
            self.expression, self.result = self.result, None
        if not self.expression:
            if operator_symbol == "-":
                self.expression = "-"
            return
        if self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1] + operator_symbol
        else:
            self.expression += operator_symbol

    def _press_decimal(self) -> None:
        if self.result is not None:
            self.expression, self.result = "", None
        current = re.split(r"[+\-*/]", self.expression)[-1]
        if "." not in current:
            self.expression += "0." if not current else "."

    def _calculate(self) -> None:
        try:
            value = safe_eval(self.expression)
            self.result = _format_number(value)
        except (ValueError, ZeroDivisionError, OverflowError):
            self.result = "Error"


def _format_number(value: float) -> str:
    """Format numeric results without unnecessary trailing zeroes."""
    if value == int(value):
        return str(int(value))
    return f"{value:.12g}"

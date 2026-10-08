# skills.md

Skills and patterns the coding agent should apply when building the Vision Calculator. Each skill lists what it is, when to use it, and a short reference.

---

## 1. Webcam Capture (OpenCV)

**Use for:** opening the camera, reading frames, mirroring, cleanup.

```python
import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera not found. Check that it is connected and not in use.")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror so movement feels natural
        cv2.imshow("Vision Calculator", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
```

**Rules:** always release in `finally`; flip horizontally; try camera index 1 if 0 fails.

---

## 2. Hand Landmark Tracking (MediaPipe)

**Use for:** getting the fingertip and thumb positions.

Key landmarks:
- `4` = thumb tip
- `8` = index fingertip (the cursor)
- `0` = wrist, `9` = middle finger base (used to measure hand size)

```python
import mediapipe as mp

hands = mp.solutions.hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
)

# frame is BGR from OpenCV; MediaPipe wants RGB
result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
if result.multi_hand_landmarks:
    lm = result.multi_hand_landmarks[0].landmark
    h, w, _ = frame.shape
    index_tip = (int(lm[8].x * w), int(lm[8].y * h))
    thumb_tip = (int(lm[4].x * w), int(lm[4].y * h))
```

**Rules:** convert BGR to RGB; return `None` when no hand is found; use `max_num_hands=1`; if the installed MediaPipe version no longer exposes `mp.solutions`, use the newer `mediapipe.tasks` HandLandmarker API instead.

---

## 3. Pinch (Click) Detection

**Use for:** turning landmarks into a click event.

Normalize by hand size so it works at any distance from the camera.

```python
import math

def pinch_ratio(lm) -> float:
    d_pinch = math.dist((lm[4].x, lm[4].y), (lm[8].x, lm[8].y))
    d_hand = math.dist((lm[0].x, lm[0].y), (lm[9].x, lm[9].y))
    return d_pinch / max(d_hand, 1e-6)

class PinchDetector:
    def __init__(self, on=0.25, off=0.35):
        self.on, self.off, self.pinched = on, off, False

    def update(self, ratio: float) -> bool:
        """Returns True only on the frame where a pinch starts."""
        if not self.pinched and ratio < self.on:
            self.pinched = True
            return True
        if self.pinched and ratio > self.off:
            self.pinched = False
        return False
```

**Rules:** use two thresholds (hysteresis) so the click does not flicker; fire on the rising edge only; tune `on` and `off` in `config.py`.

---

## 4. Dwell Click

**Use for:** an alternative click for users who cannot pinch easily.

- Track which button the fingertip is on and when it arrived.
- If the button stays the same for `DWELL_SECONDS` (about 1.0), fire a click.
- Reset the timer when the fingertip leaves the button.
- Draw a progress arc around the cursor while dwelling.

```python
cv2.ellipse(frame, center, (20, 20), 0, 0, int(360 * progress), (0, 255, 0), 3)
```

---

## 5. Fingertip Smoothing

**Use for:** removing jitter so buttons are easier to hit.

```python
class Smoother:
    def __init__(self, alpha=0.4):
        self.alpha, self.pos = alpha, None

    def update(self, p):
        if self.pos is None:
            self.pos = p
        else:
            self.pos = (
                int(self.alpha * p[0] + (1 - self.alpha) * self.pos[0]),
                int(self.alpha * p[1] + (1 - self.alpha) * self.pos[1]),
            )
        return self.pos
```

Lower `alpha` means smoother but laggier. Start around 0.4 and tune.

---

## 6. Calculator UI Drawing and Hit-Testing

**Use for:** drawing buttons on the frame and finding which one is under the cursor.

Layout (4 columns):

```
[ 7 ][ 8 ][ 9 ][ ÷ ]
[ 4 ][ 5 ][ 6 ][ × ]
[ 1 ][ 2 ][ 3 ][ - ]
[ 0 ][ . ][ = ][ + ]
[ C ][ ⌫ ]
```

```python
from dataclasses import dataclass

@dataclass
class Button:
    label: str
    x: int
    y: int
    w: int
    h: int

    def contains(self, px: int, py: int) -> bool:
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h
```

Drawing tips:
- Use a semi-transparent panel: draw on a copy, then `cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)`.
- Highlight the hovered button with a different fill color.
- Flash a button briefly after it is pressed.
- OpenCV's default fonts cannot render `×`, `÷`, or `⌫`. Either draw them with lines, use Pillow (`ImageFont`) to render text, or display `x`, `/`, and `<-` instead.

---

## 7. Safe Expression Evaluation

**Use for:** computing results without `eval()`.

```python
import ast
import operator as op

_OPS = {
    ast.Add: op.add, ast.Sub: op.sub,
    ast.Mult: op.mul, ast.Div: op.truediv,
    ast.USub: op.neg,
}

def safe_eval(expr: str) -> float:
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression")
    return _eval(ast.parse(expr, mode="eval"))
```

Before parsing, convert display symbols: `×` to `*`, `÷` to `/`.

**Rules:** catch `ZeroDivisionError` and `ValueError` and show `Error`; never pass raw user input to `eval`/`exec`; limit expression length.

---

## 8. Calculator State Machine

**Use for:** handling button presses cleanly.

State: `expression` (string) and `result` (string or None).

| Button | Behavior |
|---|---|
| digit | append; if a result is showing, start a new expression |
| operator | append; if a result is showing, continue from the result; replace a trailing operator instead of stacking two |
| `.` | allow only one decimal point per number |
| `=` | evaluate; store result; show `Error` on failure |
| `C` | clear everything |
| `⌫` | remove the last character |

Keep this in `calculator_logic.py` with no OpenCV or MediaPipe imports so it is easy to test.

---

## 9. Performance

- Capture at 1280x720 but consider running hand detection on a downscaled copy (for example 640x360) and scaling coordinates back up.
- Reuse the `Hands` object; never create it inside the loop.
- Set `frame.flags.writeable = False` before `hands.process()` for a small speedup.
- Measure FPS with `time.perf_counter()` and display it in debug mode.

---

## 10. Testing with pytest

**Use for:** verifying logic without a camera.

```python
import pytest
from src.calculator_logic import safe_eval

@pytest.mark.parametrize("expr,expected", [
    ("2+3", 5),
    ("10/4", 2.5),
    ("2*3+4", 10),
    ("-5+2", -3),
])
def test_eval(expr, expected):
    assert safe_eval(expr) == expected

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        safe_eval("1/0")

def test_rejects_unsafe():
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('ls')")
```

Also test: hit-testing at button edges, pinch rising-edge behavior with a fake ratio sequence, debounce timing, double-decimal rejection.

---

## 11. Error Handling

- Camera missing: print a clear message and exit.
- Frame read fails: break the loop and clean up.
- No hand in frame: hide cursor, reset pinch state and dwell timer.
- Invalid expression: show `Error`, clear it on the next digit press.

---

## 12. Debugging Tips

- Draw all 21 landmarks with `mp.solutions.drawing_utils` in a debug flag.
- Print the live pinch ratio to choose good thresholds.
- Test in different lighting; add on-screen text like "Show your hand" when nothing is detected.
- If clicks feel unreliable, enlarge buttons and increase smoothing before changing thresholds.

---

## Optional Extensions (later)

- **OCR mode:** read a handwritten or printed expression held up to the camera (OpenCV preprocessing + a digit classifier or an OCR library), then evaluate it.
- **Gesture shortcuts:** open palm to clear, thumbs up to evaluate.
- **Voice or sound feedback** on each press.
- **Packaging:** build a standalone app with PyInstaller.

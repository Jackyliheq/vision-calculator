# Vision Calculator

A calculator you operate with your camera. The webcam feed shows a virtual calculator overlay. The user moves their index finger over a button and "clicks" it with a pinch gesture (or by holding still for a short dwell time). No mouse or keyboard needed.

> This README is written for the coding agent that will build and maintain the project. Read it fully before writing code. See `skills.md` for the specific skills and patterns the agent should apply.

---

## 1. Goal

Build a Python desktop app that:

1. Opens the user's webcam.
2. Draws a calculator UI (digits, operators, clear, equals) on top of the live video.
3. Tracks the user's hand with computer vision.
4. Detects a "click" gesture over a button and enters that button into the calculator.
5. Shows the expression and the result on screen in real time.

## 2. Tech Stack

| Purpose | Library |
|---|---|
| Camera capture + drawing | `opencv-python` |
| Hand landmark detection | `mediapipe` |
| Math helpers | `numpy` |
| Safe expression evaluation | Python `ast` (standard library) |
| Tests | `pytest` |

Python 3.10 or newer.

## 3. Project Structure

```
vision-calculator/
├── README.md
├── skills.md
├── requirements.txt
├── main.py                  # entry point: runs the app loop
├── src/
│   ├── __init__.py
│   ├── camera.py            # webcam open/read/release, mirror flip
│   ├── hand_tracker.py      # MediaPipe wrapper -> fingertip + pinch state
│   ├── gestures.py          # click detection (pinch, dwell), debounce
│   ├── calculator_ui.py     # button layout, drawing, hit-testing
│   ├── calculator_logic.py  # expression state + safe evaluation
│   └── config.py            # all constants (sizes, colors, thresholds)
└── tests/
    ├── test_calculator_logic.py
    ├── test_calculator_ui.py
    └── test_gestures.py
```

## 4. How It Works

```
Camera frame
   -> flip horizontally (mirror view)
   -> HandTracker: find 21 hand landmarks
   -> fingertip position (landmark 8) + thumb tip (landmark 4)
   -> Gestures: is the user pinching? did they dwell on a button?
   -> CalculatorUI: which button is under the fingertip? (hit-test)
   -> CalculatorLogic: apply the button press
   -> Draw overlay (buttons, hover highlight, expression, result)
   -> Show frame
```

### Click methods

- **Pinch click (default):** the distance between thumb tip (4) and index tip (8), divided by hand size, falls below a threshold. Fire the click on the transition from open to pinched, not on every frame.
- **Dwell click (fallback):** the fingertip stays on the same button for about 1 second. Show a progress ring while it fills.

### Debounce rules

- One pinch = exactly one press.
- After a press, ignore new presses for about 400 ms.
- Require the pinch to be released before another press can register.

## 5. Features

### Must have (MVP)

- [ ] Webcam preview, mirrored
- [ ] Buttons: `0-9`, `.`, `+`, `-`, `×`, `÷`, `=`, `C` (clear), `⌫` (backspace)
- [ ] Fingertip cursor drawn on screen
- [ ] Hover highlight on the button under the fingertip
- [ ] Pinch-to-click
- [ ] Expression display and result display
- [ ] Safe evaluation (no `eval`)
- [ ] Division by zero shows `Error` and does not crash
- [ ] Quit with the `q` key

### Nice to have

- [ ] Dwell-to-click mode, toggled with the `d` key
- [ ] Parentheses and `%`
- [ ] Calculation history panel
- [ ] Left-hand / right-hand support
- [ ] Sound or visual feedback on a press
- [ ] Draggable calculator position

## 6. Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The repository includes the official `models/hand_landmarker.task` model used by
MediaPipe's Tasks HandLandmarker API. Keep that file beside the source when
moving or cloning the project.

`requirements.txt`:

```
opencv-python>=4.8
mediapipe>=0.10
numpy>=1.24
pytest>=7.4
```

## 7. Controls

| Action | How |
|---|---|
| Move cursor | Move your index finger |
| Click a button | Pinch thumb and index finger together |
| Toggle dwell mode | Press `d` |
| Quit | Press `q` |

## 8. Coding Rules for the Agent

1. **Never use `eval()` or `exec()`** on user input. Parse with `ast` and allow only numbers and `+ - * /` (plus parentheses if added).
2. Keep logic and UI separate: `calculator_logic.py` must not import OpenCV or MediaPipe so it can be unit tested without a camera.
3. Put every magic number (thresholds, colors, sizes, delays) in `config.py`.
4. Always release the camera and close windows in a `finally` block.
5. Handle "no hand detected" gracefully: hide the cursor, reset the pinch state, do not crash.
6. Handle "camera not found" with a clear error message and a non-zero exit.
7. Keep the main loop at 20 FPS or better on an ordinary laptop. Avoid per-frame allocations in hot paths.
8. Use type hints and short docstrings on every public function.
9. Make buttons large (at least 80x80 px at 1280x720) so finger tracking jitter does not cause misclicks.
10. Smooth the fingertip position (exponential moving average) to reduce jitter.

## 9. Testing

- **Unit tests (no camera):** expression evaluation, backspace/clear behavior, divide by zero, decimal handling, button hit-testing, pinch-threshold logic with fake landmark data.
- **Manual test checklist:**
  - Good lighting, hand 30-60 cm from the camera
  - Dim lighting
  - Fast hand movement
  - Hand leaving and re-entering the frame
  - Two hands in frame (only the first is used)

Run tests:

```bash
pytest -q
```

## 10. Milestones

1. **M1:** Camera opens, mirrored feed displays, `q` quits.
2. **M2:** Hand tracking works and the fingertip cursor follows the finger.
3. **M3:** Calculator overlay drawn, hover highlighting works.
4. **M4:** Pinch click enters digits and operators; logic evaluates safely.
5. **M5:** Debounce, smoothing, error handling, tests.
6. **M6:** Nice-to-have features and polish.

## 11. Known Limitations

- Needs decent lighting and a visible hand.
- Pinch detection is less reliable if the hand is rotated sharply away from the camera.
- MediaPipe's Python package may lag behind the newest Python versions; use a version it supports.

## 12. Definition of Done

- A user can run `python main.py`, calculate `12 × (3 + 4)`-style basic expressions entirely by hand gestures, and see the correct result.
- All unit tests pass.
- No crashes when the hand disappears, the camera fails, or the user divides by zero.

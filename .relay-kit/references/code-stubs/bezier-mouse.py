"""
Bezier + Fitts's Law Mouse Movement — Relay-kit Reference Template
Purpose: Generate human-like mouse trajectories for MMO automation to defeat
         behavioral detection (Pixel Bot detection, MouseMove pattern analysis).

Physics model:
  - Cubic Bezier curve from (x0,y0) to (x1,y1) with 2 randomized control points.
  - Fitts's Law: movement duration ∝ log2(distance / target_width + 1).
  - Gaussian jitter on each waypoint to break straight-line patterns.
  - Micro-pause injection at curve inflection points.

Usage:
    from bezier_mouse import BezierMouse
    mouse = BezierMouse()
    mouse.move_to(800, 600, target_width=32)
    mouse.click()
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Generator

try:
    import ctypes
    _INPUT = ctypes.c_uint
    # Windows SendInput
    _MOUSE_MOVE = 0x0001
    _MOUSEEVENTF_ABSOLUTE = 0x8000
    _SM_CXSCREEN = 0
    _SM_CYSCREEN = 1

    class _MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long), ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class _INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("mi", _MOUSEINPUT)]

    _WINDOWS_AVAILABLE = True
except Exception:
    _WINDOWS_AVAILABLE = False


@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.hypot(other.x - self.x, other.y - self.y)


def _cubic_bezier(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    """Evaluate cubic Bezier at parameter t ∈ [0,1]."""
    mt = 1 - t
    x = mt**3*p0.x + 3*mt**2*t*p1.x + 3*mt*t**2*p2.x + t**3*p3.x
    y = mt**3*p0.y + 3*mt**2*t*p1.y + 3*mt*t**2*p2.y + t**3*p3.y
    return Point(x, y)


def _fitts_duration(distance: float, target_width: float, a: float = 0.05, b: float = 0.12) -> float:
    """Fitts's Law: MT = a + b * log2(distance/width + 1). Returns seconds."""
    if distance < 1:
        return 0.05
    return a + b * math.log2(distance / max(target_width, 1) + 1)


def _random_control_point(start: Point, end: Point, deviation: float = 0.3) -> Point:
    """Generate a control point offset from the midpoint by ±deviation * distance."""
    mid_x = (start.x + end.x) / 2
    mid_y = (start.y + end.y) / 2
    dist = start.distance_to(end)
    perp_x = -(end.y - start.y)
    perp_y = end.x - start.x
    length = math.hypot(perp_x, perp_y) or 1
    offset = random.uniform(-deviation, deviation) * dist
    return Point(mid_x + perp_x / length * offset, mid_y + perp_y / length * offset)


def bezier_waypoints(
    start: Point,
    end: Point,
    steps: int = 60,
    jitter_px: float = 1.5,
) -> Generator[Point, None, None]:
    """Yield `steps` waypoints along a cubic Bezier from start to end with Gaussian jitter."""
    cp1 = _random_control_point(start, end, deviation=random.uniform(0.2, 0.45))
    cp2 = _random_control_point(start, end, deviation=random.uniform(0.1, 0.35))
    for i in range(steps + 1):
        t = i / steps
        # Non-linear t for more natural acceleration/deceleration (ease in-out)
        t_eased = t * t * (3 - 2 * t)
        p = _cubic_bezier(start, cp1, cp2, end, t_eased)
        # Gaussian jitter — magnitude decreases near destination
        jitter_scale = 1 - (t ** 2)
        p.x += random.gauss(0, jitter_px * jitter_scale)
        p.y += random.gauss(0, jitter_px * jitter_scale)
        yield p


class BezierMouse:
    """Human-like mouse controller using Bezier curves + Fitts's Law timing."""

    def __init__(self, steps_per_100px: int = 30, jitter_px: float = 1.5) -> None:
        self.steps_per_100px = steps_per_100px
        self.jitter_px = jitter_px
        self._screen_w, self._screen_h = self._get_screen_size()

    @staticmethod
    def _get_screen_size() -> tuple[int, int]:
        if _WINDOWS_AVAILABLE:
            u32 = ctypes.windll.user32
            return u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)
        return 1920, 1080

    def _get_pos(self) -> Point:
        if _WINDOWS_AVAILABLE:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return Point(pt.x, pt.y)
        return Point(0, 0)

    def _send_move(self, x: int, y: int) -> None:
        if _WINDOWS_AVAILABLE:
            # Normalize to 0-65535 for MOUSEEVENTF_ABSOLUTE
            nx = int(x * 65535 / self._screen_w)
            ny = int(y * 65535 / self._screen_h)
            inp = _INPUT()
            inp.type = 0  # INPUT_MOUSE
            inp.mi.dx = nx
            inp.mi.dy = ny
            inp.mi.dwFlags = _MOUSE_MOVE | _MOUSEEVENTF_ABSOLUTE
            ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def move_to(self, x: int, y: int, target_width: float = 24) -> None:
        start = self._get_pos()
        end = Point(x, y)
        dist = start.distance_to(end)
        steps = max(20, int(dist / 100 * self.steps_per_100px))
        duration = _fitts_duration(dist, target_width)
        delay_per_step = duration / steps

        for waypoint in bezier_waypoints(start, end, steps=steps, jitter_px=self.jitter_px):
            self._send_move(int(waypoint.x), int(waypoint.y))
            # Micro-pause: randomize ±20% of base delay
            time.sleep(delay_per_step * random.uniform(0.8, 1.2))

        # Overshoot + correction (human-like)
        if dist > 80 and random.random() < 0.4:
            over_x = x + random.randint(-4, 4)
            over_y = y + random.randint(-4, 4)
            self._send_move(over_x, over_y)
            time.sleep(random.uniform(0.02, 0.06))
            self._send_move(x, y)

    def click(self, button: str = "left") -> None:
        if _WINDOWS_AVAILABLE:
            u32 = ctypes.windll.user32
            if button == "left":
                u32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
                time.sleep(random.uniform(0.04, 0.12))
                u32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
            elif button == "right":
                u32.mouse_event(0x0008, 0, 0, 0, 0)
                time.sleep(random.uniform(0.04, 0.12))
                u32.mouse_event(0x0010, 0, 0, 0, 0)

    def move_and_click(self, x: int, y: int, target_width: float = 24, button: str = "left") -> None:
        self.move_to(x, y, target_width=target_width)
        time.sleep(random.uniform(0.05, 0.15))  # Pre-click pause
        self.click(button)

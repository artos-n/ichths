"""
Perf Tool — Configuration & Settings
"""
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".perf-tool"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class MonitorConfig:
    """All tunable settings for the overlay."""

    # Window
    x: int = 20
    y: int = 20
    width: int = 320
    height: int = 380
    opacity: float = 0.82
    always_on_top: bool = True
    compact_mode: bool = False
    click_through: bool = False

    # Refresh
    refresh_ms: int = 1000
    fps_refresh_ms: int = 500

    # Modules (which panels to show)
    show_fps: bool = True
    show_cpu: bool = True
    show_gpu: bool = True
    show_ram: bool = True
    show_network: bool = True
    show_temps: bool = True

    # Theme
    accent_color: str = "#00D4FF"
    warning_color: str = "#FFB800"
    danger_color: str = "#FF3B5C"
    success_color: str = "#00E676"
    glass_bg: str = "rgba(20, 20, 30, 0.55)"
    glass_blur: int = 24
    border_color: str = "rgba(255, 255, 255, 0.12)"
    text_primary: str = "#FFFFFF"
    text_secondary: str = "rgba(255, 255, 255, 0.65)"

    # Bar
    bar_height: int = 6
    bar_radius: int = 3
    bar_bg: str = "rgba(255, 255, 255, 0.08)"

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls) -> "MonitorConfig":
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    data = json.load(f)
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except Exception:
                pass
        return cls()

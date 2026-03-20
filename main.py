#!/usr/bin/env python3
"""
Gaming Performance Monitor — Entry Point

A real-time glassmorphism performance overlay for gamers.
Displays CPU, GPU, RAM, network, and FPS metrics in a
frosted-glass always-on-top window.

Usage:
    python main.py                      # Default settings
    python main.py --x 100 --y 100      # Custom position
    python main.py --compact             # Compact mode
    python main.py --refresh 500         # 500ms refresh rate
    python main.py --opacity 0.9         # 90% opacity
    python main.py --no-gpu --no-network # Disable modules
"""
import sys
import argparse

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from config import MonitorConfig
from monitor import SystemMonitor
from overlay import GlassOverlay


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gaming Performance Monitor — Glassmorphism Overlay",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--x", type=int, help="Window X position")
    parser.add_argument("--y", type=int, help="Window Y position")
    parser.add_argument("--width", type=int, help="Window width")
    parser.add_argument("--height", type=int, help="Window height")
    parser.add_argument("--opacity", type=float, help="Overlay opacity (0.0 - 1.0)")
    parser.add_argument("--refresh", type=int, help="UI refresh rate in ms")
    parser.add_argument("--compact", action="store_true", help="Start in compact mode")

    parser.add_argument("--no-fps", action="store_true", help="Hide FPS counter")
    parser.add_argument("--no-cpu", action="store_true", help="Hide CPU card")
    parser.add_argument("--no-gpu", action="store_true", help="Hide GPU card")
    parser.add_argument("--no-ram", action="store_true", help="Hide RAM card")
    parser.add_argument("--no-network", action="store_true", help="Hide network card")
    parser.add_argument("--no-temps", action="store_true", help="Hide temperature display")

    return parser.parse_args()


def apply_args(config: MonitorConfig, args):
    """Apply CLI args to config, overriding saved settings."""
    if args.x is not None:
        config.x = args.x
    if args.y is not None:
        config.y = args.y
    if args.width is not None:
        config.width = args.width
    if args.height is not None:
        config.height = args.height
    if args.opacity is not None:
        config.opacity = max(0.1, min(1.0, args.opacity))
    if args.refresh is not None:
        config.refresh_ms = max(100, args.refresh)
    if args.compact:
        config.compact_mode = True

    config.show_fps = not args.no_fps
    config.show_cpu = not args.no_cpu
    config.show_gpu = not args.no_gpu
    config.show_ram = not args.no_ram
    config.show_network = not args.no_network
    config.show_temps = not args.no_temps


def main():
    args = parse_args()

    # Load config, apply CLI overrides
    config = MonitorConfig.load()
    apply_args(config, args)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Gaming Monitor")
    app.setQuitOnLastWindowClosed(True)

    # Set a clean default font
    font = QFont("Segoe UI", 9)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # Start system monitor
    monitor = SystemMonitor(refresh_interval=config.refresh_ms / 1000.0)
    monitor.start()

    # Create overlay
    overlay = GlassOverlay(config, monitor)
    overlay.show()

    print(f"🎮 Gaming Monitor running at ({config.x}, {config.y})")
    print(f"   Refresh: {config.refresh_ms}ms | Opacity: {config.opacity:.0%}")
    print(f"   Shortcuts: F9=hide | F10=opacity | F11=compact | Ctrl+Q=quit")

    # Run
    exit_code = app.exec()

    # Cleanup
    monitor.stop()
    config.save()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

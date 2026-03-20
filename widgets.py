"""
Perf Tool — Glassmorphism Overlay Widget
Individual metric widgets rendered as frosted-glass cards.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QPen, QFont
from config import MonitorConfig


class GlassCard(QWidget):
    """
    A single glassmorphism card with title, value, optional bar, and optional subtitle.
    """

    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self._value = "—"
        self._subtitle = ""
        self._bar_value = 0.0
        self._bar_color = "#00D4FF"
        self._show_bar = True
        self._unit = "%"
        self.setFixedHeight(68)

    def set_data(self, value: str, bar_value: float = 0.0, subtitle: str = "",
                 bar_color: str = "#00D4FF", unit: str = "%"):
        changed = (self._value != value or self._bar_value != bar_value or
                   self._subtitle != subtitle or self._bar_color != bar_color)
        self._value = value
        self._bar_value = min(100, max(0, bar_value))
        self._subtitle = subtitle
        self._bar_color = bar_color
        self._unit = unit
        if changed:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Glass background
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 14, 14)
        painter.fillPath(path, QColor(255, 255, 255, 18))

        # Border glow
        pen = QPen(QColor(255, 255, 255, 25))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        painter.drawPath(path)

        # Inner highlight (top edge shine)
        highlight = QPainterPath()
        highlight.addRoundedRect(1, 1, w - 2, h / 2, 13, 13)
        painter.fillPath(highlight, QColor(255, 255, 255, 8))

        # Icon + Title
        painter.setPen(QColor(255, 255, 255, 160))
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        title_text = f"{self._icon}  {self._title}" if self._icon else self._title
        painter.drawText(16, 20, title_text)

        # Value (big number)
        painter.setPen(QColor(255, 255, 255, 240))
        font = QFont("Segoe UI", 18)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(16, 44, f"{self._value}{self._unit}")

        # Subtitle (right-aligned)
        if self._subtitle:
            painter.setPen(QColor(255, 255, 255, 120))
            font = QFont("Segoe UI", 8)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            sw = metrics.horizontalAdvance(self._subtitle)
            painter.drawText(w - sw - 16, 20, self._subtitle)

        # Progress bar
        if self._show_bar:
            bar_x = 16
            bar_y = 54
            bar_w = w - 32
            bar_h = 5

            # Bar background
            bar_bg = QPainterPath()
            bar_bg.addRoundedRect(bar_x, bar_y, bar_w, bar_h, 2.5, 2.5)
            painter.fillPath(bar_bg, QColor(255, 255, 255, 18))

            # Bar fill
            fill_w = max(0, bar_w * self._bar_value / 100)
            if fill_w > 0:
                bar_fill = QPainterPath()
                bar_fill.addRoundedRect(bar_x, bar_y, fill_w, bar_h, 2.5, 2.5)

                # Gradient fill
                gradient = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
                base_color = QColor(self._bar_color)
                gradient.setColorAt(0, base_color)
                lighter = QColor(base_color)
                lighter.setAlpha(200)
                gradient.setColorAt(1, lighter)
                painter.fillPath(bar_fill, gradient)

        painter.end()


class NetworkCard(QWidget):
    """Special card for network with download/upload side by side."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dl = "0.0"
        self._ul = "0.0"
        self.setFixedHeight(50)

    def set_data(self, download_mbps: float, upload_mbps: float):
        self._dl = f"{download_mbps:.1f}"
        self._ul = f"{upload_mbps:.1f}"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Glass background
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 14, 14)
        painter.fillPath(path, QColor(255, 255, 255, 18))

        pen = QPen(QColor(255, 255, 255, 25))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        painter.drawPath(path)

        # Download
        painter.setPen(QColor(255, 255, 255, 160))
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        painter.drawText(16, 18, "⬇ Download")

        painter.setPen(QColor(0, 212, 255, 240))
        font = QFont("Segoe UI", 14)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(16, 38, f"{self._dl} Mbps")

        # Upload
        painter.setPen(QColor(255, 255, 255, 160))
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        mid = w // 2
        painter.drawText(mid, 18, "⬆ Upload")

        painter.setPen(QColor(0, 230, 118, 240))
        font = QFont("Segoe UI", 14)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(mid, 38, f"{self._ul} Mbps")

        painter.end()


class HeaderWidget(QWidget):
    """The top header with app title and FPS display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fps = 0
        self._title = "PERFORMANCE MONITOR"
        self.setFixedHeight(50)

    def set_fps(self, fps: int):
        if self._fps != fps:
            self._fps = fps
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Title
        painter.setPen(QColor(255, 255, 255, 100))
        font = QFont("Segoe UI", 8)
        font.setWeight(QFont.Weight.DemiBold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        painter.drawText(16, 20, self._title)

        # FPS badge (right side)
        if self._fps > 0:
            fps_text = f"{self._fps} FPS"
            font = QFont("Segoe UI", 13)
            font.setWeight(QFont.Weight.Bold)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            tw = metrics.horizontalAdvance(fps_text) + 20

            # Badge background
            badge_x = w - tw - 16
            badge_path = QPainterPath()
            badge_path.addRoundedRect(badge_x, 10, tw, 28, 14, 14)

            # Color based on FPS
            if self._fps >= 120:
                badge_color = QColor(0, 230, 118, 60)  # Green
                text_color = QColor(0, 230, 118)
            elif self._fps >= 60:
                badge_color = QColor(0, 212, 255, 60)  # Blue
                text_color = QColor(0, 212, 255)
            elif self._fps >= 30:
                badge_color = QColor(255, 184, 0, 60)  # Yellow
                text_color = QColor(255, 184, 0)
            else:
                badge_color = QColor(255, 59, 92, 60)  # Red
                text_color = QColor(255, 59, 92)

            painter.fillPath(badge_path, badge_color)

            # Border
            pen = QPen(text_color)
            pen.setWidthF(0.6)
            painter.setPen(pen)
            painter.drawPath(badge_path)

            # Text
            painter.setPen(text_color)
            painter.drawText(badge_x + 10, 30, fps_text)

        painter.end()

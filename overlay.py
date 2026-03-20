"""
Gaming Performance Monitor — Main Glassmorphism Overlay
A frosted-glass always-on-top performance overlay for gamers.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QApplication,
    QGraphicsDropShadowEffect, QSizeGrip, QMenu, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QLinearGradient, QIcon

from config import MonitorConfig
from monitor import SystemMonitor
from widgets import GlassCard, NetworkCard, HeaderWidget


class GlassOverlay(QWidget):
    """
    The main glassmorphism overlay window.
    Renders a frosted-glass panel with real-time metrics.
    """

    def __init__(self, config: MonitorConfig, monitor: SystemMonitor):
        super().__init__()
        self.config = config
        self.monitor = monitor
        self._drag_pos = None
        self._opacity = config.opacity

        self._setup_window()
        self._build_ui()
        self._setup_timers()
        self._setup_shortcuts()

    def _setup_window(self):
        """Configure the window to be a frameless, translucent, always-on-top overlay."""
        flags = (
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setGeometry(self.config.x, self.config.y, self.config.width, self.config.height)
        self.setMinimumSize(280, 200)

    def _build_ui(self):
        """Create all the metric cards and arrange them in a vertical layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(6)

        # Header with FPS
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        # CPU Card
        if self.config.show_cpu:
            self.cpu_card = GlassCard("CPU", "⚡")
            main_layout.addWidget(self.cpu_card)

        # GPU Card
        if self.config.show_gpu:
            self.gpu_card = GlassCard("GPU", "🎮")
            main_layout.addWidget(self.gpu_card)

        # RAM Card
        if self.config.show_ram:
            self.ram_card = GlassCard("RAM", "🧠")
            main_layout.addWidget(self.ram_card)

        # Network Card
        if self.config.show_network:
            self.net_card = NetworkCard()
            main_layout.addWidget(self.net_card)

        # Bottom spacer + size grip
        main_layout.addStretch()

        grip_layout = QHBoxLayout()
        grip_layout.addStretch()
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)
        grip_layout.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(grip_layout)

    def _setup_timers(self):
        """Start the UI refresh timer."""
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_ui)
        self.ui_timer.start(self.config.refresh_ms)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        from PyQt6.QtGui import QShortcut, QKeySequence

        QShortcut(QKeySequence("F9"), self, self._toggle_visibility)
        QShortcut(QKeySequence("F10"), self, self._cycle_opacity)
        QShortcut(QKeySequence("F11"), self, self._toggle_compact)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+R"), self, self._reset_position)

    def paintEvent(self, event):
        """
        Draw the glassmorphism background.
        Uses layered rounded rects with gradients and subtle borders
        to simulate frosted glass.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        r = 20  # corner radius

        # === Main glass panel ===
        main_path = QPainterPath()
        main_path.addRoundedRect(0, 0, w, h, r, r)

        # Dark tinted background (simulates glass tint)
        bg_color = QColor(12, 12, 20, int(255 * self._opacity * 0.75))
        painter.fillPath(main_path, bg_color)

        # === Gradient overlay (top half lighter) ===
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0, QColor(255, 255, 255, int(12 * self._opacity)))
        gradient.setColorAt(0.3, QColor(255, 255, 255, int(4 * self._opacity)))
        gradient.setColorAt(1, QColor(0, 0, 0, int(8 * self._opacity)))
        painter.fillPath(main_path, gradient)

        # === Inner highlight (top edge) ===
        highlight_path = QPainterPath()
        highlight_path.addRoundedRect(1, 1, w - 2, h * 0.35, r - 1, r - 1)
        painter.fillPath(highlight_path, QColor(255, 255, 255, int(10 * self._opacity)))

        # === Border (subtle white glow) ===
        pen = QPen(QColor(255, 255, 255, int(30 * self._opacity)))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawPath(main_path)

        # === Outer glow (shadow-like depth) ===
        outer_path = QPainterPath()
        outer_path.addRoundedRect(-1, -1, w + 2, h + 2, r + 1, r + 1)
        pen = QPen(QColor(0, 0, 0, int(40 * self._opacity)))
        pen.setWidthF(2.0)
        painter.setPen(pen)
        painter.drawPath(outer_path)

        painter.end()

    def _update_ui(self):
        """Refresh all metric cards from the system monitor."""
        snap = self.monitor.get_snapshot()

        # Header FPS
        if self.config.show_fps:
            self.header.set_fps(snap.fps.fps if snap.fps.fps > 0 else 0)

        # CPU
        if self.config.show_cpu and hasattr(self, 'cpu_card'):
            cpu = snap.cpu
            freq_str = f"{cpu.frequency_mhz / 1000:.1f} GHz" if cpu.frequency_mhz > 0 else ""
            temp_str = f"{cpu.temperature_c:.0f}°C" if cpu.temperature_c else ""
            subtitle = " | ".join(filter(None, [freq_str, temp_str]))
            color = self._bar_color(cpu.usage_percent)
            self.cpu_card.set_data(
                value=f"{cpu.usage_percent:.0f}",
                bar_value=cpu.usage_percent,
                subtitle=subtitle,
                bar_color=color,
            )

        # GPU
        if self.config.show_gpu and hasattr(self, 'gpu_card'):
            gpu = snap.gpu
            if gpu.available:
                mem_str = f"{gpu.memory_used_mb / 1024:.1f}/{gpu.memory_total_mb / 1024:.1f} GB"
                temp_str = f"{gpu.temperature_c:.0f}°C" if gpu.temperature_c else ""
                subtitle = " | ".join(filter(None, [mem_str, temp_str]))
                color = self._bar_color(gpu.usage_percent)
                self.gpu_card.set_data(
                    value=f"{gpu.usage_percent:.0f}",
                    bar_value=gpu.usage_percent,
                    subtitle=subtitle,
                    bar_color=color,
                )
            else:
                self.gpu_card.set_data(value="N/A", bar_value=0, subtitle="No GPU detected")

        # RAM
        if self.config.show_ram and hasattr(self, 'ram_card'):
            ram = snap.ram
            subtitle = f"{ram.used_gb:.1f}/{ram.total_gb:.1f} GB"
            color = self._bar_color(ram.usage_percent)
            self.ram_card.set_data(
                value=f"{ram.usage_percent:.0f}",
                bar_value=ram.usage_percent,
                subtitle=subtitle,
                bar_color=color,
            )

        # Network
        if self.config.show_network and hasattr(self, 'net_card'):
            self.net_card.set_data(snap.network.download_mbps, snap.network.upload_mbps)

    def _bar_color(self, percent: float) -> str:
        """Return a color string based on usage percentage."""
        if percent >= 90:
            return self.config.danger_color
        elif percent >= 70:
            return self.config.warning_color
        else:
            return self.config.accent_color

    # ─── Window behavior ─────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            self.config.x = self.x()
            self.config.y = self.y()
            self.config.save()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Double-click toggles compact mode."""
        self._toggle_compact()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        opacity_menu = menu.addMenu("Opacity")
        for val in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            action = opacity_menu.addAction(f"{int(val * 100)}%")
            action.setCheckable(val == self.config.opacity)
            action.triggered.connect(lambda checked, v=val: self._set_opacity(v))

        compact_action = menu.addAction("Compact Mode")
        compact_action.setCheckable(True)
        compact_action.setChecked(self.config.compact_mode)
        compact_action.triggered.connect(self._toggle_compact)

        menu.addSeparator()
        menu.addAction("Reset Position", self._reset_position)
        menu.addSeparator()
        menu.addAction("Quit", self.close)

        menu.exec(event.globalPos())

    # ─── Actions ──────────────────────────────────────────────────

    def _toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def _cycle_opacity(self):
        levels = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        try:
            idx = levels.index(self.config.opacity)
            self._set_opacity(levels[(idx + 1) % len(levels)])
        except ValueError:
            self._set_opacity(0.8)

    def _set_opacity(self, value: float):
        self.config.opacity = value
        self._opacity = value
        self.config.save()
        self.update()

    def _toggle_compact(self):
        self.config.compact_mode = not self.config.compact_mode
        self.config.save()
        # Toggle visibility of non-essential cards
        for card_name in ['cpu_card', 'gpu_card', 'ram_card', 'net_card']:
            card = getattr(self, card_name, None)
            if card:
                card.setVisible(not self.config.compact_mode)

    def _reset_position(self):
        self.move(20, 20)
        self.config.x = 20
        self.config.y = 20
        self.config.save()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.config.width = self.width()
        self.config.height = self.height()
        self.config.save()

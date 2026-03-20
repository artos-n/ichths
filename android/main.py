"""
Perf Tool — Android (Kivy)
Glassmorphism-style performance overlay for Android gaming.
"""
import os
import time
import threading
import json
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import DragBehavior

from kivy.graphics import (
    Color, RoundedRectangle, Line, Rectangle,
    PushMatrix, PopMatrix, Rotate, Ellipse
)

try:
    import psutil
except ImportError:
    psutil = None


# ─── Glassmorphism KV Layout ─────────────────────────────────────

KV = '''
<GlassCard>:
    size_hint_y: None
    height: dp(88)
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: [1, 1, 1, 0.06]
        RoundedRectangle:
            pos: [self.pos[0] + dp(1), self.pos[1] + dp(1)]
            size: [self.size[0] - dp(2), self.size[1] / 2]
            radius: [dp(13)]
        Color:
            rgba: [1, 1, 1, 0.1]
        Line:
            rounded_rectangle: [self.pos[0], self.pos[1], self.size[0], self.size[1], dp(14)]
            width: dp(0.8)

    BoxLayout:
        orientation: 'horizontal'
        padding: [dp(16), dp(12), dp(16), dp(8)]
        spacing: dp(8)

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.6

            Label:
                text: root.icon_text + '  ' + root.title
                font_size: sp(11)
                color: [1, 1, 1, 0.6]
                halign: 'left'
                text_size: self.size
                size_hint_y: 0.4

            Label:
                text: root.value_text
                font_size: sp(24)
                bold: True
                color: [1, 1, 1, 0.95]
                halign: 'left'
                text_size: self.size
                size_hint_y: 0.6

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.4

            Label:
                text: root.subtitle
                font_size: sp(9)
                color: [1, 1, 1, 0.5]
                halign: 'right'
                text_size: self.size
                size_hint_y: 0.5

    # Progress bar at bottom
    canvas.after:
        Color:
            rgba: [1, 1, 1, 0.06]
        RoundedRectangle:
            pos: [self.pos[0] + dp(16), self.pos[1] + dp(8)]
            size: [self.size[0] - dp(32), dp(5)]
            radius: [dp(2.5)]
        Color:
            rgba: root.bar_color
        RoundedRectangle:
            pos: [self.pos[0] + dp(16), self.pos[1] + dp(8)]
            size: [(self.size[0] - dp(32)) * root.bar_pct / 100, dp(5)]
            radius: [dp(2.5)]


<NetworkCard>:
    size_hint_y: None
    height: dp(64)
    canvas.before:
        Color:
            rgba: [1, 1, 1, 0.06]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: [1, 1, 1, 0.1]
        Line:
            rounded_rectangle: [self.pos[0], self.pos[1], self.size[0], self.size[1], dp(14)]
            width: dp(0.8)

    BoxLayout:
        orientation: 'horizontal'
        padding: [dp(16), dp(8)]

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: '⬇  Download'
                font_size: sp(9)
                color: [1, 1, 1, 0.55]
                halign: 'left'
                text_size: self.size
                size_hint_y: 0.45
            Label:
                text: root.dl_text
                font_size: sp(16)
                bold: True
                color: [0, 0.83, 1, 0.95]
                halign: 'left'
                text_size: self.size
                size_hint_y: 0.55

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: '⬆  Upload'
                font_size: sp(9)
                color: [1, 1, 1, 0.55]
                halign: 'left'
                text_size: self.size
                size_hint_y: 0.45
            Label:
                text: root.ul_text
                font_size: sp(16)
                bold: True
                color: [0, 0.9, 0.46, 0.95]
                halign: 'left'
                text_size: self.size
                size_hint_y: 0.55


<MonitorRoot>:
    canvas.before:
        # Dark glass background
        Color:
            rgba: [0.047, 0.047, 0.078, 0.82]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(20)]
        # Gradient top highlight
        Color:
            rgba: [1, 1, 1, 0.035]
        RoundedRectangle:
            pos: [self.pos[0] + dp(1), self.pos[1] + self.size[1] * 0.5]
            size: [self.size[0] - dp(2), self.size[1] * 0.5]
            radius: [dp(19)]
        # Border
        Color:
            rgba: [1, 1, 1, 0.08]
        Line:
            rounded_rectangle: [self.pos[0], self.pos[1], self.size[0], self.size[1], dp(20)]
            width: dp(1)
'''


Builder.load_string(KV)


# ─── Glass Card Widget ───────────────────────────────────────────

class GlassCard(BoxLayout):
    """A single metric card with glassmorphism styling."""

    title = 'CPU'
    icon_text = '⚡'
    value_text = '—'
    subtitle = ''
    bar_pct = 0.0
    bar_color = get_color_from_hex('#00D4FF')
    bg_color = [1, 1, 1, 0.06]

    def __init__(self, title='Metric', icon='', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.icon_text = icon

    def update_data(self, value, pct=0.0, subtitle='', color_hex='#00D4FF'):
        self.value_text = str(value)
        self.bar_pct = min(100, max(0, pct))
        self.subtitle = subtitle
        self.bar_color = get_color_from_hex(color_hex)


class NetworkCard(BoxLayout):
    """Network download/upload card."""

    dl_text = '0.0 Mbps'
    ul_text = '0.0 Mbps'

    def update_data(self, dl, ul):
        self.dl_text = f'{dl:.1f} Mbps'
        self.ul_text = f'{ul:.1f} Mbps'


# ─── System Monitor (Android-adapted) ────────────────────────────

class AndroidMonitor:
    """
    Lightweight system monitor for Android.
    Uses psutil for available metrics; GPU info limited on Android.
    """

    def __init__(self):
        self.cpu_percent = 0.0
        self.cpu_freq = 0.0
        self.cpu_temp = None
        self.ram_percent = 0.0
        self.ram_used_gb = 0.0
        self.ram_total_gb = 0.0
        self.dl_mbps = 0.0
        self.ul_mbps = 0.0
        self._prev_net = None
        self._prev_time = None
        self.fps = 0
        self._fps_history = []

        if psutil:
            psutil.cpu_percent(percpu=True)

    def update(self):
        if not psutil:
            return

        # CPU
        self.cpu_percent = psutil.cpu_percent()
        freq = psutil.cpu_freq()
        self.cpu_freq = freq.current if freq else 0

        # Temperature (limited on Android without root)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    if entries:
                        self.cpu_temp = entries[0].current
                        break
        except Exception:
            pass

        # RAM
        mem = psutil.virtual_memory()
        self.ram_percent = mem.percent
        self.ram_used_gb = mem.used / (1024 ** 3)
        self.ram_total_gb = mem.total / (1024 ** 3)

        # Network
        counters = psutil.net_io_counters()
        now = time.time()
        if self._prev_net and self._prev_time:
            dt = now - self._prev_time
            if dt > 0:
                self.dl_mbps = max(0, (counters.bytes_recv - self._prev_net.bytes_recv) / dt / (1024 ** 2) * 8)
                self.ul_mbps = max(0, (counters.bytes_sent - self._prev_net.bytes_sent) / dt / (1024 ** 2) * 8)
        self._prev_net = counters
        self._prev_time = now

    def report_fps(self, fps):
        self.fps = fps
        self._fps_history.append(fps)
        if len(self._fps_history) > 60:
            self._fps_history = self._fps_history[-60:]


# ─── Main Root Widget ────────────────────────────────────────────

class MonitorRoot(FloatLayout):
    """The glassmorphism overlay panel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.monitor = AndroidMonitor()

        # Scrollable content
        scroll = ScrollView(
            size_hint=(0.92, 0.88),
            pos_hint={'center_x': 0.5, 'center_y': 0.46},
            do_scroll_x=False,
            bar_color=[1, 1, 1, 0.15],
            bar_width=dp(3),
        )

        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(6),
            padding=[0, dp(4), 0, dp(12)],
        )
        content.bind(minimum_height=content.setter('height'))

        # Header
        self.header = Label(
            text='PERFORMANCE MONITOR',
            font_size=sp(9),
            color=[1, 1, 1, 0.45],
            size_hint_y=None,
            height=dp(32),
            halign='left',
        )
        content.add_widget(self.header)

        # FPS Badge
        self.fps_label = Label(
            text='🎮  — FPS',
            font_size=sp(14),
            bold=True,
            color=[0, 0.83, 1, 0.95],
            size_hint_y=None,
            height=dp(40),
            halign='left',
        )
        content.add_widget(self.fps_label)

        # CPU Card
        self.cpu_card = GlassCard('CPU', '⚡')
        content.add_widget(self.cpu_card)

        # RAM Card
        self.ram_card = GlassCard('RAM', '🧠')
        content.add_widget(self.ram_card)

        # Network Card
        self.net_card = NetworkCard()
        content.add_widget(self.net_card)

        scroll.add_widget(content)
        self.add_widget(scroll)

        # Schedule updates
        Clock.schedule_interval(self._update, 1.0)

    def _update(self, dt):
        self.monitor.update()
        m = self.monitor

        # Color helper
        def color(pct):
            if pct >= 90:
                return '#FF3B5C'
            elif pct >= 70:
                return '#FFB800'
            return '#00D4FF'

        # FPS
        fps = m.fps
        if fps >= 120:
            fps_color = [0, 0.9, 0.46, 0.95]
        elif fps >= 60:
            fps_color = [0, 0.83, 1, 0.95]
        elif fps >= 30:
            fps_color = [1, 0.72, 0, 0.95]
        else:
            fps_color = [1, 0.23, 0.36, 0.95]
        self.fps_label.text = f'🎮  {fps} FPS' if fps > 0 else '🎮  — FPS'
        self.fps_label.color = fps_color

        # CPU
        freq_str = f'{m.cpu_freq / 1000:.1f} GHz' if m.cpu_freq > 0 else ''
        temp_str = f'{m.cpu_temp:.0f}°C' if m.cpu_temp else ''
        cpu_sub = ' | '.join(filter(None, [freq_str, temp_str]))
        self.cpu_card.update_data(
            f'{m.cpu_percent:.0f}%',
            m.cpu_percent,
            cpu_sub,
            color(m.cpu_percent),
        )

        # RAM
        ram_sub = f'{m.ram_used_gb:.1f}/{m.ram_total_gb:.1f} GB'
        self.ram_card.update_data(
            f'{m.ram_percent:.0f}%',
            m.ram_percent,
            ram_sub,
            color(m.ram_percent),
        )

        # Network
        self.net_card.update_data(m.dl_mbps, m.ul_mbps)


# ─── App ─────────────────────────────────────────────────────────

class PerfToolApp(App):

    def build(self):
        self.title = 'Perf Tool'
        root = MonitorRoot()
        return root


if __name__ == '__main__':
    PerfToolApp().run()

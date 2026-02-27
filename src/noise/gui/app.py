import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.audio import SoundLoader
import pyaudio
import numpy as np
import math
from ..resources import SOUND_ALERT, FONT_SYMBOLS, FONT_TITLE
from kivy.core.text import LabelBase
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior


LabelBase.register(name="MaterialSymbols", fn_regular=str(FONT_SYMBOLS))
LabelBase.register(name="Limelight", fn_regular=str(FONT_TITLE))


class IconButton(ButtonBehavior, Label):
    pass


# --- Audio Config ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class GaugeWidget(BoxLayout):
    value = NumericProperty(0)
    threshold = NumericProperty(85)  # Default loud noise threshold

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Background arc
            Color(0.2, 0.2, 0.2, 1)
            self.bg_arc = Line(circle=(0, 0, 100, 135, 425), width=10)

            # Threshold marker (Red line)
            Color(1, 0, 0, 0.5)
            self.threshold_line = Line(circle=(0, 0, 100, 135, 135), width=5)

            # Value arc
            self.color_instr = Color(0, 0.8, 1, 1)
            self.value_arc = Line(circle=(0, 0, 100, 135, 135), width=12)

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas,
            value=self.update_canvas,
            threshold=self.update_canvas,
        )

    def update_canvas(self, *args):
        cx, cy = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.4

        self.bg_arc.circle = (cx, cy, radius, 135, 425)

        # Update Threshold Marker position
        thresh_angle = 135 + (min(self.threshold, 100) * 2.9)
        self.threshold_line.circle = (
            cx,
            cy,
            radius + 15,
            thresh_angle - 2,
            thresh_angle + 2,
        )

        # Dynamic color: Turn red if over threshold
        if self.value >= self.threshold:
            self.color_instr.rgb = (1, 0, 0)
        else:
            self.color_instr.rgb = (0, 0.8, 1)

        val_clamped = max(0, min(self.value, 100))
        end_angle = 135 + (val_clamped * 2.9)
        self.value_arc.circle = (cx, cy, radius, 135, end_angle)


class NoiseMeterApp(App):
    # App Settings
    def build_config(self, config):
        config.setdefaults("Alerts", {"threshold": 85, "enabled": True})

    def build_settings(self, settings):
        # Defines the UI for the settings panel
        settings_json = """[
            { "type": "title", "title": "Noise Alert Settings" },
            { "type": "numeric", "title": "Threshold (dB)", "desc": "Set the dB level to trigger alert", "section": "Alerts", "key": "threshold" },
            { "type": "bool", "title": "Enable Sound Alert", "desc": "Play a sound when threshold is exceeded", "section": "Alerts", "key": "enabled" }
        ]"""
        settings.add_json_panel("Alert Settings", self.config, data=settings_json)

    def build(self):
        self.alert_sound = SoundLoader.load(str(SOUND_ALERT))
        self.alert_active = False

        self.root_layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # --- Modern Header ---
        header = BoxLayout(size_hint_y=0.15)
        header.add_widget(
            Label(
                text="NOISE ALERT",
                font_name="Limelight",
                font_size="46sp",
                bold=True,
                color=(0.5, 0.5, 0.5, 1),
                size_hint_x=0.8,
            )
        )

        # 2. Use the font name we registered above
        # \ue8b8 is the 'settings' gear icon
        self.btn_settings = Button(
            text="\ue8b8",
            font_name="MaterialSymbols",
            font_size="32sp",
            size_hint=(None, None),
            size=("56dp", "56dp"),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(0.7, 0.7, 0.7, 1),
        )
        self.btn_settings.bind(on_release=self.handle_settings_release)
        header.add_widget(self.btn_settings)

        self.root_layout.add_widget(header)

        # --- Gauge and Label ---
        self.gauge = GaugeWidget()
        self.gauge.threshold = float(self.config.get("Alerts", "threshold"))
        self.root_layout.add_widget(self.gauge)

        self.label = Label(
            text="0 dB",
            font_size="54sp",
            size_hint_y=0.2,
            bold=True,
            font_name="Limelight",
            color=(0.5, 0.5, 0.5, 1),
        )
        self.root_layout.add_widget(self.label)

        # PyAudio Init
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        Clock.schedule_interval(self.update_meter, 0.05)
        return self.root_layout

    def handle_settings_release(self, instance):
        self.open_settings()

    def on_config_change(self, config, section, key, value):
        if key == "threshold":
            self.gauge.threshold = float(value)

    def update_meter(self, dt):
        try:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(samples.astype(float) ** 2))

            db = 20 * math.log10(rms) if rms > 0 else 0
            db_display = round(db, 1)

            # Update UI
            self.gauge.value = db_display
            self.label.text = f"{db_display} dB"

            # Logic for Alert
            threshold = float(self.config.get("Alerts", "threshold"))
            enabled = self.config.getboolean("Alerts", "enabled")

            if enabled and db_display >= threshold:
                self.trigger_alert()

        except Exception as e:
            print(f"Error: {e}")

    def trigger_alert(self):
        if self.alert_sound and not self.alert_active:
            self.alert_active = True
            self.alert_sound.play()
            # Allow sound to play again after 2 seconds
            Clock.schedule_once(self.reset_alert_cooldown, 2)

    def reset_alert_cooldown(self, dt):
        self.alert_active = False

    def on_stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

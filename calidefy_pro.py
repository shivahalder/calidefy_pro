import sys
import threading
import time
import requests
import json
import calendar
import os
import random
from datetime import datetime, date, timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFrame, QDialog, QLineEdit, 
                             QPushButton, QDialogButtonBox, QScrollArea, 
                             QComboBox, QTextEdit, QGraphicsDropShadowEffect,
                             QStackedWidget, QGridLayout, QFrame, QListWidget)
from PyQt6.QtCore import Qt, QRect, QMimeData, QTimer, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QDrag, QBrush, QLinearGradient

# --- 1. THEME CONFIGURATIONS ---
THEMES = {
    "Clean": {
        "bg": "#F9FAFB",
        "sidebar": "#FFFFFF",
        "card": "#FFFFFF",
        "text": "#111827",
        "text_muted": "#6B7280",
        "grid": "#E5E7EB",
        "accent": "#6366F1",
        "preview_gradient": ["#FFFFFF", "#F3F4F6"],
        "suggestion_bg": "#F3F4F6"
    },
    "Dark": {
        "bg": "#111827",
        "sidebar": "#1F2937",
        "card": "#1F2937",
        "text": "#F9FAFB",
        "text_muted": "#9CA3AF",
        "grid": "#374151",
        "accent": "#818CF8",
        "preview_gradient": ["#1F2937", "#111827"],
        "suggestion_bg": "#374151"
    },
    "Warm": {
        "bg": "#FFFBEB",
        "sidebar": "#FEF3C7",
        "card": "#FFFFFF",
        "text": "#78350F",
        "text_muted": "#B45309",
        "grid": "#FDE68A",
        "accent": "#D97706",
        "preview_gradient": ["#FEF3C7", "#FFFBEB"],
        "suggestion_bg": "#FEF3C7"
    },
    "Bold": {
        "bg": "#F3F4F6",
        "sidebar": "#111827",
        "card": "#FFFFFF",
        "text": "#111827",
        "text_muted": "#4B5563",
        "grid": "#D1D5DB",
        "accent": "#EC4899",
        "preview_gradient": ["#111827", "#EC4899"],
        "suggestion_bg": "#FCE7F3"
    }
}

TEMPLATES = [
    {"name": "Geisel Library", "icon": "📚", "color": "#4F46E5", "duration": 3.0},
    {"name": "Campus Walk", "icon": "🚶", "color": "#10B981", "duration": 0.5},
    {"name": "Price Center", "icon": "🍔", "color": "#F59E0B", "duration": 1.0},
    {"name": "RIMAC Gym", "icon": "💪", "color": "#EF4444", "duration": 1.5},
    {"name": "Lecture", "icon": "🎓", "color": "#6366F1", "duration": 1.5},
]

SETTINGS_FILE = "calidefy_settings.json"

# --- 2. BACKEND (FLASK) ---
server = Flask(__name__)
CORS(server)

@server.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    return jsonify([
        {"title": "Study @ Geisel", "start": 14.0, "end": 17.0, "reason": "Gap detected."},
        {"title": "Sunset Walk", "start": 18.0, "end": 19.0, "reason": "Clear skies."},
        {"title": "Triton Sync", "start": 10.0, "end": 11.0, "reason": "Club meeting."}
    ])

def run_flask():
    server.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# --- 3. UI COMPONENTS ---

class EditDialog(QDialog):
    def __init__(self, event_data, theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Refine Event")
        self.setFixedWidth(400)
        self.theme = theme
        layout = QVBoxLayout(self)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme['bg']}; }}
            QLabel {{ color: {theme['text']}; font-weight: bold; font-size: 12px; }}
            QLineEdit, QTextEdit, QComboBox {{ 
                background: {theme['card']}; border: 1px solid {theme['grid']}; border-radius: 8px; padding: 8px; color: {theme['text']};
            }}
        """)
        layout.addWidget(QLabel("EVENT TITLE"))
        self.title_in = QLineEdit(event_data.get('title', 'New Event'))
        layout.addWidget(self.title_in)
        h_times = QHBoxLayout()
        v_start = QVBoxLayout(); v_start.addWidget(QLabel("START (8-22)")); self.start_in = QLineEdit(str(event_data.get('start', 8.0))); v_start.addWidget(self.start_in)
        v_end = QVBoxLayout(); v_end.addWidget(QLabel("END (8-22)")); self.end_in = QLineEdit(str(event_data.get('end', 9.0))); v_end.addWidget(self.end_in)
        h_times.addLayout(v_start); h_times.addLayout(v_end)
        layout.addLayout(h_times)
        layout.addWidget(QLabel("LOCATION"))
        self.loc_in = QLineEdit(event_data.get('location', ''))
        layout.addWidget(self.loc_in)
        layout.addWidget(QLabel("PEOPLE"))
        self.people_in = QLineEdit(event_data.get('people', ''))
        layout.addWidget(self.people_in)
        layout.addWidget(QLabel("NOTES"))
        self.notes_in = QTextEdit()
        self.notes_in.setPlainText(event_data.get('notes', ''))
        self.notes_in.setFixedHeight(60)
        layout.addWidget(self.notes_in)
        self.weather_lbl = QLabel("Weather: Loading...")
        self.weather_lbl.setStyleSheet(f"color: {theme['accent']}; font-style: italic;")
        layout.addWidget(self.weather_lbl)
        self.update_weather()
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def update_weather(self):
        weathers = ["☀️ Sunny, 72°F", "☁️ Cloudy, 65°F", "🌊 Coastal Breeze, 68°F", "🌦️ Showers, 60°F"]
        self.weather_lbl.setText(f"Forecast: {random.choice(weathers)}")

    def get_data(self):
        try:
            return {
                "title": self.title_in.text(),
                "start": float(self.start_in.text()),
                "end": float(self.end_in.text()),
                "location": self.loc_in.text(),
                "people": self.people_in.text(),
                "notes": self.notes_in.toPlainText()
            }
        except: return {}

class ThemeCard(QFrame):
    selected = pyqtSignal(str)
    def __init__(self, name, config):
        super().__init__()
        self.name = name
        self.setFixedSize(220, 300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("ThemeCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        self.preview = QFrame()
        self.preview.setFixedHeight(160)
        self.preview.setStyleSheet(f"""
            border-radius: 12px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {config['preview_gradient'][0]}, stop:1 {config['preview_gradient'][1]});
            border: 1px solid {config['grid']};
        """)
        self.title = QLabel(name)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; font-weight: 900; color: #111827; margin-top: 10px;")
        layout.addWidget(self.preview)
        layout.addWidget(self.title)
        self.setStyleSheet("""
            #ThemeCard { background: white; border: 2px solid #E5E7EB; border-radius: 20px; }
            #ThemeCard:hover { border-color: #6366F1; background: #F5F3FF; }
        """)
    def mousePressEvent(self, e): self.selected.emit(self.name)

class OnboardingView(QWidget):
    themeChosen = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: white;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("Welcome to Calidefy")
        title.setStyleSheet("font-size: 48px; font-weight: 900; color: #111827; letter-spacing: -2px;")
        subtitle = QLabel("Select your visual style to get started.")
        subtitle.setStyleSheet("font-size: 18px; color: #6B7280; margin-bottom: 40px;")
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle, 0, Qt.AlignmentFlag.AlignCenter)
        grid = QHBoxLayout()
        for name, config in THEMES.items():
            card = ThemeCard(name, config)
            card.selected.connect(self.themeChosen.emit)
            grid.addWidget(card)
        layout.addLayout(grid)

class SuggestionItem(QWidget):
    def __init__(self, data, theme):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setObjectName("SuggestionItem")
        self.title = QLabel(f"<b>{data['title']}</b>")
        self.reason = QLabel(data['reason'])
        layout.addWidget(self.title)
        layout.addWidget(self.reason)
        self.title.setStyleSheet(f"color: {theme['text']}; font-size: 12px;")
        self.reason.setStyleSheet(f"color: {theme['text_muted']}; font-size: 10px; font-style: italic;")
        self.setStyleSheet(f"#SuggestionItem {{ background: {theme['suggestion_bg']}; border-radius: 10px; padding: 10px; margin-bottom: 5px; }}")

class CalendarCanvas(QWidget):
    eventsChanged = pyqtSignal()
    def __init__(self, theme):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.theme = theme
        self.events = []
        self.anytime_events = []
        self.hour_height = 100
        self.anytime_height = 80
        self.setMinimumHeight(1700)
        self.drag_start_hour = None
        self.current_drag_hour = None
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.theme['bg']))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(self.rect())
        p.setBrush(QColor(self.theme['sidebar']))
        p.setPen(QPen(QColor(self.theme['grid']), 1))
        p.drawRect(0, 0, self.width(), self.anytime_height)
        p.setPen(QColor(self.theme['text_muted']))
        p.setFont(QFont("Arial", 8, QFont.Weight.Black))
        p.drawText(15, 45, "ANYTIME")
        for i, ev in enumerate(self.anytime_events):
            rect = QRect(95 + (i * 160), 15, 150, 50)
            ev['rect'] = rect
            p.setBrush(QColor(ev.get('color', '#6366F1')))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, 10, 10)
            p.setPen(QColor("white"))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, ev.get('title', 'Event'))
        for i in range(16):
            y = i * self.hour_height + self.anytime_height
            p.setPen(QPen(QColor(self.theme['grid']), 1))
            p.drawLine(85, y, self.width(), y)
            p.setPen(QColor(self.theme['text_muted']))
            p.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            p.drawText(15, y + 22, f"{8+i}:00")
        if self.drag_start_hour is not None and self.current_drag_hour is not None:
            s, e = min(self.drag_start_hour, self.current_drag_hour), max(self.drag_start_hour, self.current_drag_hour)
            y = int((s - 8) * self.hour_height) + self.anytime_height
            h = int((e - s) * self.hour_height)
            p.setBrush(QColor(self.theme['accent']))
            p.setOpacity(0.3)
            p.drawRoundedRect(95, y, self.width() - 130, h, 12, 12)
            p.setOpacity(1.0)
        for ev in self.events:
            y = int((ev.get('start', 8) - 8) * self.hour_height) + self.anytime_height
            h = int((ev.get('end', 9) - ev.get('start', 8)) * self.hour_height)
            rect = QRect(95, y + 4, self.width() - 130, h - 8)
            ev['rect'] = rect
            p.setBrush(QColor(ev.get('color', '#6366F1')))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, 12, 12)
            p.setPen(QColor("white"))
            p.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            p.drawText(rect.adjusted(15, 15, -15, -15), Qt.AlignmentFlag.AlignTop, ev.get('title', 'Event'))

    def mousePressEvent(self, e):
        y = e.position().y()
        if y > self.anytime_height:
            self.drag_start_hour = round(((y - self.anytime_height) / self.hour_height + 8) * 4) / 4
            self.current_drag_hour = self.drag_start_hour
            self.update()

    def mouseMoveEvent(self, e):
        if self.drag_start_hour is not None:
            y = e.position().y()
            self.current_drag_hour = round(((y - self.anytime_height) / self.hour_height + 8) * 4) / 4
            self.update()

    def mouseReleaseEvent(self, e):
        if self.drag_start_hour is not None:
            s, e_h = min(self.drag_start_hour, self.current_drag_hour), max(self.drag_start_hour, self.current_drag_hour)
            if e_h - s >= 0.25:
                new_ev = {"title": "New Session", "start": s, "end": e_h, "color": self.theme['accent']}
                self.events.append(new_ev)
                self.eventsChanged.emit()
                dlg = EditDialog(new_ev, self.theme, self)
                if dlg.exec(): new_ev.update(dlg.get_data()); self.eventsChanged.emit()
            self.drag_start_hour = None
            self.current_drag_hour = None
            self.update()

    def mouseDoubleClickEvent(self, e):
        p = e.position().toPoint()
        for ev in self.events + self.anytime_events:
            if ev.get('rect') and ev['rect'].contains(p):
                dlg = EditDialog(ev, self.theme, self)
                if dlg.exec(): ev.update(dlg.get_data()); self.eventsChanged.emit(); self.update()
                return

    def dragEnterEvent(self, e): e.accept() if e.mimeData().hasText() else e.ignore()
    def dropEvent(self, e):
        try:
            data = json.loads(e.mimeData().text())
            y = e.position().y()
            if y < self.anytime_height:
                self.anytime_events.append({"title": data['name'], "color": data['color'], "rect": None})
            else:
                start = round(((y - self.anytime_height) / self.hour_height + 8) * 4) / 4
                self.events.append({"title": data['name'], "start": start, "end": start + data['duration'], "color": data['color']})
            self.eventsChanged.emit(); self.update()
        except: pass

class TemplateCard(QLabel):
    def __init__(self, t, theme):
        super().__init__(f"   {t['icon']}   {t['name']}")
        self.t, self.theme = t, theme
        self.setFixedHeight(54)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.update_style(theme)
    def update_style(self, theme):
        self.setStyleSheet(f"QLabel {{ background: {theme['card']}; color: {theme['text']}; font-weight: 700; border-radius: 12px; border: 1px solid {theme['grid']}; margin: 4px; }} QLabel:hover {{ border-color: {theme['accent']}; }}")
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self); m = QMimeData(); m.setText(json.dumps(self.t)); drag.setMimeData(m); drag.exec(Qt.DropAction.MoveAction)

class CalidefyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calidefy")
        self.resize(1280, 850)
        self.load_settings()
        self.theme = THEMES[self.current_theme_name]
        self.root_stack = QStackedWidget()
        self.setCentralWidget(self.root_stack)
        self.onboarding = OnboardingView()
        self.main_app = QWidget()
        self.root_stack.addWidget(self.onboarding)
        self.root_stack.addWidget(self.main_app)
        self.init_main_ui()
        self.onboarding.themeChosen.connect(self.complete_onboarding)
        if getattr(self, 'is_first_run', True): self.root_stack.setCurrentIndex(0)
        else: self.root_stack.setCurrentIndex(1); self.apply_theme()
        QTimer.singleShot(1000, self.fetch_suggestions)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f); self.current_theme_name = s.get("theme", "Clean"); self.is_first_run = s.get("first_run", True)
            except: self.current_theme_name, self.is_first_run = "Clean", True
        else: self.current_theme_name, self.is_first_run = "Clean", True

    def init_main_ui(self):
        layout = QHBoxLayout(self.main_app)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        self.sidebar = QFrame(); self.sidebar.setFixedWidth(260)
        self.s_layout = QVBoxLayout(self.sidebar); self.s_layout.setContentsMargins(20, 40, 20, 30)
        self.logo = QLabel("CALIDEFY"); self.s_layout.addWidget(self.logo)
        self.reminder_box = QFrame()
        rem_layout = QVBoxLayout(self.reminder_box); rem_layout.addWidget(QLabel("NEXT EVENT"))
        self.next_ev_lbl = QLabel("No events"); self.next_ev_lbl.setStyleSheet("color: white; font-weight: 900; font-size: 14px;")
        rem_layout.addWidget(self.next_ev_lbl); self.s_layout.addWidget(self.reminder_box)
        self.cat_lbl = QLabel("CATALOG"); self.s_layout.addWidget(self.cat_lbl)
        self.template_cards = []
        for t in TEMPLATES:
            c = TemplateCard(t, self.theme); self.s_layout.addWidget(c); self.template_cards.append(c)
        self.s_layout.addSpacing(20); self.ai_lbl = QLabel("AI SUGGESTIONS"); self.s_layout.addWidget(self.ai_lbl)
        self.ai_container = QVBoxLayout(); self.s_layout.addLayout(self.ai_container)
        self.s_layout.addStretch()
        self.theme_sel = QComboBox(); self.theme_sel.addItems(list(THEMES.keys())); self.theme_sel.currentTextChanged.connect(self.change_theme)
        self.s_layout.addWidget(QLabel("<b>THEME</b>")); self.s_layout.addWidget(self.theme_sel)
        content = QVBoxLayout()
        self.header = QFrame(); self.header.setFixedHeight(80)
        h_layout = QHBoxLayout(self.header); self.h_title = QLabel("TODAY"); h_layout.addWidget(self.h_title); h_layout.addStretch()
        self.tab_container = QWidget(); self.tab_layout = QHBoxLayout(self.tab_container); self.btns = {}
        for i, v in enumerate(['YEAR', 'MONTH', 'DAY']):
            b = QPushButton(v); b.setCheckable(True); b.clicked.connect(lambda ch, idx=i: self.switch_view(idx)); self.btns[v] = b; self.tab_layout.addWidget(b)
        h_layout.addWidget(self.tab_container)
        self.stack = QStackedWidget()
        self.canvas = CalendarCanvas(self.theme); self.canvas.eventsChanged.connect(self.update_reminder)
        scroll = QScrollArea(); scroll.setWidget(self.canvas); scroll.setWidgetResizable(True); scroll.setStyleSheet("border: none;")
        self.stack.addWidget(QLabel("Year View Coming Soon...")); self.stack.addWidget(QLabel("Month View Coming Soon...")); self.stack.addWidget(scroll)
        content.addWidget(self.header); content.addWidget(self.stack); layout.addWidget(self.sidebar); layout.addLayout(content)
        self.switch_view(2)

    def complete_onboarding(self, name):
        self.current_theme_name = name; self.theme = THEMES[name]
        with open(SETTINGS_FILE, 'w') as f: json.dump({"theme": name, "first_run": False}, f)
        self.apply_theme(); self.root_stack.setCurrentIndex(1)

    def change_theme(self, name): self.current_theme_name = name; self.theme = THEMES[name]; self.apply_theme()

    def apply_theme(self):
        t = self.theme
        self.sidebar.setStyleSheet(f"background: {t['sidebar']}; border-right: 1px solid {t['grid']};")
        self.header.setStyleSheet(f"background: {t['sidebar']}; border-bottom: 1px solid {t['grid']};")
        self.main_app.setStyleSheet(f"background: {t['bg']};")
        self.logo.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {t['accent']}; margin-bottom: 30px;")
        self.h_title.setStyleSheet(f"font-size: 22px; font-weight: 900; color: {t['text']};")
        self.reminder_box.setStyleSheet(f"background: {t['accent']}; border-radius: 15px; margin-bottom: 20px;")
        for c in self.template_cards: c.update_style(t)
        self.canvas.theme = t; self.canvas.update()
        self.theme_sel.setCurrentText(self.current_theme_name)

    def update_reminder(self):
        now = datetime.now(); now_h = now.hour + now.minute/60.0
        up = sorted([e for e in self.canvas.events if e.get('start', 0) > now_h], key=lambda x: x.get('start', 0))
        self.next_ev_lbl.setText(f"{up[0]['title']} @ {int(up[0]['start'])}:00" if up else "No events")

    def switch_view(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self.btns.values()): b.setChecked(i == idx)

    def fetch_suggestions(self):
        try:
            r = requests.get("http://127.0.0.1:5000/api/suggestions", timeout=1)
            if r.status_code == 200:
                for s in r.json(): self.ai_container.addWidget(SuggestionItem(s, self.theme))
        except: pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = QApplication(sys.argv); window = CalidefyApp(); window.show(); sys.exit(app.exec())

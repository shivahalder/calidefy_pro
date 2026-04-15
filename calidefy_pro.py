import sys
import threading
import time
import requests
import json
import calendar
import os
from datetime import datetime, date
from flask import Flask, jsonify
from flask_cors import CORS
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFrame, QDialog, QLineEdit, 
                             QPushButton, QDialogButtonBox, QScrollArea, 
                             QComboBox, QTextEdit, QGraphicsDropShadowEffect,
                             QStackedWidget, QGridLayout, QFrame)
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
        
        # Preview
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
        self.update_style(theme)

    def update_style(self, theme):
        self.title.setStyleSheet(f"color: {theme['text']}; font-size: 12px;")
        self.reason.setStyleSheet(f"color: {theme['text_muted']}; font-size: 10px; font-style: italic;")
        self.setStyleSheet(f"#SuggestionItem {{ background: {theme['suggestion_bg']}; border-radius: 10px; padding: 10px; margin-bottom: 5px; }}")

class CalendarCanvas(QWidget):
    def __init__(self, theme):
        super().__init__()
        self.setAcceptDrops(True)
        self.theme = theme
        self.events = []
        self.anytime_events = []
        self.hour_height = 100
        self.anytime_height = 80
        self.setMinimumHeight(1700)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.theme['bg']))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(self.rect())

        # Anytime Zone
        p.setBrush(QColor(self.theme['sidebar']))
        p.setPen(QPen(QColor(self.theme['grid']), 1))
        p.drawRect(0, 0, self.width(), self.anytime_height)
        
        p.setPen(QColor(self.theme['text_muted']))
        p.setFont(QFont("Arial", 8, QFont.Weight.Black))
        p.drawText(15, 45, "ANYTIME")
        
        for i, ev in enumerate(self.anytime_events):
            rect = QRect(95 + (i * 160), 15, 150, 50)
            ev['rect'] = rect
            p.setBrush(QColor(ev['color']))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, 10, 10)
            p.setPen(QColor("white"))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, ev['title'])

        # Grid
        for i in range(16):
            y = i * self.hour_height + self.anytime_height
            p.setPen(QPen(QColor(self.theme['grid']), 1))
            p.drawLine(85, y, self.width(), y)
            p.setPen(QColor(self.theme['text_muted']))
            p.drawText(15, y + 22, f"{8+i}:00")

        # Events
        for ev in self.events:
            y = int((ev['start'] - 8) * self.hour_height) + self.anytime_height
            h = int((ev['end'] - ev['start']) * self.hour_height)
            rect = QRect(95, y + 4, self.width() - 130, h - 8)
            ev['rect'] = rect
            p.setBrush(QColor(ev['color']))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, 12, 12)
            p.setPen(QColor("white"))
            p.drawText(rect.adjusted(15, 15, -15, -15), ev['title'])

    def dragEnterEvent(self, e): e.accept() if e.mimeData().hasText() else e.ignore()
    def dropEvent(self, e):
        try:
            data = json.loads(e.mimeData().text())
            y = e.position().y()
            if y < self.anytime_height:
                self.anytime_events.append({"title": data['name'], "color": data['color'], "rect": None})
            else:
                hour = ((y - self.anytime_height) / self.hour_height) + 8
                start = round(hour * 4) / 4
                self.events.append({"title": data['name'], "start": start, "end": start + data['duration'], "color": data['color']})
            self.update()
        except: pass

class TemplateCard(QLabel):
    def __init__(self, t, theme):
        super().__init__(f"   {t['icon']}   {t['name']}")
        self.t, self.theme = t, theme
        self.setFixedHeight(54)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.update_style(theme)

    def update_style(self, theme):
        self.theme = theme
        self.setStyleSheet(f"QLabel {{ background: {theme['card']}; color: {theme['text']}; font-weight: 700; border-radius: 12px; border: 1px solid {theme['grid']}; margin: 4px; }} QLabel:hover {{ border-color: {theme['accent']}; }}")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(json.dumps(self.t))
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)

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
        self.onboarding.themeChosen.connect(self.apply_and_save_theme)
        
        if self.is_first_run: self.root_stack.setCurrentIndex(0)
        else:
            self.root_stack.setCurrentIndex(1)
            self.apply_theme()
        
        QTimer.singleShot(1000, self.fetch_suggestions)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                s = json.load(f)
                self.current_theme_name = s.get("theme", "Clean")
                self.is_first_run = s.get("first_run", True)
        else: self.current_theme_name, self.is_first_run = "Clean", True

    def apply_and_save_theme(self, name):
        self.current_theme_name = name
        self.theme = THEMES[name]
        with open(SETTINGS_FILE, 'w') as f: json.dump({"theme": name, "first_run": False}, f)
        self.apply_theme()
        self.root_stack.setCurrentIndex(1)

    def init_main_ui(self):
        layout = QHBoxLayout(self.main_app)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.s_layout = QVBoxLayout(self.sidebar)
        self.s_layout.setContentsMargins(20, 40, 20, 30)
        
        self.logo = QLabel("CALIDEFY")
        self.s_layout.addWidget(self.logo)
        
        self.cat_lbl = QLabel("EVENT CATALOG")
        self.s_layout.addWidget(self.cat_lbl)
        
        self.template_cards = []
        for t in TEMPLATES:
            c = TemplateCard(t, self.theme)
            self.s_layout.addWidget(c)
            self.template_cards.append(c)
            
        self.s_layout.addSpacing(20)
        self.ai_lbl = QLabel("AI SUGGESTIONS")
        self.s_layout.addWidget(self.ai_lbl)
        self.ai_container = QVBoxLayout()
        self.s_layout.addLayout(self.ai_container)
        
        self.s_layout.addStretch()
        self.theme_sel = QComboBox()
        self.theme_sel.addItems(list(THEMES.keys()))
        self.theme_sel.currentTextChanged.connect(self.apply_and_save_theme)
        self.s_layout.addWidget(QLabel("<b>SETTINGS: THEME</b>"))
        self.s_layout.addWidget(self.theme_sel)
        
        content = QVBoxLayout()
        self.header = QFrame(); self.header.setFixedHeight(80)
        h_layout = QHBoxLayout(self.header)
        self.h_title = QLabel("TODAY")
        h_layout.addWidget(self.h_title)
        
        self.canvas = CalendarCanvas(self.theme)
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        content.addWidget(self.header)
        content.addWidget(scroll)
        layout.addWidget(self.sidebar)
        layout.addLayout(content)

    def apply_theme(self):
        t = self.theme
        self.sidebar.setStyleSheet(f"background: {t['sidebar']}; border-right: 1px solid {t['grid']};")
        self.header.setStyleSheet(f"background: {t['sidebar']}; border-bottom: 1px solid {t['grid']};")
        self.main_app.setStyleSheet(f"background: {t['bg']};")
        self.logo.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {t['accent']}; margin-bottom: 30px;")
        self.h_title.setStyleSheet(f"font-size: 22px; font-weight: 900; color: {t['text']};")
        self.cat_lbl.setStyleSheet(f"color: {t['text_muted']}; font-size: 10px; font-weight: 800;")
        self.ai_lbl.setStyleSheet(f"color: {t['text_muted']}; font-size: 10px; font-weight: 800;")
        for c in self.template_cards: c.update_style(t)
        self.canvas.theme = t
        self.canvas.update()
        self.theme_sel.setCurrentText(self.current_theme_name)

    def fetch_suggestions(self):
        try:
            r = requests.get("http://127.0.0.1:5000/api/suggestions", timeout=1)
            if r.status_code == 200:
                for s in r.json(): self.ai_container.addWidget(SuggestionItem(s, self.theme))
        except: pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = QApplication(sys.argv)
    window = CalidefyApp()
    window.show()
    sys.exit(app.exec())

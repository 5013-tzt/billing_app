"""
main.py - Theme System Integration
===================================
Replace your main.py with this version
"""

import sys
import os
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"
os.environ["QT_QPA_PLATFORM"] = "windows:fontengine=freetype"
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
    QPushButton, QDialog, QMessageBox, QFrame, QStackedWidget, QHBoxLayout,
    QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor

# Internal Imports
from database import get_db, init_db, get_theme_preference
from views.styles import get_theme  # Changed from STYLESHEET
from views.clients import ClientDialog
from views.invoice import InvoiceDialog
from views.settings import SettingsDialog
from views.dashboard import DashboardView
from views.invoice_list import InvoiceListDialog

class Login(QDialog):
    def __init__(self, stylesheet):
        super().__init__()
        self.setFixedSize(350, 450)
        self.setStyleSheet(stylesheet)  # Use passed stylesheet
        conn = get_db()
        self.s = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
        conn.close()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        t = QLabel(self.s['admin_name'] if self.s and self.s['admin_name'] else "LOGIN")
        t.setStyleSheet("font-size: 18px; color: #2563EB; font-weight: bold;")
        layout.addWidget(t)
        
        self.u = QLineEdit()
        self.u.setPlaceholderText("Username")
        self.p = QLineEdit()
        self.p.setPlaceholderText("Password")
        self.p.setEchoMode(QLineEdit.Password)
        b = QPushButton("LOGIN")
        b.setFixedHeight(40)
        b.clicked.connect(self.handle)
        
        layout.addWidget(self.u)
        layout.addWidget(self.p)
        layout.addWidget(b)

    def handle(self):
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM settings WHERE admin_user=? AND password=?", 
            (self.u.text(), self.p.text())
        ).fetchone()
        conn.close()
        if row:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

class MainWindow(QMainWindow):
    def __init__(self, stylesheet):
        super().__init__()
        self.setWindowTitle("Billing System")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(stylesheet)  # Use passed stylesheet
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)
        
        title_label = QLabel("📊 Billing System")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 15px; color: #2563EB;")
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        # Navigation Buttons
        nav_data = [
            ("🏠 Dashboard", self.show_dashboard),
            ("👥 Clients", self.open_clients),
            ("📄 Create Invoice", self.open_invoice),
            ("📋 Invoice List", self.open_invoice_list),
            ("⚙️ Settings", self.open_settings),
        ]
        
        for text, func in nav_data:
            btn = QPushButton(text)
            btn.setObjectName("NavBtn")
            btn.setFixedHeight(45)
            btn.clicked.connect(func)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("NavBtn")
        logout_btn.setFixedHeight(45)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        # Content Area
        self.stacked = QStackedWidget()
        self.dashboard = DashboardView()
        self.stacked.addWidget(self.dashboard)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked)
    
    def show_dashboard(self):
        self.stacked.setCurrentWidget(self.dashboard)
    
    def open_clients(self):
        ClientDialog(self).exec()
    
    def open_invoice(self):
        InvoiceDialog(self).exec()
    
    def open_invoice_list(self):
        InvoiceListDialog(self).exec()
    
    def open_settings(self):
        SettingsDialog(self).exec()
    
    def logout(self):
        self.close()


def main():
    # Initialize database first
    init_db()
    
    # Get user's theme preference
    theme_name = get_theme_preference()
    theme = get_theme(theme_name)
    stylesheet = theme.get_stylesheet()
    
    # Create application
    app = QApplication(sys.argv)

    # ── Force Light Mode (OS dark mode ကို override လုပ်မယ်) ──────────
    light_palette = QPalette()
    light_palette.setColor(QPalette.Window,          QColor(255, 255, 255))
    light_palette.setColor(QPalette.WindowText,      QColor(26,  26,  26))
    light_palette.setColor(QPalette.Base,            QColor(255, 255, 255))
    light_palette.setColor(QPalette.AlternateBase,   QColor(250, 250, 250))
    light_palette.setColor(QPalette.ToolTipBase,     QColor(255, 255, 255))
    light_palette.setColor(QPalette.ToolTipText,     QColor(26,  26,  26))
    light_palette.setColor(QPalette.Text,            QColor(26,  26,  26))
    light_palette.setColor(QPalette.Button,          QColor(240, 240, 240))
    light_palette.setColor(QPalette.ButtonText,      QColor(26,  26,  26))
    light_palette.setColor(QPalette.BrightText,      QColor(255, 0,   0))
    light_palette.setColor(QPalette.Link,            QColor(37,  99,  235))
    light_palette.setColor(QPalette.Highlight,       QColor(37,  99,  235))
    light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    light_palette.setColor(QPalette.Mid,             QColor(200, 200, 200))
    light_palette.setColor(QPalette.Shadow,          QColor(150, 150, 150))
    light_palette.setColor(QPalette.Dark,            QColor(180, 180, 180))
    light_palette.setColor(QPalette.Midlight,        QColor(230, 230, 230))
    # Disabled state
    light_palette.setColor(QPalette.Disabled, QPalette.Text,       QColor(170, 170, 170))
    light_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(170, 170, 170))
    light_palette.setColor(QPalette.Disabled, QPalette.Base,       QColor(245, 245, 245))
    app.setPalette(light_palette)
    # ─────────────────────────────────────────────────────────────────
    
    # Apply global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Show login dialog with theme
    login = Login(stylesheet)
    if login.exec() == QDialog.Accepted:
        # Show main window with theme
        window = MainWindow(stylesheet)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == '__main__':
    main()
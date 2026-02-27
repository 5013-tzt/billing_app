"""
main.py - Professional Billing System with Dashboard
=====================================================
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
from views.styles import get_theme
from views.clients import ClientDialog
from views.invoice import InvoiceDialog
from views.settings import SettingsDialog
from views.dashboard import Dashboard  # ✅ NEW: Professional Dashboard
from views.invoice_list import InvoiceListDialog


class Login(QDialog):
    """Login Dialog"""
    def __init__(self, stylesheet):
        super().__init__()
        self.setFixedSize(400, 500)
        self.setWindowTitle("🔐 Login")
        self.setStyleSheet(stylesheet)
        
        # Get admin info from database
        conn = get_db()
        self.settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
        conn.close()
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo/Title
        title_label = QLabel("💼 BILLING SYSTEM")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2563EB; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        if self.settings and self.settings['admin_name']:
            subtitle = QLabel(f"Welcome, {self.settings['admin_name']}")
        else:
            subtitle = QLabel("Please login to continue")
        subtitle.setStyleSheet("color: #666; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold; margin-top: 10px;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(20)
        
        # Login Button
        login_btn = QPushButton("🔓 LOGIN")
        login_btn.setFixedHeight(50)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        layout.addStretch()
    
    def handle_login(self):
        """Handle login authentication"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "❌ Error", "Please enter both username and password!")
            return
        
        try:
            conn = get_db()
            row = conn.execute(
                "SELECT * FROM settings WHERE admin_user=? AND password=?", 
                (username, password)
            ).fetchone()
            conn.close()
            
            if row:
                self.accept()
            else:
                QMessageBox.warning(self, "❌ Login Failed", "Invalid username or password!")
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login error: {str(e)}")


class MainWindow(QMainWindow):
    """Main Application Window with Dashboard"""
    def __init__(self, stylesheet):
        super().__init__()
        self.setWindowTitle("💼 Professional Billing System")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(stylesheet)
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ═══════════════════════════════════════════════════════════
        # SIDEBAR
        # ═══════════════════════════════════════════════════════════
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame#Sidebar {
                background-color: palette(window);
                border-right: 1px solid palette(mid);
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)
        
        # App Title
        title_label = QLabel("💼 Billing System")
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            padding: 15px; 
            color: #2563EB;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        sidebar_layout.addSpacing(20)
        
        # Navigation Buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("👥 Clients", self.open_clients),
            ("📄 New Invoice", self.open_new_invoice),
            ("📋 Invoice List", self.open_invoice_list),
            ("⚙️ Settings", self.open_settings),
        ]
        
        for text, func in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName("NavBtn")
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton#NavBtn {
                    text-align: left;
                    padding-left: 20px;
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                    border-radius: 0px;
                    background-color: transparent;
                }
                QPushButton#NavBtn:hover {
                    background-color: #e0e7ff;
                    color: #2563EB;
                }
                QPushButton#NavBtn:pressed {
                    background-color: #c7d2fe;
                }
            """)
            btn.clicked.connect(func)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Version Info
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #999; font-size: 10px; padding: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        # Logout Button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("NavBtn")
        logout_btn.setFixedHeight(50)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton#NavBtn {
                text-align: left;
                padding-left: 20px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                background-color: transparent;
                color: #ef4444;
            }
            QPushButton#NavBtn:hover {
                background-color: #fee2e2;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        # ═══════════════════════════════════════════════════════════
        # CONTENT AREA (Stacked Widget)
        # ═══════════════════════════════════════════════════════════
        self.content_stack = QStackedWidget()
        
        # ✅ Create Dashboard
        self.dashboard_page = Dashboard()
        self.dashboard_page.new_invoice_clicked.connect(self.open_new_invoice)
        self.dashboard_page.new_client_clicked.connect(self.open_clients)
        self.dashboard_page.view_invoice_clicked.connect(self.open_invoice_for_edit)
        self.content_stack.addWidget(self.dashboard_page)
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)
    
    def show_dashboard(self):
        """Show dashboard and refresh data"""
        self.content_stack.setCurrentWidget(self.dashboard_page)
        self.dashboard_page.load_dashboard_data()
    
    def open_clients(self):
        """Open clients management dialog"""
        dialog = ClientDialog(self)
        dialog.exec()
        # Refresh dashboard after closing
        self.dashboard_page.load_dashboard_data()
    
    def open_new_invoice(self):
        """Open new invoice dialog"""
        dialog = InvoiceDialog(self)
        dialog.exec()
        # Refresh dashboard after closing
        self.dashboard_page.load_dashboard_data()
    
    def open_invoice_for_edit(self, invoice_id):
        """Open invoice in edit mode"""
        dialog = InvoiceDialog(self, invoice_id=invoice_id, mode='edit')
        dialog.exec()
        # Refresh dashboard after closing
        self.dashboard_page.load_dashboard_data()
    
    def open_invoice_list(self):
        """Open invoice list dialog"""
        dialog = InvoiceListDialog(self)
        dialog.exec()
        # Refresh dashboard after closing
        self.dashboard_page.load_dashboard_data()
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()
        self.dashboard_page.load_dashboard_data()
    
    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            "🚪 Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()


def main():
    """Main application entry point"""
    # Initialize database
    init_db()
    
    # Get user's theme preference
    theme_name = get_theme_preference()
    theme = get_theme(theme_name)
    stylesheet = theme.get_stylesheet()
    
    # Create application
    app = QApplication(sys.argv)
    
    # ══════════════════════════════════════════════════════════════
    # Force Light Mode (Override OS dark mode if needed)
    # ══════════════════════════════════════════════════════════════
    if theme_name == 'light':
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
    
    # Apply global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Show login dialog
    login = Login(stylesheet)
    if login.exec() == QDialog.Accepted:
        # Show main window
        window = MainWindow(stylesheet)
        window.showMaximized()  # Start maximized
        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == '__main__':
    main()
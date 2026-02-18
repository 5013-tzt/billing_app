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
from PySide6.QtGui import QPixmap, QFont

# Internal Imports
from database import get_db, init_db
from views.styles import STYLESHEET
from views.clients import ClientDialog
from views.invoice import InvoiceDialog
from views.settings import SettingsDialog
from views.dashboard import DashboardView
from views.invoice_list import InvoiceListDialog  # Invoice List ကိုထည့်

class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(350, 450)
        self.setStyleSheet(STYLESHEET)
        conn = get_db()
        self.s = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
        conn.close()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        t = QLabel(self.s['company_name'] if self.s else "LOGIN")
        t.setStyleSheet("font-size: 18px; color: #BB86FC;")
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
        if self.s and self.u.text() == self.s['admin_user'] and self.p.text() == self.s['password']:
            self.accept()
        else:
            QMessageBox.warning(self, "No", "Wrong Access")

class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle(f"{settings['company_name']} Suite")
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        
        cw = QWidget()
        self.setCentralWidget(cw)
        l = QHBoxLayout(cw)
        l.setContentsMargins(0,0,0,0)
        
        # Sidebar
        sb = QFrame()
        sb.setObjectName("Sidebar")
        sb.setFixedWidth(220)
        sl = QVBoxLayout(sb)
        
        if settings['logo'] and os.path.exists(settings['logo']):
            logo = QLabel()
            logo.setPixmap(QPixmap(settings['logo']).scaled(80,80, Qt.KeepAspectRatio))
            logo.setAlignment(Qt.AlignCenter)
            sl.addWidget(logo)
            
        self.b1 = QPushButton("  🏠  Dashboard")
        self.b2 = QPushButton("  📑  New Invoice")
        self.b3 = QPushButton("  👥  Clients")
        self.b4 = QPushButton("  📋  Invoice List")  # Invoice List ကိုထည့်
        self.b5 = QPushButton("  ⚙️  Settings")      # Settings ကိုအောက်ဆုံးမှာထား
        
        buttons = [self.b1, self.b2, self.b3, self.b4, self.b5]
        for b in buttons:
            b.setObjectName("NavBtn")
            b.setFixedHeight(45)
            sl.addWidget(b)
            
        sl.addStretch()
        l.addWidget(sb)
        
        # Stacked Widget
        self.stk = QStackedWidget()
        self.dashboard = DashboardView(settings['company_name'])
        self.stk.addWidget(self.dashboard)
        l.addWidget(self.stk)
        
        # Connections
        self.b1.clicked.connect(lambda: self.stk.setCurrentIndex(0))
        self.b2.clicked.connect(lambda: InvoiceDialog(self).exec())
        self.b3.clicked.connect(lambda: ClientDialog(self).exec())
        self.b4.clicked.connect(self.show_invoice_list)  # Invoice List
        self.b5.clicked.connect(self.open_settings)      # Settings

    def show_invoice_list(self):
        """Invoice List dialog ကိုဖွင့်မယ်"""
        dialog = InvoiceListDialog(self)
        dialog.exec()

    def open_settings(self):
        if SettingsDialog(self).exec() == QDialog.Accepted:
            pass

if __name__ == "__main__":
    init_db()
    
    app = QApplication(sys.argv)
    
    if Login().exec() == QDialog.Accepted:
        conn = get_db()
        s = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
        conn.close()
        w = MainWindow(s)
        w.show()
        sys.exit(app.exec())
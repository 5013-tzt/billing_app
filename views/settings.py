import os
import shutil
import time
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QGroupBox, QGridLayout,
    QLineEdit, QTextEdit, QLabel, QPushButton, QFrame, QFileDialog, QComboBox,
    QMessageBox, QTabWidget, QCheckBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from database import get_db
from .styles import STYLESHEET

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Company Settings")
        self.resize(650, 750)
        self.setStyleSheet(STYLESHEET)
        self.current_company_id = None
        self.logo_path = ""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        self.company_tab = QWidget()
        self.setup_company_tab()
        self.tab_widget.addTab(self.company_tab, "🏢 Companies")
        
        self.security_tab = QWidget()
        self.setup_security_tab()
        self.tab_widget.addTab(self.security_tab, "🔐 Security")
        
        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Company")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setFixedWidth(150)
        self.save_btn.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white;
                          font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #059669; }
        """)
        self.save_btn.clicked.connect(self.save_company)
        
        self.delete_btn = QPushButton("🗑️ Delete Company")
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setFixedWidth(150)
        self.delete_btn.setStyleSheet("""
            QPushButton { background-color: #ef4444; color: white;
                          font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #dc2626; }
        """)
        self.delete_btn.clicked.connect(self.delete_company)
        
        self.new_btn = QPushButton("➕ New Company")
        self.new_btn.setFixedHeight(40)
        self.new_btn.setFixedWidth(150)
        self.new_btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white;
                          font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.new_btn.clicked.connect(self.new_company)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.new_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        self.load_companies()

    def setup_company_tab(self):
        layout = QVBoxLayout(self.company_tab)
        layout.setSpacing(10)
        
        # Company selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Company:"))
        self.company_selector = QComboBox()
        self.company_selector.setMinimumWidth(250)
        self.company_selector.currentIndexChanged.connect(self.on_company_selected)
        selector_layout.addWidget(self.company_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        form_layout = QVBoxLayout(content)
        form_layout.setSpacing(12)
        
        # ── Company Info ──────────────────────────────────────────────────
        info_group = QGroupBox("Company Information")
        info_grid = QGridLayout(info_group)
        info_grid.setSpacing(8)
        
        info_grid.addWidget(QLabel("Company Name:"), 0, 0)
        self.m_name = QLineEdit()
        self.m_name.setPlaceholderText("Enter company name...")
        info_grid.addWidget(self.m_name, 0, 1)
        
        info_grid.addWidget(QLabel("Short Code:"), 1, 0)
        self.m_code = QLineEdit()
        self.m_code.setPlaceholderText("e.g., ABC")
        self.m_code.setMaxLength(10)
        info_grid.addWidget(self.m_code, 1, 1)
        
        info_grid.addWidget(QLabel("Phone:"), 2, 0)
        self.m_ph = QLineEdit()
        info_grid.addWidget(self.m_ph, 2, 1)
        
        info_grid.addWidget(QLabel("Email:"), 3, 0)
        self.m_em = QLineEdit()
        info_grid.addWidget(self.m_em, 3, 1)
        
        info_grid.addWidget(QLabel("Address:"), 4, 0)
        self.m_ad = QTextEdit()
        self.m_ad.setFixedHeight(55)
        info_grid.addWidget(self.m_ad, 4, 1)
        
        info_grid.addWidget(QLabel("Tax Number:"), 5, 0)
        self.m_tax = QLineEdit()
        self.m_tax.setPlaceholderText("Business tax ID")
        info_grid.addWidget(self.m_tax, 5, 1)
        
        form_layout.addWidget(info_group)
        
        # ── Payment Details (NEW) ─────────────────────────────────────────
        payment_group = QGroupBox("💳 Payment Details  (Invoice footer မှာပြမည်)")
        payment_grid = QGridLayout(payment_group)
        payment_grid.setSpacing(8)
        
        payment_grid.addWidget(QLabel("Bank Name:"), 0, 0)
        self.m_bank = QLineEdit()
        self.m_bank.setPlaceholderText("e.g., KBZ Bank")
        payment_grid.addWidget(self.m_bank, 0, 1)
        
        payment_grid.addWidget(QLabel("Beneficiary:"), 1, 0)
        self.m_beneficiary = QLineEdit()
        self.m_beneficiary.setPlaceholderText("Account holder name")
        payment_grid.addWidget(self.m_beneficiary, 1, 1)
        
        payment_grid.addWidget(QLabel("Account No:"), 2, 0)
        self.m_account_no = QLineEdit()
        self.m_account_no.setPlaceholderText("Bank account number")
        payment_grid.addWidget(self.m_account_no, 2, 1)
        
        payment_grid.addWidget(QLabel("KPay No:"), 3, 0)
        self.m_kpay = QLineEdit()
        self.m_kpay.setPlaceholderText("KPay phone number")
        payment_grid.addWidget(self.m_kpay, 3, 1)
        
        form_layout.addWidget(payment_group)
        
        # ── Logo ──────────────────────────────────────────────────────────
        logo_group = QGroupBox("Company Logo")
        logo_layout = QHBoxLayout(logo_group)
        logo_layout.setSpacing(15)
        
        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(80, 80)
        self.logo_lbl.setStyleSheet("border: 1px solid #333; border-radius: 4px;")
        self.logo_lbl.setAlignment(Qt.AlignCenter)
        self.logo_lbl.setText("No Logo")
        self.logo_lbl.setScaledContents(True)
        logo_layout.addWidget(self.logo_lbl)
        
        logo_btn_layout = QVBoxLayout()
        self.upload_btn = QPushButton("📁 Upload Logo")
        self.upload_btn.setFixedHeight(32)
        self.upload_btn.clicked.connect(self.upload_logo)
        logo_btn_layout.addWidget(self.upload_btn)
        
        self.clear_logo_btn = QPushButton("🗑️ Clear Logo")
        self.clear_logo_btn.setFixedHeight(32)
        self.clear_logo_btn.clicked.connect(self.clear_logo)
        logo_btn_layout.addWidget(self.clear_logo_btn)
        
        logo_layout.addLayout(logo_btn_layout)
        logo_layout.addStretch()
        form_layout.addWidget(logo_group)
        
        # ── Default ───────────────────────────────────────────────────────
        default_group = QGroupBox("Default Settings")
        default_layout = QHBoxLayout(default_group)
        self.is_default = QCheckBox("Set as Default Company")
        default_layout.addWidget(self.is_default)
        default_layout.addStretch()
        form_layout.addWidget(default_group)
        
        form_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def setup_security_tab(self):
        layout = QVBoxLayout(self.security_tab)
        group = QGroupBox("User Settings")
        grid = QGridLayout(group)
        grid.setSpacing(10)
        
        grid.addWidget(QLabel("Display Name:"), 0, 0)
        self.u_display = QLineEdit()
        grid.addWidget(self.u_display, 0, 1)
        
        grid.addWidget(QLabel("Username:"), 1, 0)
        self.u_login = QLineEdit()
        grid.addWidget(self.u_login, 1, 1)
        
        grid.addWidget(QLabel("Password:"), 2, 0)
        self.u_pass = QLineEdit()
        self.u_pass.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.u_pass, 2, 1)
        
        layout.addWidget(group)
        layout.addStretch()

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            if not os.path.exists("assets"):
                os.makedirs("assets")
            timestamp = str(int(time.time()))
            ext = os.path.splitext(file_path)[1]
            new_filename = f"assets/company_{self.current_company_id or 'new'}_{timestamp}{ext}"
            shutil.copy(file_path, new_filename)
            self.logo_path = new_filename
            pixmap = QPixmap(new_filename)
            if not pixmap.isNull():
                self.logo_lbl.setPixmap(pixmap)
            else:
                QMessageBox.warning(self, "Error", "Invalid image file!")

    def clear_logo(self):
        self.logo_path = ""
        self.logo_lbl.clear()
        self.logo_lbl.setText("No Logo")

    def load_companies(self):
        try:
            conn = get_db()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, code TEXT, phone TEXT, email TEXT,
                    address TEXT, tax_number TEXT, logo TEXT,
                    is_default INTEGER DEFAULT 0,
                    bank_name TEXT DEFAULT '', beneficiary TEXT DEFAULT '',
                    account_no TEXT DEFAULT '', kpay_no TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_name TEXT, admin_user TEXT, password TEXT
                )
            ''')
            settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
            if not settings:
                conn.execute('''INSERT INTO settings (id, admin_name, admin_user, password)
                                VALUES (1, 'Administrator', 'admin', 'admin')''')
            conn.commit()
            
            companies = conn.execute(
                "SELECT * FROM companies ORDER BY is_default DESC, name"
            ).fetchall()
            conn.close()
            
            self.company_selector.clear()
            self.company_selector.addItem("Select a company...", None)
            for company in companies:
                name = company['name'] + (" (Default)" if company['is_default'] else "")
                self.company_selector.addItem(name, company['id'])
            
            if companies:
                default_id = next((c['id'] for c in companies if c['is_default']), None)
                idx = self.company_selector.findData(default_id) if default_id else 1
                self.company_selector.setCurrentIndex(max(idx, 1))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load companies: {str(e)}")

    def on_company_selected(self, index):
        company_id = self.company_selector.itemData(index)
        if company_id:
            self.current_company_id = company_id
            self.load_company_details(company_id)
            self.save_btn.setText("💾 Update Company")
            self.delete_btn.setEnabled(True)
        else:
            self.clear_form()
            self.save_btn.setText("💾 Save Company")
            self.delete_btn.setEnabled(False)

    def load_company_details(self, company_id):
        try:
            conn = get_db()
            company = conn.execute(
                "SELECT * FROM companies WHERE id=?", (company_id,)
            ).fetchone()
            
            # Security settings
            sec = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
            conn.close()
            
            if company:
                self.m_name.setText(company['name'] or "")
                self.m_code.setText(company['code'] or "")
                self.m_ph.setText(company['phone'] or "")
                self.m_em.setText(company['email'] or "")
                self.m_ad.setText(company['address'] or "")
                self.m_tax.setText(company['tax_number'] or "")
                self.is_default.setChecked(company['is_default'] == 1)
                
                # Payment details
                self.m_bank.setText(company['bank_name'] or "")
                self.m_beneficiary.setText(company['beneficiary'] or "")
                self.m_account_no.setText(company['account_no'] or "")
                self.m_kpay.setText(company['kpay_no'] or "")
                
                # Logo
                self.logo_path = company['logo'] or ""
                if self.logo_path and os.path.exists(self.logo_path):
                    pixmap = QPixmap(self.logo_path)
                    if not pixmap.isNull():
                        self.logo_lbl.setPixmap(pixmap)
                        return
                self.logo_lbl.clear()
                self.logo_lbl.setText("No Logo")
            
            if sec:
                self.u_display.setText(sec['admin_name'] or "")
                self.u_login.setText(sec['admin_user'] or "")
                # Password field ကို blank ထားမယ် — ပြောင်းချင်မှ ဖြည့်ရမယ်
                self.u_pass.clear()
                self.u_pass.setPlaceholderText("Leave blank to keep current password")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load details: {str(e)}")

    def clear_form(self):
        self.current_company_id = None
        for w in [self.m_name, self.m_code, self.m_ph, self.m_em,
                  self.m_tax, self.m_bank, self.m_beneficiary,
                  self.m_account_no, self.m_kpay]:
            w.clear()
        self.m_ad.clear()
        self.is_default.setChecked(False)
        self.clear_logo()

    def new_company(self):
        self.clear_form()
        self.company_selector.setCurrentIndex(0)
        self.save_btn.setText("💾 Save Company")
        self.delete_btn.setEnabled(False)

    def save_company(self):
        if not self.m_name.text().strip():
            QMessageBox.warning(self, "Error", "Company name is required!")
            return
        try:
            conn = get_db()
            if self.is_default.isChecked():
                conn.execute("UPDATE companies SET is_default = 0")
            
            fields = (
                self.m_name.text().strip(),
                self.m_code.text().strip(),
                self.m_ph.text().strip(),
                self.m_em.text().strip(),
                self.m_ad.toPlainText().strip(),
                self.m_tax.text().strip(),
                self.logo_path,
                1 if self.is_default.isChecked() else 0,
                self.m_bank.text().strip(),
                self.m_beneficiary.text().strip(),
                self.m_account_no.text().strip(),
                self.m_kpay.text().strip(),
            )
            
            if self.current_company_id:
                conn.execute('''
                    UPDATE companies SET
                        name=?, code=?, phone=?, email=?, address=?,
                        tax_number=?, logo=?, is_default=?,
                        bank_name=?, beneficiary=?, account_no=?, kpay_no=?
                    WHERE id=?
                ''', (*fields, self.current_company_id))
                message = "Company updated successfully!"
            else:
                conn.execute('''
                    INSERT INTO companies
                        (name, code, phone, email, address, tax_number, logo, is_default,
                         bank_name, beneficiary, account_no, kpay_no)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', fields)
                message = "Company added successfully!"
            
            # Security settings save
            # Password blank ဆိုရင် မပြောင်းဘဲထား
            new_pass = self.u_pass.text().strip()
            if new_pass:
                conn.execute('''
                    UPDATE settings SET admin_name=?, admin_user=?, password=? WHERE id=1
                ''', (
                    self.u_display.text().strip(),
                    self.u_login.text().strip(),
                    new_pass
                ))
            elif self.u_display.text().strip() or self.u_login.text().strip():
                # username/display ပဲပြောင်းမယ်၊ password မထိဘူး
                conn.execute('''
                    UPDATE settings SET admin_name=?, admin_user=? WHERE id=1
                ''', (
                    self.u_display.text().strip(),
                    self.u_login.text().strip(),
                ))
            
            conn.commit()
            conn.close()
            QMessageBox.information(self, "✅ Success", message)
            self.load_companies()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")

    def delete_company(self):
        if not self.current_company_id:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {self.m_name.text()}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                conn = get_db()
                conn.execute("DELETE FROM companies WHERE id=?", (self.current_company_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "✅ Success", "Company deleted!")
                self.load_companies()
                self.new_company()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")
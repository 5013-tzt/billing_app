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
from database import get_db, get_theme_preference, set_theme_preference
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
        
        self.appearance_tab = QWidget()
        self.setup_appearance_tab()
        self.tab_widget.addTab(self.appearance_tab, "🎨 Appearance")
        
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
        
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.load_companies()

    def setup_company_tab(self):
        """Company management tab"""
        layout = QVBoxLayout(self.company_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Company selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Company:"))
        self.company_combo = QComboBox()
        self.company_combo.setFixedHeight(35)
        self.company_combo.currentIndexChanged.connect(self.load_company_details)
        selector_layout.addWidget(self.company_combo, 1)
        layout.addLayout(selector_layout)
        
        # Scroll area for company details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        # Basic Info
        basic_group = QGroupBox("📋 Basic Information")
        basic_grid = QGridLayout(basic_group)
        basic_grid.setSpacing(10)
        
        basic_grid.addWidget(QLabel("Company Name:"), 0, 0)
        self.m_name = QLineEdit()
        self.m_name.setPlaceholderText("Company legal name")
        basic_grid.addWidget(self.m_name, 0, 1)
        
        basic_grid.addWidget(QLabel("Code:"), 1, 0)
        self.m_code = QLineEdit()
        self.m_code.setPlaceholderText("Short code (e.g., MDS)")
        basic_grid.addWidget(self.m_code, 1, 1)
        
        scroll_layout.addWidget(basic_group)
        
        # Contact Info
        contact_group = QGroupBox("📞 Contact Information")
        contact_grid = QGridLayout(contact_group)
        contact_grid.setSpacing(10)
        
        contact_grid.addWidget(QLabel("Phone:"), 0, 0)
        self.m_phone = QLineEdit()
        self.m_phone.setPlaceholderText("+95 9 xxx xxx xxx")
        contact_grid.addWidget(self.m_phone, 0, 1)
        
        contact_grid.addWidget(QLabel("Email:"), 1, 0)
        self.m_email = QLineEdit()
        self.m_email.setPlaceholderText("info@company.com")
        contact_grid.addWidget(self.m_email, 1, 1)
        
        contact_grid.addWidget(QLabel("Address:"), 2, 0)
        self.m_addr = QTextEdit()
        self.m_addr.setPlaceholderText("Full address")
        self.m_addr.setMaximumHeight(80)
        contact_grid.addWidget(self.m_addr, 2, 1)
        
        scroll_layout.addWidget(contact_group)
        
        # Tax & Logo
        tax_group = QGroupBox("🏛️ Tax & Branding")
        tax_grid = QGridLayout(tax_group)
        tax_grid.setSpacing(10)
        
        tax_grid.addWidget(QLabel("Tax Number:"), 0, 0)
        self.m_tax = QLineEdit()
        self.m_tax.setPlaceholderText("Tax identification number")
        tax_grid.addWidget(self.m_tax, 0, 1)
        
        tax_grid.addWidget(QLabel("Logo:"), 1, 0)
        logo_layout = QHBoxLayout()
        self.m_logo_label = QLabel("No logo selected")
        self.m_logo_label.setStyleSheet("padding: 5px; border: 1px solid #333;")
        logo_layout.addWidget(self.m_logo_label)
        logo_btn = QPushButton("Browse...")
        logo_btn.clicked.connect(self.browse_logo)
        logo_layout.addWidget(logo_btn)
        tax_grid.addLayout(logo_layout, 1, 1)
        
        scroll_layout.addWidget(tax_group)
        
        # Payment Details
        payment_group = QGroupBox("💳 Payment Details")
        payment_grid = QGridLayout(payment_group)
        payment_grid.setSpacing(10)
        
        payment_grid.addWidget(QLabel("Bank Name:"), 0, 0)
        self.m_bank = QLineEdit()
        self.m_bank.setPlaceholderText("Bank name (e.g., KBZ Bank)")
        payment_grid.addWidget(self.m_bank, 0, 1)
        
        payment_grid.addWidget(QLabel("Beneficiary:"), 1, 0)
        self.m_beneficiary = QLineEdit()
        self.m_beneficiary.setPlaceholderText("Account holder name")
        payment_grid.addWidget(self.m_beneficiary, 1, 1)
        
        payment_grid.addWidget(QLabel("Account No:"), 2, 0)
        self.m_account_no = QLineEdit()
        self.m_account_no.setPlaceholderText("Bank account number")
        payment_grid.addWidget(self.m_account_no, 2, 1)
        
        payment_grid.addWidget(QLabel("KPay:"), 3, 0)
        self.m_kpay = QLineEdit()
        self.m_kpay.setPlaceholderText("KPay phone number")
        payment_grid.addWidget(self.m_kpay, 3, 1)
        
        scroll_layout.addWidget(payment_group)
        
        # Default checkbox
        self.m_default = QCheckBox("Set as default company")
        scroll_layout.addWidget(self.m_default)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

    def setup_security_tab(self):
        """Security settings tab"""
        layout = QVBoxLayout(self.security_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        sec_group = QGroupBox("🔐 Login Credentials")
        grid = QGridLayout(sec_group)
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
        
        layout.addWidget(sec_group)
        layout.addStretch()
        
        self.load_security()

    def setup_appearance_tab(self):
        """Appearance settings - Theme selection"""
        layout = QVBoxLayout(self.appearance_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Theme Selection GroupBox
        theme_group = QGroupBox("🎨 Theme")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(15)
        
        # Current theme label
        current_label = QLabel("Select your preferred color theme:")
        current_label.setStyleSheet("font-size: 13px; color: #888;")
        theme_layout.addWidget(current_label)
        
        # Theme options
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("🌙 Dark Theme", "dark")
        self.theme_combo.addItem("☀️ Light Theme", "light")
        self.theme_combo.setFixedHeight(40)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 8px 15px;
            }
        """)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        # Theme preview/info
        self.theme_info = QLabel()
        self.theme_info.setWordWrap(True)
        self.theme_info.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 15px;
                font-size: 12px;
                color: #888;
            }
        """)
        theme_layout.addWidget(self.theme_info)
        
        # Apply button
        self.apply_theme_btn = QPushButton("✨ Apply Theme")
        self.apply_theme_btn.setFixedHeight(40)
        self.apply_theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #BB86FC;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #9965D4;
            }
        """)
        self.apply_theme_btn.clicked.connect(self.apply_theme)
        theme_layout.addWidget(self.apply_theme_btn)
        
        theme_layout.addStretch()
        layout.addWidget(theme_group)
        
        # Load current theme
        current_theme = get_theme_preference()
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.update_theme_info()

    def on_theme_changed(self):
        """Theme combo box ပြောင်းရင်"""
        self.update_theme_info()

    def update_theme_info(self):
        """Theme information ကို update လုပ်မယ်"""
        theme_name = self.theme_combo.currentData()
        
        if theme_name == 'dark':
            info_text = """
            <b>Dark Theme</b><br>
            • Eye-friendly for long working hours<br>
            • Reduces screen brightness<br>
            • Perfect for low-light environments<br>
            • Modern, professional look
            """
        else:  # light
            info_text = """
            <b>Light Theme</b><br>
            • Clean and bright interface<br>
            • Better for well-lit environments<br>
            • Easier to read for some users<br>
            • Classic, professional appearance
            """
        
        self.theme_info.setText(info_text)

    def apply_theme(self):
        """Theme ကို Apply လုပ်ပြီး App တစ်ခုလုံးရှိ Window အားလုံးကို ချက်ချင်းအရောင်ပြောင်းခိုင်းမယ်"""
        from PySide6.QtWidgets import QApplication, QMessageBox
        from .styles import get_theme
        
        theme_name = self.theme_combo.currentData()  # 'dark' သို့မဟုတ် 'light'
        
        # ၁။ ရွေးချယ်လိုက်သော Theme ကို Database ထဲမှာ အရင်သိမ်းမယ်
        if set_theme_preference(theme_name):
            
            # ၂။ styles.py ထဲကနေ Theme နဲ့ သက်ဆိုင်တဲ့ Stylesheet (အရောင်သတ်မှတ်ချက်) ကို ယူမယ်
            new_theme = get_theme(theme_name)
            new_style = new_theme.get_stylesheet()
            
            # ၃။ QApplication ကို သုံးပြီး ပွင့်နေသမျှ Window အားလုံးကို (ဥပမာ- Invoice, Client List) 
            # တစ်ခါတည်း ချက်ချင်း အရောင်လိုက်ပြောင်းခိုင်းမယ်
            QApplication.instance().setStyleSheet(new_style)
            
            # ၄။ User ကို အောင်မြင်ကြောင်း အသိပေးချက်ပြမယ်
            QMessageBox.information(
                self, 
                "✅ Theme Updated", 
                f"App style has been changed to {self.theme_combo.currentText()} mode successfully!"
            )
        else:
            # Database သိမ်းရတာ အဆင်မပြေရင် Error ပြမယ်
            QMessageBox.warning(self, "Error", "Failed to save theme preference!")

    def browse_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.logo_path = file_path
            self.m_logo_label.setText(os.path.basename(file_path))

    def load_companies(self):
        try:
            conn = get_db()
            companies = conn.execute("SELECT * FROM companies ORDER BY name").fetchall()
            conn.close()
            
            self.company_combo.clear()
            for company in companies:
                self.company_combo.addItem(company['name'], company['id'])
        except Exception as e:
            print(f"Error loading companies: {e}")

    def load_company_details(self):
        company_id = self.company_combo.currentData()
        if not company_id:
            return
        
        try:
            conn = get_db()
            company = conn.execute(
                "SELECT * FROM companies WHERE id=?", (company_id,)
            ).fetchone()
            conn.close()
            
            if company:
                self.current_company_id = company['id']
                self.m_name.setText(company['name'] or "")
                self.m_code.setText(company['code'] or "")
                self.m_phone.setText(company['phone'] or "")
                self.m_email.setText(company['email'] or "")
                self.m_addr.setText(company['address'] or "")
                self.m_tax.setText(company['tax_number'] or "")
                self.m_bank.setText(company['bank_name'] or "")
                self.m_beneficiary.setText(company['beneficiary'] or "")
                self.m_account_no.setText(company['account_no'] or "")
                self.m_kpay.setText(company['kpay_no'] or "")
                self.m_default.setChecked(bool(company['is_default']))
                
                if company['logo']:
                    self.logo_path = company['logo']
                    self.m_logo_label.setText(os.path.basename(company['logo']))
                else:
                    self.logo_path = ""
                    self.m_logo_label.setText("No logo selected")
        except Exception as e:
            print(f"Error loading company details: {e}")

    def load_security(self):
        try:
            conn = get_db()
            sec = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
            conn.close()
            
            if sec:
                self.u_display.setText(sec['admin_name'] or "")
                self.u_login.setText(sec['admin_user'] or "")
                self.u_pass.clear()
                self.u_pass.setPlaceholderText("Leave blank to keep current password")
        except Exception as e:
            print(f"Error loading security: {e}")

    def save_company(self):
        if not self.m_name.text().strip():
            QMessageBox.warning(self, "Error", "Company name is required!")
            return
        
        try:
            conn = get_db()
            
            # Handle logo
            logo_final = self.logo_path
            
            if self.current_company_id:
                # Update
                conn.execute('''
                    UPDATE companies SET
                        name=?, code=?, phone=?, email=?, address=?, 
                        tax_number=?, logo=?, is_default=?,
                        bank_name=?, beneficiary=?, account_no=?, kpay_no=?
                    WHERE id=?
                ''', (
                    self.m_name.text().strip(),
                    self.m_code.text().strip(),
                    self.m_phone.text().strip(),
                    self.m_email.text().strip(),
                    self.m_addr.toPlainText().strip(),
                    self.m_tax.text().strip(),
                    logo_final,
                    1 if self.m_default.isChecked() else 0,
                    self.m_bank.text().strip(),
                    self.m_beneficiary.text().strip(),
                    self.m_account_no.text().strip(),
                    self.m_kpay.text().strip(),
                    self.current_company_id
                ))
            else:
                # Insert
                conn.execute('''
                    INSERT INTO companies (
                        name, code, phone, email, address, tax_number, logo, is_default,
                        bank_name, beneficiary, account_no, kpay_no
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    self.m_name.text().strip(),
                    self.m_code.text().strip(),
                    self.m_phone.text().strip(),
                    self.m_email.text().strip(),
                    self.m_addr.toPlainText().strip(),
                    self.m_tax.text().strip(),
                    logo_final,
                    1 if self.m_default.isChecked() else 0,
                    self.m_bank.text().strip(),
                    self.m_beneficiary.text().strip(),
                    self.m_account_no.text().strip(),
                    self.m_kpay.text().strip(),
                ))
            
            # Security settings save
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
                conn.execute('''
                    UPDATE settings SET admin_name=?, admin_user=? WHERE id=1
                ''', (
                    self.u_display.text().strip(),
                    self.u_login.text().strip(),
                ))
            
            # Clear other defaults
            if self.m_default.isChecked():
                if self.current_company_id:
                    conn.execute("UPDATE companies SET is_default=0 WHERE id!=?", 
                                (self.current_company_id,))
                else:
                    conn.execute("UPDATE companies SET is_default=0")
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "✅ Success", "Company saved successfully!")
            self.load_companies()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")

    def delete_company(self):
        if not self.current_company_id:
            QMessageBox.warning(self, "Error", "No company selected!")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this company?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = get_db()
                conn.execute("DELETE FROM companies WHERE id=?", (self.current_company_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "✅ Success", "Company deleted!")
                self.current_company_id = None
                self.load_companies()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")

    def new_company(self):
        self.current_company_id = None
        for w in [self.m_name, self.m_code, self.m_phone, self.m_email, 
                  self.m_tax, self.m_bank, self.m_beneficiary, self.m_account_no, self.m_kpay]:
            w.clear()
        self.m_addr.clear()
        self.m_default.setChecked(False)
        self.logo_path = ""
        self.m_logo_label.setText("No logo selected")
# invoice.py - အဆင့်မြှင့်တင်ထားသော ဗားရှင်း (Complete Version)
# ပိုကြီးတဲ့ စာလုံးများ၊ ခလုပ်များ၊ window အပြည့်နဲ့

import calendar
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, QLineEdit,
    QLabel, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QCheckBox, QMessageBox, QScrollArea, QWidget, QDateEdit,
    QFrame, QSplitter, QFormLayout, QFileDialog, QApplication
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor
from database import get_db
from .styles import STYLESHEET, get_theme
from .pdf_generator import InvoicePDFGenerator
import os


class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice_id=None, mode='new'):
        super().__init__(parent)
        
        from .styles import STYLESHEET
        self.setStyleSheet(STYLESHEET)
        
        # Edit mode ဆိုရင် window title ပြောင်းမယ်
        if mode == 'edit' and invoice_id:
            self.setWindowTitle(f"✏️ Edit Invoice (ID: {invoice_id})")
        else:
            self.setWindowTitle("🏢 Professional Invoice Generator")
        
        # === Window အပြည့်ဖြစ်အောင် သတ်မှတ်ခြင်း ===
        self.setWindowState(Qt.WindowMaximized)  # အပြည့်ဖွင့်မယ်
        self.resize(1600, 950)  # နောက်ကွယ်ကအရွယ်အစား
        self.setMinimumSize(1400, 800)  # အနည်းဆုံးအရွယ်အစား
        
        self.invoice_type = "monthly"
        self.clients_data = []
        self.mother_companies_data = []
        self.selected_mother_company = None
        self.updating_totals = False
        self.current_invoice_id = invoice_id
        self.edit_mode = (mode == 'edit')
        
        # Font size ချိန်ညှိခြင်း
        self.set_font_sizes()
        
        self.init_ui()
        self.load_clients_list()
        self.load_mother_companies()
        # Table uses global light stylesheet — no override needed
        
        # Edit mode ဆိုရင် invoice data ကို load မယ်
        if self.edit_mode and self.current_invoice_id:
            QTimer.singleShot(100, lambda: self.load_invoice_data(self.current_invoice_id))
    
    def set_font_sizes(self):
        """စာလုံးအရွယ်အစားများကို ချိန်ညှိမယ်"""
        font = QFont()
        font.setPointSize(11)  # ပုံမှန်စာလုံး အရွယ်
        self.setFont(font)
    
    def init_ui(self):
        # Main layout with fixed footer
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 10)

        # === မိခင် Company Info Bar - ပိုကြီးအောင်လုပ် ===
        company_bar = QFrame()
        company_bar.setFrameShape(QFrame.StyledPanel)
        company_bar.setMinimumHeight(120)  # အမြင့်တိုးမယ်
        company_layout = QHBoxLayout(company_bar)
        company_layout.setSpacing(20)
        company_layout.setContentsMargins(15, 15, 15, 15)
        
        # Logo - ပိုကြီးအောင်
        self.company_logo = QLabel()
        self.company_logo.setFixedSize(100, 100)  # 80 > 100
        self.company_logo.setAlignment(Qt.AlignCenter)
        self.company_logo.setText("🏢 LOGO")
        self.company_logo.setStyleSheet("""
            QLabel {
                border: 2px solid palette(mid);
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.company_logo.setScaledContents(True)
        company_layout.addWidget(self.company_logo)
        
        # Company Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        self.company_name_display = QLabel("Mother Company")
        company_name_font = QFont()
        company_name_font.setPointSize(20)  # 18 > 20
        company_name_font.setBold(True)
        self.company_name_display.setFont(company_name_font)
        info_layout.addWidget(self.company_name_display)
        
        self.company_details_display = QLabel("Phone | Email | Address")
        details_font = QFont()
        details_font.setPointSize(12)  # 14 > 12
        self.company_details_display.setFont(details_font)
        info_layout.addWidget(self.company_details_display)
        
        company_layout.addLayout(info_layout, 3)
        
        # Tax Number
        tax_layout = QHBoxLayout()
        tax_label = QLabel("Tax ID:")
        tax_label_font = QFont()
        tax_label_font.setPointSize(12)
        tax_label.setFont(tax_label_font)
        tax_layout.addWidget(tax_label)
        
        self.company_tax_display = QLabel("N/A")
        tax_value_font = QFont()
        tax_value_font.setPointSize(14)
        tax_value_font.setBold(True)
        self.company_tax_display.setFont(tax_value_font)
        tax_layout.addWidget(self.company_tax_display)
        company_layout.addLayout(tax_layout)
        
        layout.addWidget(company_bar)

        # === Header Section - ပိုကြီးအောင်လုပ် ===
        header_gb = QGroupBox("📄 Invoice Configuration & Client Information")
        header_gb.setMinimumHeight(280)  # 220 > 280
        
        header_font = QFont()
        header_font.setPointSize(13)
        header_font.setBold(True)
        header_gb.setFont(header_font)
        
        header_layout = QVBoxLayout(header_gb)
        header_layout.setSpacing(15)
        header_layout.setContentsMargins(15, 20, 15, 15)
        
        # === ပထမတန်း ===
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        
        # Type
        type_label = QLabel("Type:")
        type_label_font = QFont()
        type_label_font.setPointSize(12)
        type_label.setFont(type_label_font)
        row1.addWidget(type_label)
        
        self.inv_type_cb = QComboBox()
        self.inv_type_cb.addItems(["📅 Monthly", "📊 Daily"])
        self.inv_type_cb.setMinimumWidth(150)
        self.inv_type_cb.setMinimumHeight(35)
        cb_font = QFont()
        cb_font.setPointSize(12)
        self.inv_type_cb.setFont(cb_font)
        self.inv_type_cb.currentTextChanged.connect(self.on_invoice_type_changed)
        row1.addWidget(self.inv_type_cb)
        
        # Mother Co
        mother_label = QLabel("Mother Co:")
        mother_label.setFont(type_label_font)
        row1.addWidget(mother_label)
        
        self.mother_company_cb = QComboBox()
        self.mother_company_cb.setMinimumWidth(250)
        self.mother_company_cb.setMinimumHeight(35)
        self.mother_company_cb.setFont(cb_font)
        self.mother_company_cb.currentIndexChanged.connect(self.on_mother_company_selected)
        row1.addWidget(self.mother_company_cb)
        
        # Service
        service_label = QLabel("Service:")
        service_label.setFont(type_label_font)
        row1.addWidget(service_label)
        
        self.service_cat_cb = QComboBox()
        self.service_cat_cb.setEditable(True)
        self.service_cat_cb.addItems(["🛡️ Security", "🧹 Cleaning", "🔧 Maintenance", "Other"])
        self.service_cat_cb.setMinimumWidth(180)
        self.service_cat_cb.setMinimumHeight(35)
        self.service_cat_cb.setFont(cb_font)
        row1.addWidget(self.service_cat_cb)
        
        row1.addStretch()
        header_layout.addLayout(row1)
        
        # === ဒုတိယတန်း ===
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        # Inv No
        invno_label = QLabel("Inv No:")
        invno_label.setFont(type_label_font)
        row2.addWidget(invno_label)
        
        self.inv_no = QLineEdit()
        self.inv_no.setReadOnly(True)
        self.inv_no.setMinimumWidth(180)
        self.inv_no.setMinimumHeight(35)
        lineedit_font = QFont()
        lineedit_font.setPointSize(12)
        self.inv_no.setFont(lineedit_font)
        row2.addWidget(self.inv_no)
        
        # Date
        date_label = QLabel("Date:")
        date_label.setFont(type_label_font)
        row2.addWidget(date_label)
        
        self.invoice_date = QDateEdit()
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setMinimumWidth(150)
        self.invoice_date.setMinimumHeight(35)
        self.invoice_date.setFont(lineedit_font)
        self.invoice_date.dateChanged.connect(self.calculate_totals)
        row2.addWidget(self.invoice_date)
        
        # Status
        status_label = QLabel("Status:")
        status_label.setFont(type_label_font)
        row2.addWidget(status_label)
        
        self.received_status = QLabel("📥 Not Received")
        self.received_status.setMinimumWidth(150)
        self.received_status.setMinimumHeight(35)
        status_font = QFont()
        status_font.setPointSize(12)
        status_font.setBold(True)
        self.received_status.setFont(status_font)
        row2.addWidget(self.received_status)
        
        row2.addStretch()
        header_layout.addLayout(row2)
        
        # === တတိယတန်း ===
        row3 = QHBoxLayout()
        row3.setSpacing(15)
        
        # Title
        title_label = QLabel("Title:")
        title_label.setFont(type_label_font)
        row3.addWidget(title_label)
        
        self.inv_title = QLineEdit("PROFESSIONAL SERVICE INVOICE")
        self.inv_title.setMinimumWidth(600)
        self.inv_title.setMinimumHeight(35)
        self.inv_title.setFont(lineedit_font)
        row3.addWidget(self.inv_title)
        
        row3.addStretch()
        header_layout.addLayout(row3)
        
        # === စတုတ္ထတန်း ===
        row4 = QHBoxLayout()
        row4.setSpacing(15)
        
        # Client Co
        client_label = QLabel("Client Co:")
        client_label.setFont(type_label_font)
        row4.addWidget(client_label)
        
        self.client_cb = QComboBox()
        self.client_cb.setEditable(True)
        self.client_cb.setPlaceholderText("Select Client Company")
        self.client_cb.setMinimumWidth(350)
        self.client_cb.setMinimumHeight(35)
        self.client_cb.setFont(cb_font)
        self.client_cb.currentIndexChanged.connect(self.on_client_selected)
        row4.addWidget(self.client_cb)
        
        # Address
        addr_label = QLabel("Address:")
        addr_label.setFont(type_label_font)
        row4.addWidget(addr_label)
        
        self.addr_cb = QComboBox()
        self.addr_cb.setEditable(True)
        self.addr_cb.setPlaceholderText("Select Address")
        self.addr_cb.setMinimumWidth(400)
        self.addr_cb.setMinimumHeight(35)
        self.addr_cb.setFont(cb_font)
        row4.addWidget(self.addr_cb)
        
        row4.addStretch()
        header_layout.addLayout(row4)
        
        # === ပဉ္စမတန်း (Contact Info) ===
        # === ပဉ္စမတန်း (Contact Info) ===
        row5 = QHBoxLayout()
        row5.setSpacing(15)

        contact_label = QLabel("Contact:")
        contact_label.setFont(type_label_font)
        row5.addWidget(contact_label)

        # Name
        name_layout = QHBoxLayout()
        name_layout.setSpacing(5)

        self.contact_name = QLineEdit()
        self.contact_name.setPlaceholderText("Name")
        self.contact_name.setMinimumWidth(140)
        self.contact_name.setMinimumHeight(35)
        self.contact_name.setFont(lineedit_font)
        name_layout.addWidget(self.contact_name)

        self.show_name = QCheckBox()
        self.show_name.setMinimumHeight(35)
        name_layout.addWidget(self.show_name)

        row5.addLayout(name_layout)

        # Position
        pos_layout = QHBoxLayout()
        pos_layout.setSpacing(5)

        self.contact_pos = QLineEdit()
        self.contact_pos.setPlaceholderText("Position")
        self.contact_pos.setMinimumWidth(120)
        self.contact_pos.setMinimumHeight(35)
        self.contact_pos.setFont(lineedit_font)
        pos_layout.addWidget(self.contact_pos)

        self.show_pos = QCheckBox()
        self.show_pos.setMinimumHeight(35)
        pos_layout.addWidget(self.show_pos)

        row5.addLayout(pos_layout)

        # Phone
        phone_layout = QHBoxLayout()
        phone_layout.setSpacing(5)

        self.contact_ph = QLineEdit()
        self.contact_ph.setPlaceholderText("Phone")
        self.contact_ph.setMinimumWidth(120)
        self.contact_ph.setMinimumHeight(35)
        self.contact_ph.setFont(lineedit_font)
        phone_layout.addWidget(self.contact_ph)

        self.show_ph = QCheckBox()
        self.show_ph.setMinimumHeight(35)
        phone_layout.addWidget(self.show_ph)

        row5.addLayout(phone_layout)

        # Email
        email_layout = QHBoxLayout()
        email_layout.setSpacing(5)

        self.contact_em = QLineEdit()
        self.contact_em.setPlaceholderText("Email")
        self.contact_em.setMinimumWidth(200)
        self.contact_em.setMinimumHeight(35)
        self.contact_em.setFont(lineedit_font)
        email_layout.addWidget(self.contact_em)

        self.show_em = QCheckBox()
        self.show_em.setMinimumHeight(35)
        email_layout.addWidget(self.show_em)

        row5.addLayout(email_layout)

        row5.addStretch()
        header_layout.addLayout(row5)
        
        layout.addWidget(header_gb)

        # --- Service Details (Table) ---
        items_gb = QGroupBox("📦 Service Details")
        items_gb_font = QFont()
        items_gb_font.setPointSize(13)
        items_gb_font.setBold(True)
        items_gb.setFont(items_gb_font)
        
        items_lay = QVBoxLayout(items_gb)
        items_lay.setSpacing(10)
        
        # Working Days Checkbox
        self.work_day_check = QCheckBox("✅ Enable Working Days Calculation")
        work_check_font = QFont()
        work_check_font.setPointSize(12)
        self.work_day_check.setFont(work_check_font)
        self.work_day_check.setMinimumHeight(35)
        self.work_day_check.stateChanged.connect(self.on_working_days_toggled)
        items_lay.addWidget(self.work_day_check)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setMinimumHeight(350)
        self.table.setMaximumHeight(400)
        self.table.verticalHeader().setVisible(False)
        self.table.itemChanged.connect(self.on_cell_changed)
        self.table.setAlternatingRowColors(True)

        # Cell editor (inline QLineEdit) — OS dark override ကို ဖယ်ချနိုင်တဲ့ တစ်ခုတည်းသောနည်း
        from PySide6.QtWidgets import QStyledItemDelegate
        class LightDelegate(QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                editor = super().createEditor(parent, option, index)
                if editor:
                    editor.setStyleSheet(
                        "QLineEdit, QWidget {"
                        "  background-color: #FFFFFF;"
                        "  color: #1A1A1A;"
                        "  border: 2px solid #2563EB;"
                        "  padding: 2px 4px;"
                        "  font-size: 11pt;"
                        "}"
                    )
                return editor
        self.table.setItemDelegate(LightDelegate(self.table))

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #1A1A1A;
                alternate-background-color: #F8F8F8;
                gridline-color: #DDDDDD;
                selection-background-color: #DBEAFE;
                selection-color: #1A1A1A;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
            }
            QTableWidget::item {
                color: #1A1A1A;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1A1A1A;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #1A1A1A;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #2563EB;
                font-weight: bold;
            }
        """)
        
        # Table font
        table_font = QFont()
        table_font.setPointSize(11)
        self.table.setFont(table_font)
        
        # Row height
        self.table.verticalHeader().setDefaultSectionSize(35)
        
        self.update_table_headers()
        items_lay.addWidget(self.table)
        
        # Add Line Button
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(10)
        self.add_btn = QPushButton("➕ Add Line")
        self.add_btn.setFixedWidth(150)
        self.add_btn.setFixedHeight(45)
        add_btn_font = QFont()
        add_btn_font.setPointSize(12)
        add_btn_font.setBold(True)
        self.add_btn.setFont(add_btn_font)
        self.add_btn.clicked.connect(self.add_item_row)
        btn_lay.addWidget(self.add_btn)
        btn_lay.addStretch()
        items_lay.addLayout(btn_lay)
        layout.addWidget(items_gb)

        # --- Financial Summary ---
        summary_gb = QGroupBox("💰 Financial Summary")
        summary_gb.setFont(items_gb_font)
        summary_gb.setMinimumHeight(220)

        summary_layout = QHBoxLayout(summary_gb)
        summary_layout.setSpacing(15)
        summary_layout.setContentsMargins(15, 25, 15, 15)

        # ── Left: Subtotal & Tax ──────────────────────────────────────
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setMinimumWidth(280)
        left_layout = QHBoxLayout(left_frame)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(12, 12, 12, 12)

        val_font = QFont()
        val_font.setPointSize(15)
        val_font.setBold(True)
        lbl_font = QFont()
        lbl_font.setPointSize(11)
        lbl_font.setBold(True)

        # Subtotal
        subtotal_frame = QFrame()
        subtotal_frame.setFrameShape(QFrame.StyledPanel)
        subtotal_layout = QVBoxLayout(subtotal_frame)
        subtotal_layout.setSpacing(6)
        subtotal_layout.setContentsMargins(10, 10, 10, 10)

        subtotal_title = QLabel("SUBTOTAL")
        subtotal_title.setFont(lbl_font)
        subtotal_layout.addWidget(subtotal_title, 0, Qt.AlignCenter)

        self.subtotal_lbl = QLabel("0 MMK")
        self.subtotal_lbl.setFont(val_font)
        subtotal_layout.addWidget(self.subtotal_lbl, 0, Qt.AlignCenter)
        left_layout.addWidget(subtotal_frame)

        # Tax
        tax_frame = QFrame()
        tax_frame.setFrameShape(QFrame.StyledPanel)
        tax_layout = QVBoxLayout(tax_frame)
        tax_layout.setSpacing(6)
        tax_layout.setContentsMargins(10, 10, 10, 10)

        tax_title = QLabel("TAX (5%)")
        tax_title.setFont(lbl_font)
        tax_layout.addWidget(tax_title, 0, Qt.AlignCenter)

        self.tax_lbl = QLabel("0 MMK")
        self.tax_lbl.setFont(val_font)
        tax_layout.addWidget(self.tax_lbl, 0, Qt.AlignCenter)
        left_layout.addWidget(tax_frame)

        summary_layout.addWidget(left_frame)

        # ── Middle: Tax checkbox + Deduction ─────────────────────────
        middle_frame = QFrame()
        middle_frame.setFrameShape(QFrame.StyledPanel)
        middle_layout = QVBoxLayout(middle_frame)
        middle_layout.setSpacing(10)
        middle_layout.setContentsMargins(15, 12, 15, 12)

        self.tax_check = QCheckBox("💳 Apply Commercial Tax")
        tax_check_font = QFont()
        tax_check_font.setPointSize(11)
        tax_check_font.setBold(True)
        self.tax_check.setFont(tax_check_font)
        self.tax_check.setMinimumHeight(32)
        self.tax_check.stateChanged.connect(self.calculate_totals)
        middle_layout.addWidget(self.tax_check)

        # Deduction label
        deduction_lbl = QLabel("Deduction / Advance:")
        deduction_lbl.setFont(lbl_font)
        deduction_lbl.setMinimumHeight(24)
        middle_layout.addWidget(deduction_lbl)

        # Deduction inputs row
        deduction_row = QHBoxLayout()
        deduction_row.setSpacing(8)

        input_font = QFont()
        input_font.setPointSize(11)

        amt_font = QFont()
        amt_font.setPointSize(13)
        amt_font.setBold(True)

        # Description textbox (wider)
        self.advance_text = QLineEdit()
        self.advance_text.setPlaceholderText("Description (e.g. Advance paid)")
        self.advance_text.setMinimumHeight(42)
        self.advance_text.setFont(input_font)
        deduction_row.addWidget(self.advance_text, 3)   # stretch 3 = wider

        # Amount box (bigger font, fixed width)
        self.advance_amt = QLineEdit("0")
        self.advance_amt.setMinimumWidth(150)
        self.advance_amt.setMinimumHeight(42)
        self.advance_amt.setFont(amt_font)
        self.advance_amt.setAlignment(Qt.AlignRight)
        self.advance_amt.textChanged.connect(self.calculate_totals)
        deduction_row.addWidget(self.advance_amt, 1)    # stretch 1 = narrower

        middle_layout.addLayout(deduction_row)
        summary_layout.addWidget(middle_frame, 3)

        # ── Right: Grand Total ────────────────────────────────────────
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setMinimumWidth(220)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(20, 15, 20, 15)
        right_layout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        grand_title = QLabel("GRAND TOTAL")
        grand_title_font = QFont()
        grand_title_font.setPointSize(12)
        grand_title_font.setBold(True)
        grand_title.setFont(grand_title_font)
        right_layout.addWidget(grand_title, 0, Qt.AlignRight)

        self.grand_total_lbl = QLabel("0 MMK")
        grand_total_font = QFont()
        grand_total_font.setPointSize(22)
        grand_total_font.setBold(True)
        self.grand_total_lbl.setFont(grand_total_font)
        self.grand_total_lbl.setMinimumHeight(50)
        right_layout.addWidget(self.grand_total_lbl, 0, Qt.AlignRight)

        summary_layout.addWidget(right_frame)

        layout.addWidget(summary_gb)
        
        # Small stretch
        layout.addStretch(1)

        # Add container to scroll
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # --- Footer - ပိုကြီးအောင်၊ ခလုပ်တွေပေါ်လွင်အောင် ---
        footer_frame = QFrame()
        footer_frame.setFixedHeight(100)  # 75 > 100
        footer_frame.setFrameShape(QFrame.StyledPanel)
        
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(25, 15, 25, 15)
        footer_layout.setSpacing(20)

        # Left buttons
        left_btn_frame = QFrame()
        left_btn_layout = QHBoxLayout(left_btn_frame)
        left_btn_layout.setSpacing(15)
        
        self.list_btn = QPushButton("📋 Invoice List")
        self.list_btn.setFixedHeight(50)
        self.list_btn.setFixedWidth(160)
        btn_font = QFont()
        btn_font.setPointSize(13)
        btn_font.setBold(True)
        self.list_btn.setFont(btn_font)
        self.list_btn.clicked.connect(self.show_invoice_list)
        left_btn_layout.addWidget(self.list_btn)

        self.print_btn = QPushButton("🖨️ Print")
        self.print_btn.setFixedHeight(50)
        self.print_btn.setFixedWidth(120)
        self.print_btn.setFont(btn_font)
        self.print_btn.clicked.connect(self.print_invoice)
        left_btn_layout.addWidget(self.print_btn)

        self.export_btn = QPushButton("📊 Export")
        self.export_btn.setFixedHeight(50)
        self.export_btn.setFixedWidth(120)
        self.export_btn.setFont(btn_font)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        left_btn_layout.addWidget(self.export_btn)
        
        footer_layout.addWidget(left_btn_frame)

        footer_layout.addStretch()

        # Right buttons
        right_btn_frame = QFrame()
        right_btn_layout = QHBoxLayout(right_btn_frame)
        right_btn_layout.setSpacing(15)

        self.save_btn = QPushButton("💾 Save Invoice")
        self.save_btn.setFixedHeight(55)  # 45 > 55
        self.save_btn.setFixedWidth(200)  # 160 > 200
        self.save_btn.setFont(btn_font)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_invoice)
        right_btn_layout.addWidget(self.save_btn)

        footer_layout.addWidget(right_btn_frame)

        main_layout.addWidget(footer_frame)

        self.add_item_row()

    def load_mother_companies(self):
        """မိခင် company များကို database ကနေ load မယ်"""
        try:
            conn = get_db()
            companies = conn.execute("SELECT * FROM companies ORDER BY is_default DESC, name").fetchall()
            conn.close()
            
            self.mother_company_cb.clear()
            self.mother_companies_data = [dict(company) for company in companies]
            
            for company in self.mother_companies_data:
                name = company['name']
                if company.get('is_default'):
                    name += " (Default)"
                self.mother_company_cb.addItem(name, company)
            
            # Select default company
            for i, company in enumerate(self.mother_companies_data):
                if company.get('is_default'):
                    self.mother_company_cb.setCurrentIndex(i)
                    self.display_mother_company_info(company)
                    break
                    
        except Exception as e:
            print(f"Error loading mother companies: {e}")

    def on_mother_company_selected(self, index):
        """မိခင် company ရွေးလိုက်ရင် အချက်အလက်တွေပြမယ်"""
        company = self.mother_company_cb.itemData(index)
        if company:
            self.selected_mother_company = company
            self.display_mother_company_info(company)

    def display_mother_company_info(self, company):
        """မိခင် company info ကို top bar မှာပြမယ်"""
        if company:
            self.company_name_display.setText(company.get('name', 'N/A'))
            
            # Phone | Email | Address
            details = []
            if company.get('phone'):
                details.append(f"📞 {company['phone']}")
            if company.get('email'):
                details.append(f"✉️ {company['email']}")
            if company.get('address'):
                addr = company['address'].split('\n')[0][:40]
                details.append(f"📍 {addr}")
            
            self.company_details_display.setText(" | ".join(details) if details else "No contact info")
            self.company_tax_display.setText(company.get('tax_number', 'N/A'))
            
            # Logo
            logo_path = company.get('logo', '')
            if logo_path and os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.company_logo.setPixmap(scaled_pixmap)
                    self.company_logo.setText("")
                else:
                    self.company_logo.clear()
                    self.company_logo.setText("No Logo")
            else:
                self.company_logo.clear()
                self.company_logo.setText("No Logo")

    def show_invoice_list(self):
        """စာရင်းပြန်ကြည့်ရန်"""
        from .invoice_list import InvoiceListDialog
        dialog = InvoiceListDialog(self)
        dialog.exec()
           
    def load_clients_list(self):
        """Client company များကို database ကနေ load မယ်"""
        try:
            self.client_cb.clear()
            self.client_cb.addItem("Select/Type New", None)
            conn = get_db()
            rows = conn.execute("SELECT * FROM clients").fetchall()
            self.clients_data = [dict(row) for row in rows]
            for client in self.clients_data:
                name = client.get('name', 'Unknown')
                self.client_cb.addItem(name, client)
            conn.close()
        except Exception as e: 
            print(f"Load Error: {e}")

    def on_client_selected(self, index):
        """Client company ရွေးလိုက်လျှင် Contact Info နဲ့ Invoice No ကို Update လုပ်ခြင်း"""
        
        if index <= 0:
            self.addr_cb.clear()
            self.clear_contact_fields()
            return
            
        client = self.client_cb.itemData(index)
        if client:
            # Addresses
            self.addr_cb.clear()
            addresses = []
            for i in range(1, 4):
                addr = client.get(f'addr{i}')
                if addr:
                    addresses.append(addr)
                    self.addr_cb.addItem(addr)
            if addresses: 
                self.addr_cb.setCurrentIndex(0)
                
            # Contact info
            self.contact_name.setText(client.get('c1_name', ''))
            self.contact_pos.setText(client.get('c1_pos', ''))
            self.contact_ph.setText(client.get('c1_ph', ''))
            self.contact_em.setText(client.get('c1_em', ''))
            self.set_toggles(False)

    def clear_contact_fields(self):
        self.contact_name.clear()
        self.contact_pos.clear()
        self.contact_ph.clear()
        self.contact_em.clear()
        self.set_toggles(False)

    def set_toggles(self, state):
        self.show_name.setChecked(state)
        self.show_pos.setChecked(state)
        self.show_ph.setChecked(state)
        self.show_em.setChecked(state)

    def get_col_index(self, name):
        """Column name အတွက် index ကိုရှာမယ်"""
        for i in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(i)
            if header_item and header_item.text() == name:
                return i
        return -1

    def update_table_headers(self):
        """Table header တွေကို update လုပ်မယ်"""
        is_daily = self.inv_type_cb.currentText() == "📊 Daily"
        use_work_days = self.work_day_check.isChecked()
    
        headers = ["Description"]
    
        if is_daily:
            headers.extend(["Start Date", "End Date", "Days"])  # ဒီ လိုင်း ကို မတွေ့ရင် ထည့်ပါ။ ရှိရင် ဒီအတိုင်း ပြင်ပါ။
        elif use_work_days:
            headers.append("Days")
    
        headers.extend(["Qty", "Unit Price", "Amount", "Del"])
    
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
    
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
        for i in range(1, len(headers)):
            if headers[i] == "Del":
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 45)
            else:
                header.setSectionResizeMode(i, QHeaderView.Interactive)
                self.table.setColumnWidth(i, 100)

    def refresh_row_widgets(self, row):
        """Row ထဲက widget တွေကို refresh လုပ်မယ်"""
        for i in range(self.table.columnCount()):
            self.table.removeCellWidget(row, i)
    
        # Delete Button
        del_idx = self.get_col_index("Del")
        if del_idx != -1:
            from PySide6.QtWidgets import QStyle as _QStyle
            from PySide6.QtCore import QSize as _QSize
            del_btn = QPushButton()
            del_btn.setIcon(del_btn.style().standardIcon(_QStyle.SP_DialogCloseButton))
            del_btn.setIconSize(_QSize(14, 14))
            del_btn.setFixedSize(30, 28)
            del_btn.setToolTip("Delete row")
            del_btn.setStyleSheet(
                "QPushButton{background:#ef4444;border:none;border-radius:4px;}"
                "QPushButton:hover{background:#dc2626;}"
            )
            del_btn.clicked.connect(self.delete_specific_row)
            self.table.setCellWidget(row, del_idx, del_btn)
    
        # Start/End Dates if Daily
        is_daily = self.inv_type_cb.currentText() == "📊 Daily"
        if is_daily:
            start_idx = self.get_col_index("Start Date")
            if start_idx != -1:
                for offset in range(2):  # 0: Start, 1: End
                    de = QDateEdit()
                    de.setCalendarPopup(True)
                    de.setDate(QDate.currentDate())
                    de.setStyleSheet("font-size: 12px; padding: 4px;")
                    de.dateChanged.connect(lambda checked, r=row: self.calculate_daily_days(r))  # ဒီ လိုင်း ကို ရှိနေတဲ့ အတိုင်း ချိန်ညှိပါ
                    self.table.setCellWidget(row, start_idx + offset, de)

    def calculate_totals(self):
        """Total တွေကိုတွက်မယ်"""
        if self.updating_totals: 
            return
        self.updating_totals = True
        try:
            subtotal = 0
            
            # Get column indices
            qty_idx = self.get_col_index("Qty")
            price_idx = self.get_col_index("Unit Price")
            amt_idx = self.get_col_index("Amount")
            days_idx = self.get_col_index("Days")
            
            # Get days in month for working days calculation
            target_date = self.invoice_date.date()
            days_in_month = calendar.monthrange(target_date.year(), target_date.month())[1]
            
            is_daily = self.inv_type_cb.currentText() == "📊 Daily"
            use_work_days = self.work_day_check.isChecked()
            
            for row in range(self.table.rowCount()):
                # Get values
                qty_item = self.table.item(row, qty_idx) if qty_idx != -1 else None
                price_item = self.table.item(row, price_idx) if price_idx != -1 else None
                days_item = self.table.item(row, days_idx) if days_idx != -1 else None
                
                qty = float(qty_item.text()) if qty_item and qty_item.text() else 0
                price = float(price_item.text().replace(',', '')) if price_item and price_item.text() else 0
                
                # Calculate line total based on mode
                if is_daily:
                    # Daily mode - use days from date widgets
                    start_widget = self.table.cellWidget(row, self.get_col_index("Start Date")) if self.get_col_index("Start Date") != -1 else None
                    end_widget = self.table.cellWidget(row, self.get_col_index("Start Date") + 1) if self.get_col_index("Start Date") != -1 else None
                    
                    if start_widget and end_widget:
                        days = start_widget.date().daysTo(end_widget.date()) + 1
                        line_total = price * qty * days
                    else:
                        line_total = qty * price
                        
                elif use_work_days and days_item and days_item.text():
                    # Working days mode - with days entered
                    work_days = float(days_item.text())
                    if work_days > days_in_month:
                        work_days = days_in_month
                        days_item.setText(str(days_in_month))
                    
                    # Formula: (price / days_in_month) * qty * work_days
                    line_total = (price / days_in_month) * qty * work_days
                else:
                    # Normal mode - just qty * price
                    line_total = qty * price
                
                subtotal += line_total
                
                # Update amount cell
                if amt_idx != -1:
                    amt_item = self.table.item(row, amt_idx)
                    if not amt_item:
                        amt_item = QTableWidgetItem()
                        amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        amt_item.setFlags(amt_item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(row, amt_idx, amt_item)
                    amt_item.setText(f"{line_total:,.0f}")
            
            tax = subtotal * 0.05 if self.tax_check.isChecked() else 0
            adv_text = self.advance_amt.text().replace(',', '')
            adv = float(adv_text) if adv_text else 0
            
            self.subtotal_lbl.setText(f"{subtotal:,.0f} MMK")
            self.tax_lbl.setText(f"{tax:,.0f} MMK")
            self.grand_total_lbl.setText(f"{subtotal + tax - adv:,.0f} MMK")
            
        except Exception as e: 
            print(f"Calc Error: {e}")
        finally: 
            self.updating_totals = False

    def on_working_days_toggled(self):
        """Working days checkbox ပြောင်းရင်"""
        saved_data = []
    
        qty_idx = self.get_col_index("Qty")
        price_idx = self.get_col_index("Unit Price")
        days_idx = self.get_col_index("Days")
    
        for row in range(self.table.rowCount()):
            saved_data.append({
                "desc": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
                "qty": self.table.item(row, qty_idx).text() if qty_idx != -1 and self.table.item(row, qty_idx) else "0",
                "price": self.table.item(row, price_idx).text() if price_idx != -1 and self.table.item(row, price_idx) else "0",
                "days": self.table.item(row, days_idx).text() if days_idx != -1 and self.table.item(row, days_idx) else ""
            })
    
        self.update_table_headers()
        self.updating_totals = True
    
        self.table.setRowCount(0)  # Clear all rows and re-add them to avoid editing issues
    
        for data in saved_data:
            self.add_item_row()  # Add new row and set values
            row = self.table.rowCount() - 1
            self.table.item(row, 0).setText(data["desc"])
        
            nq = self.get_col_index("Qty")
            if nq != -1:
                self.table.item(row, nq).setText(data["qty"])
        
            np = self.get_col_index("Unit Price")
            if np != -1:
                self.table.item(row, np).setText(data["price"])
        
            nd = self.get_col_index("Days")
            if nd != -1:
                item = QTableWidgetItem(data["days"])
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, nd, item)
    
        self.updating_totals = False
        self.calculate_totals()

    def add_item_row(self):
        """Item row အသစ်ထည့်မယ်"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))
        
        # Qty
        qty_idx = self.get_col_index("Qty")
        if qty_idx != -1:
            qty_item = QTableWidgetItem("0")
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, qty_idx, qty_item)
        
        # Unit Price
        price_idx = self.get_col_index("Unit Price")
        if price_idx != -1:
            price_item = QTableWidgetItem("0")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, price_idx, price_item)
        
        # Amount
        amt_idx = self.get_col_index("Amount")
        if amt_idx != -1:
            amt_item = QTableWidgetItem("0")
            amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amt_item.setFlags(amt_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, amt_idx, amt_item)
        
        self.refresh_row_widgets(row)
        self.calculate_totals()

    def delete_specific_row(self):
        """သီးခြား row တစ်ခုကို ဖျက်မယ်"""
        button = self.sender()
        if button:
            index = self.table.indexAt(button.pos())
            if index.isValid():
                if self.table.rowCount() > 1:
                    self.table.removeRow(index.row())
                else:
                    self.clear_row_data(index.row())
                self.calculate_totals()

    def clear_row_data(self, row):
        """Row data ကိုရှင်းမယ်"""
        item = self.table.item(row, 0)
        if item:
            item.setText("")
        self.refresh_row_widgets(row)
        self.calculate_totals()

    def on_cell_changed(self, item):
        """Cell ပြောင်းရင် auto-calculate လုပ်မယ်"""
        if not self.updating_totals:
            self.calculate_totals()

    def on_invoice_type_changed(self):
        """Invoice type ပြောင်းရင်"""
        self.table.setRowCount(0)
        self.update_table_headers()
        self.add_item_row()

    def calculate_daily_days(self, row):
        """Daily mode အတွက် ရက်အရေအတွက်တွက်မယ်"""
        s_idx = self.get_col_index("Start Date")
        d_idx = self.get_col_index("Days")
    
        if s_idx != -1 and d_idx != -1:
            start_widget = self.table.cellWidget(row, s_idx)
            end_widget = self.table.cellWidget(row, s_idx + 1)  # ဒီ လိုင်း ကို မတွေ့ရင် ထည့်ပါ။ ရှိရင် ဒီအတိုင်း ပြင်ပါ။
        
            if start_widget and end_widget:
                s_d = start_widget.date()
                e_d = end_widget.date()
                diff = max(1, s_d.daysTo(e_d) + 1)
            
                self.updating_totals = True
                item = self.table.item(row, d_idx)
                if not item:
                    item = QTableWidgetItem(str(diff))
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, d_idx, item)
                else:
                    item.setText(str(diff))
                self.updating_totals = False
            
                self.calculate_totals()
                
    def load_invoice_data(self, invoice_id):
        """Database ကနေ invoice data ကို load ပြီး form မှာဖြည့်မယ်"""
        try:
            conn = get_db()
            
            # Invoice main data ယူမယ်
            invoice = conn.execute('''
                SELECT i.*, 
                    c.c1_name, c.c1_pos, c.c1_ph, c.c1_em,
                    c.abbr as client_abbr
                FROM invoices i
                LEFT JOIN clients c ON i.client_id = c.id
                WHERE i.id = ?
            ''', (invoice_id,)).fetchone()
            
            if not invoice:
                QMessageBox.warning(self, "Error", "Invoice not found!")
                conn.close()
                return
            
            # Client ကိုရွေးမယ်
            client_name = invoice['company_name']
            found = False
            for i in range(self.client_cb.count()):
                if self.client_cb.itemText(i) == client_name:
                    self.client_cb.setCurrentIndex(i)
                    found = True
                    break
            
            if not found and client_name:
                self.client_cb.setEditText(client_name)
            
            # Invoice basic info
            self.inv_no.setText(invoice['invoice_no'])
            self.inv_no.setReadOnly(True)
            
            # Date
            if invoice['invoice_date']:
                date_parts = invoice['invoice_date'].split('-')
                if len(date_parts) == 3:
                    self.invoice_date.setDate(QDate(
                        int(date_parts[0]), 
                        int(date_parts[1]), 
                        int(date_parts[2])
                    ))
            
            # Address
            if invoice['address']:
                self.addr_cb.setEditText(invoice['address'])
            
            # Contact info
            self.contact_name.setText(invoice['contact_name'] or invoice['c1_name'] or '')
            self.contact_pos.setText(invoice['contact_pos'] or invoice['c1_pos'] or '')
            self.contact_ph.setText(invoice['contact_ph'] or invoice['c1_ph'] or '')
            self.contact_em.setText(invoice['contact_email'] or invoice['c1_em'] or '')
            
            # Show checkboxes
            self.show_name.setChecked(bool(invoice['contact_name']))
            self.show_pos.setChecked(bool(invoice['contact_pos']))
            self.show_ph.setChecked(bool(invoice['contact_ph']))
            self.show_em.setChecked(bool(invoice['contact_email']))
            
            # Title (inv_title)
            if invoice['inv_title']:
                self.inv_title.setText(invoice['inv_title'])
            else:
                self.inv_title.setText("PROFESSIONAL SERVICE INVOICE")
            
            # Service Type (service_type)
            if invoice['service_type']:
                service_text = invoice['service_type']
                found_service = False
                for i in range(self.service_cat_cb.count()):
                    item_text = self.service_cat_cb.itemText(i)
                    if service_text in item_text or item_text in service_text:
                        self.service_cat_cb.setCurrentIndex(i)
                        found_service = True
                        break
                
                if not found_service:
                    self.service_cat_cb.setEditText(service_text)
            
            # Mother Company
            if invoice['mother_company_id']:
                for i in range(self.mother_company_cb.count()):
                    company_data = self.mother_company_cb.itemData(i)
                    if company_data and company_data.get('id') == invoice['mother_company_id']:
                        self.mother_company_cb.setCurrentIndex(i)
                        break
            
            # Financial info
            self.tax_check.setChecked(invoice['tax'] > 0)
            self.advance_amt.setText(str(invoice['advance'] or 0))
            
            # Items တွေ load မယ်
            items = conn.execute('''
                SELECT * FROM invoice_items 
                WHERE invoice_id = ? 
                ORDER BY id
            ''', (invoice_id,)).fetchall()
            
            print(f"Loading {len(items)} items from database")
            
            # Clear existing rows
            self.table.setRowCount(0)
            
            # Get column indices
            desc_idx = 0  # Description column
            qty_idx = self.get_col_index("Qty")
            price_idx = self.get_col_index("Unit Price")
            amt_idx = self.get_col_index("Amount")
            
            print(f"Column indices - Qty: {qty_idx}, Price: {price_idx}, Amount: {amt_idx}")
            
            for item in items:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Description
                desc_item = QTableWidgetItem(item['description'] or '')
                self.table.setItem(row, desc_idx, desc_item)
                
                # Qty
                if qty_idx != -1:
                    qty_value = str(int(item['qty'])) if item['qty'] else '0'
                    qty_item = QTableWidgetItem(qty_value)
                    qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, qty_idx, qty_item)
                    print(f"Row {row}: Set Qty = {qty_value}")
                
                # Unit Price
                if price_idx != -1:
                    price_value = f"{item['unit_price']:,.0f}" if item['unit_price'] else '0'
                    price_item = QTableWidgetItem(price_value)
                    price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, price_idx, price_item)
                    print(f"Row {row}: Set Price = {price_value}")
                
                # Amount
                if amt_idx != -1:
                    amt_value = f"{item['amount']:,.0f}" if item['amount'] else '0'
                    amt_item = QTableWidgetItem(amt_value)
                    amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    amt_item.setFlags(amt_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, amt_idx, amt_item)
                    print(f"Row {row}: Set Amount = {amt_value}")
                
                self.refresh_row_widgets(row)
            
            conn.close()
            self.calculate_totals()
            self.save_btn.setText("💾 Update Invoice")
            self.table.viewport().update()
            
            print("Invoice data loaded successfully")
            
        except Exception as e:
            print(f"Error loading invoice data: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load invoice: {str(e)}")

    def save_invoice(self):
        """Invoice ကို database မှာသိမ်းမယ်"""
        if not self.client_cb.currentText().strip():
            QMessageBox.warning(self, "Error", "Please enter client company name!")
            return False
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            company_name = self.client_cb.currentText().strip()
            client = None
            
            if self.client_cb.currentIndex() > 0:
                client = self.client_cb.itemData(self.client_cb.currentIndex())
            
            client_id = None
            if client and isinstance(client, dict):
                client_id = client.get('id')
            
            if not client_id:
                # Client အသစ်ထည့်မယ်
                cursor.execute('''
                    INSERT INTO clients (name, abbr, addr1, c1_name, c1_pos, c1_ph, c1_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    company_name,
                    '',  # abbr empty for new clients
                    self.addr_cb.currentText() if self.addr_cb.currentText() else None,
                    self.contact_name.text(),
                    self.contact_pos.text(),
                    self.contact_ph.text(),
                    self.contact_em.text()
                ))
                client_id = cursor.lastrowid
            
            subtotal = 0
            amt_idx = self.get_col_index("Amount")
            for row in range(self.table.rowCount()):
                amt_item = self.table.item(row, amt_idx) if amt_idx != -1 else None
                if amt_item:
                    try:
                        amt = float(amt_item.text().replace(',', ''))
                        subtotal += amt
                    except:
                        pass
            
            tax = subtotal * 0.05 if self.tax_check.isChecked() else 0
            advance = float(self.advance_amt.text().replace(',', '')) if self.advance_amt.text() else 0
            grand_total = subtotal + tax - advance
            
            # === မိခင်ကုမ္ပဏီ ID ကိုရှာမယ် ===
            mother_company_id = None
            if hasattr(self, 'selected_mother_company') and self.selected_mother_company:
                mother_company_id = self.selected_mother_company.get('id')
            
            # အကယ်၍ mother_company_id မရှိသေးရင် default company ကိုရှာမယ်
            if not mother_company_id:
                # Default company ကိုရှာမယ်
                cursor.execute("SELECT id FROM companies WHERE is_default = 1 LIMIT 1")
                default = cursor.fetchone()
                if default:
                    mother_company_id = default[0]
                else:
                    # ပထမဆုံး company ကိုယူမယ်
                    cursor.execute("SELECT id FROM companies LIMIT 1")
                    first = cursor.fetchone()
                    if first:
                        mother_company_id = first[0]
            
            print(f"Mother company ID: {mother_company_id}")  # စစ်ဆေးရန်
            
            # Edit mode မဟုတ်ရင် invoice no အသစ်ထုတ်မယ်
            if not self.edit_mode:
                self.generate_new_invoice_no()
            
            invoice_no = self.inv_no.text()
            
            # ဒီ invoice no ရှိပြီးသားလားစစ်မယ် (edit mode မှာမစစ်ရဘူး)
            if not self.edit_mode:
                existing = cursor.execute(
                    "SELECT id FROM invoices WHERE invoice_no = ?", 
                    (invoice_no,)
                ).fetchone()
                
                if existing:
                    print(f"Invoice no {invoice_no} already exists, generating new one...")
                    self.generate_new_invoice_no()
                    invoice_no = self.inv_no.text()
            
            if self.edit_mode and self.current_invoice_id:
                # UPDATE - ပြင်ဆင်မယ်
                cursor.execute('''
                    UPDATE invoices SET
                        invoice_date = ?,
                        client_id = ?,
                        mother_company_id = ?,
                        company_name = ?,
                        address = ?,
                        contact_name = ?,
                        contact_pos = ?,
                        contact_ph = ?,
                        contact_email = ?,
                        subtotal = ?,
                        tax = ?,
                        advance = ?,
                        grand_total = ?,
                        status = ?,
                        inv_title = ?,
                        service_type = ?
                    WHERE id = ?
                ''', (
                    self.invoice_date.date().toString("yyyy-MM-dd"),
                    client_id,
                    mother_company_id,
                    company_name,
                    self.addr_cb.currentText() if self.addr_cb.currentText() else None,
                    self.contact_name.text() if self.show_name.isChecked() else None,
                    self.contact_pos.text() if self.show_pos.isChecked() else None,
                    self.contact_ph.text() if self.show_ph.isChecked() else None,
                    self.contact_em.text() if self.show_em.isChecked() else None,
                    subtotal,
                    tax,
                    advance,
                    grand_total,
                    'Pending',
                    self.inv_title.text(),
                    self.service_cat_cb.currentText(),
                    self.current_invoice_id
                ))
                
                # Delete old items
                cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (self.current_invoice_id,))
                invoice_id = self.current_invoice_id
                
                message = f"Invoice {invoice_no} Updated Successfully!"
                print(f"Update successful for invoice ID: {invoice_id}")
                
            else:
                # INSERT - အသစ်ထည့်မယ်
                cursor.execute('''
                    INSERT INTO invoices (
                        invoice_no, invoice_date, client_id, mother_company_id, company_name, address,
                        contact_name, contact_pos, contact_ph, contact_email,
                        subtotal, tax, advance, grand_total, status, inv_title, service_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    invoice_no,
                    self.invoice_date.date().toString("yyyy-MM-dd"),
                    client_id,
                    mother_company_id,
                    company_name,
                    self.addr_cb.currentText() if self.addr_cb.currentText() else None,
                    self.contact_name.text() if self.show_name.isChecked() else None,
                    self.contact_pos.text() if self.show_pos.isChecked() else None,
                    self.contact_ph.text() if self.show_ph.isChecked() else None,
                    self.contact_em.text() if self.show_em.isChecked() else None,
                    subtotal,
                    tax,
                    advance,
                    grand_total,
                    'Pending',
                    self.inv_title.text(),
                    self.service_cat_cb.currentText()
                ))
                
                invoice_id = cursor.lastrowid
                message = f"Invoice {invoice_no} Saved Successfully!"
            
            # Insert new items (ဒီအတိုင်းထား)
            qty_idx = self.get_col_index("Qty")
            price_idx = self.get_col_index("Unit Price")
            amt_idx = self.get_col_index("Amount")
            
            for row in range(self.table.rowCount()):
                desc_item = self.table.item(row, 0)
                qty_item = self.table.item(row, qty_idx) if qty_idx != -1 else None
                price_item = self.table.item(row, price_idx) if price_idx != -1 else None
                amt_item = self.table.item(row, amt_idx) if amt_idx != -1 else None
                
                if desc_item and desc_item.text().strip():
                    qty_val = 0
                    if qty_item and qty_item.text():
                        try:
                            qty_val = float(qty_item.text())
                        except:
                            qty_val = 0
                    
                    price_val = 0
                    if price_item and price_item.text():
                        try:
                            price_val = float(price_item.text().replace(',', ''))
                        except:
                            price_val = 0
                    
                    amt_val = 0
                    if amt_item and amt_item.text():
                        try:
                            amt_val = float(amt_item.text().replace(',', ''))
                        except:
                            amt_val = 0
                    
                    cursor.execute('''
                        INSERT INTO invoice_items (invoice_id, description, qty, unit_price, amount)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        invoice_id,
                        desc_item.text(),
                        qty_val,
                        price_val,
                        amt_val
                    ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "✅ Success", message)
            
            # Save ပြီးရင် ဘာလုပ်မလဲ
            if self.edit_mode:
                self.accept()
            else:
                self.clear_all_fields()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def clear_all_fields(self):
        """Form ထဲက အကွက်အားလုံးကိုရှင်းမယ်"""
        self.client_cb.setCurrentIndex(0)
        self.addr_cb.clear()
        self.addr_cb.setEditText("")
        
        self.contact_name.clear()
        self.contact_pos.clear()
        self.contact_ph.clear()
        self.contact_em.clear()
        
        self.show_name.setChecked(False)
        self.show_pos.setChecked(False)
        self.show_ph.setChecked(False)
        self.show_em.setChecked(False)
        
        self.table.setRowCount(0)
        self.add_item_row()
        
        self.tax_check.setChecked(False)
        self.advance_text.clear()
        self.advance_amt.setText("0")
        
        self.edit_mode = False
        self.current_invoice_id = None
        self.save_btn.setText("💾 Save Invoice")
        self.setWindowTitle("🏢 Professional Invoice Generator")
        
        # Client ရွေးထားရင် invoice no အသစ်ထုတ်မယ်
        if self.client_cb.currentIndex() > 0:
            self.generate_new_invoice_no()
        else:
            date_str = self.invoice_date.date().toString("ddMMyyyy")
            self.inv_no.setText(f"INV-001-{date_str}")

    def generate_new_invoice_no(self):
        """Client company ရဲ့ Abbr နဲ့ invoice နံပါတ်အသစ်ထုတ်မယ်"""
        try:
            client_abbr = 'INV'  # Default
            current_index = self.client_cb.currentIndex()
            
            # Client ရွေးထားရင် သူ့ရဲ့ abbr ကိုယူမယ်
            if current_index > 0:
                client = self.client_cb.itemData(current_index)
                if client and isinstance(client, dict):
                    client_abbr = client.get('abbr', 'INV')
            else:
                # Client အသစ်ဆိုရင် INV နဲ့ထုတ်
                client_abbr = 'INV'
            
            date_str = self.invoice_date.date().toString("ddMMyyyy")
            
            conn = get_db()
            result = conn.execute('''
                SELECT invoice_no FROM invoices 
                WHERE invoice_no LIKE ? 
                ORDER BY id DESC LIMIT 1
            ''', (f'{client_abbr}-%',)).fetchone()
            
            next_sequence = 1
            
            if result:
                last_invoice = result[0]
                try:
                    parts = last_invoice.split('-')
                    if len(parts) >= 2:
                        last_sequence = int(parts[1])
                        next_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    next_sequence = 1
            
            conn.close()
            
            new_invoice_no = f"{client_abbr}-{next_sequence:03d}-{date_str}"
            self.inv_no.setText(new_invoice_no)
            return new_invoice_no
            
        except Exception as e:
            print(f"Error generating invoice no: {e}")
            date_str = self.invoice_date.date().toString("ddMMyyyy")
            new_invoice_no = f"INV-001-{date_str}"
            self.inv_no.setText(new_invoice_no)
            return new_invoice_no

    def print_invoice(self):
        """Invoice ကို PDF အဖြစ်ထုတ်မယ်"""
        try:
            from .pdf_generator import InvoicePDFGenerator, number_to_words_mm

            # ── Mother Company အချက်အလက်ကို database ကနေ တိုက်ရိုက်ယူမယ် ───────
            mother_company_data = {
                'name': "N/A",
                'phone': "",
                'email': "",
                'address': "",
                'logo': None,
                'tax_number': "N/A",
                'bank_name': "",
                'beneficiary': "",
                'account_no': "",
                'kpay_no': ""
            }

            if self.selected_mother_company:
                mc = self.selected_mother_company
                mother_company_data.update({
                    'name': mc.get('name', self.company_name_display.text() or "N/A"),
                    'phone': mc.get('phone', ""),
                    'email': mc.get('email', ""),
                    'address': mc.get('address', ""),
                    'logo': mc.get('logo') if mc.get('logo') and os.path.exists(mc.get('logo')) else None,
                    'tax_number': mc.get('tax_number', self.company_tax_display.text() or "N/A"),
                    'bank_name': mc.get('bank_name', ""),
                    'beneficiary': mc.get('beneficiary', ""),
                    'account_no': mc.get('account_no', ""),
                    'kpay_no': mc.get('kpay_no', "")
                })
            else:
                # fallback အနေနဲ့ UI ကနေ ယူထားတာကို သုံးလို့ရတယ် (ဒါပေမယ့် database က ပိုယုံကြည်စိတ်ချရတယ်)
                details_text = self.company_details_display.text()
                mother_company_data['name'] = self.company_name_display.text() or "N/A"
                mother_company_data['tax_number'] = self.company_tax_display.text() or "N/A"

            # ── Invoice data ဖွဲ့စည်းမယ် ────────────────────────────────────────
            raw_service = self.service_cat_cb.currentText()
            service_type_clean = raw_service.split(' ', 1)[-1].strip() if ' ' in raw_service else raw_service.strip()

            inv_title_text = self.inv_title.text().strip() or "PROFESSIONAL SERVICE INVOICE"

            invoice_data = {
                'mother_company': mother_company_data,
                'client': {
                    'company_name': self.client_cb.currentText().strip(),
                    'address': self.addr_cb.currentText().strip(),
                    'contact_name': self.contact_name.text().strip(),
                    'contact_pos': self.contact_pos.text().strip(),
                    'contact_ph': self.contact_ph.text().strip(),
                    'contact_email': self.contact_em.text().strip(),
                    'show_position': self.show_pos.isChecked(),
                    'show_phone': self.show_ph.isChecked(),
                    'show_email': self.show_em.isChecked()
                },
                'invoice': {
                    'number': self.inv_no.text().strip(),
                    'date': self.invoice_date.date().toString("dd MMM yyyy"),
                    'service_type': service_type_clean,
                    'inv_title': inv_title_text,
                },
                'payment': {
                    'bank_name': mother_company_data['bank_name'],
                    'beneficiary': mother_company_data['beneficiary'],
                    'account_no': mother_company_data['account_no'],
                    'kpay_no': mother_company_data['kpay_no'],
                },
                'items': [],
                'totals': {}
            }

            # Items စုဆောင်းခြင်း
            qty_idx   = self.get_col_index("Qty")
            price_idx = self.get_col_index("Unit Price")
            amt_idx   = self.get_col_index("Amount")

            for row in range(self.table.rowCount()):
                desc_item  = self.table.item(row, 0)
                qty_item   = self.table.item(row, qty_idx)   if qty_idx   != -1 else None
                price_item = self.table.item(row, price_idx) if price_idx != -1 else None
                amt_item   = self.table.item(row, amt_idx)   if amt_idx   != -1 else None

                if desc_item and desc_item.text().strip():
                    def safe_float(item_obj):
                        if not item_obj:
                            return 0.0
                        try:
                            return float(item_obj.text().replace(',', ''))
                        except:
                            return 0.0

                    invoice_data['items'].append({
                        'description': desc_item.text().strip(),
                        'qty': safe_float(qty_item),
                        'unit_price': safe_float(price_item),
                        'amount': safe_float(amt_item),
                    })

            # Totals တွက်ခြင်း
            subtotal = sum(item['amount'] for item in invoice_data['items'])
            tax = subtotal * 0.05 if self.tax_check.isChecked() else 0
            advance = float(self.advance_amt.text().replace(',', '')) if self.advance_amt.text().strip() else 0
            grand_total = subtotal + tax - advance

            invoice_data['totals'] = {
                'subtotal': subtotal,
                'tax': tax,
                'advance': advance,
                'grand_total': grand_total,
                'amount_in_words': number_to_words_mm(int(round(grand_total))),
            }

            # PDF သိမ်းတဲ့ dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice PDF",
                f"invoice_{self.inv_no.text().replace('/', '-')}.pdf",
                "PDF Files (*.pdf)"
            )

            if file_path:
                generator = InvoicePDFGenerator(file_path)
                generator.create_invoice(invoice_data)
                QMessageBox.information(
                    self,
                    "✅ PDF ထုတ်ပြီးပါပြီ",
                    f"သိမ်းပြီးပါပြီ\n\n{file_path}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"PDF ထုတ်မရပါ\n\n{str(e)}")
            import traceback
            traceback.print_exc()
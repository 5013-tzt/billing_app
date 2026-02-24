import calendar
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, QLineEdit,
    QLabel, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QCheckBox, QMessageBox, QScrollArea, QWidget, QDateEdit,
    QFrame, QSplitter, QFormLayout, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QColor
from database import get_db
from .styles import STYLESHEET
from .pdf_generator import InvoicePDFGenerator
import os

class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice_id=None, mode='new'):
        super().__init__(parent)
        
        if mode == 'edit' and invoice_id:
            self.setWindowTitle(f"✏️ Edit Invoice (ID: {invoice_id})")
        else:
            self.setWindowTitle("🏢 Professional Invoice Generator")
            
        self.resize(1400, 900)
        self.setMinimumSize(1300, 800)
        
        # UI Table ထဲက widget တွေအတွက် Custom Style
        self.setStyleSheet(STYLESHEET + """
            QTableWidget {
                gridline-color: #333;
                border: 1px solid #333;
                background-color: #121212;
                border-radius: 4px;
            }
            QTableWidget QLineEdit, QTableWidget QDateEdit {
                border: none;
                background: transparent;
                padding: 4px;
                color: #e0e0e0;
            }
            QTableWidget QLineEdit:focus {
                background-color: #2a2a2a;
                border-radius: 2px;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #333;
                font-weight: bold;
            }
        """)
        
        self.invoice_type = "monthly"
        self.clients_data = []
        self.mother_companies_data = []
        self.selected_mother_company = None
        self.updating_totals = False
        self.current_invoice_id = invoice_id
        self.edit_mode = (mode == 'edit')
        
        self.init_ui()
        self.load_clients_list()
        self.load_mother_companies()
        
        if self.edit_mode and self.current_invoice_id:
            self.load_invoice_data(self.current_invoice_id)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)

        # === 1. TOP BAR: Mother Company Info ===
        company_bar = QFrame()
        company_bar.setStyleSheet("""
            QFrame { background-color: #1e1e1e; border: 1px solid #333; border-radius: 12px; padding: 15px; }
        """)
        company_layout = QHBoxLayout(company_bar)
        
        self.company_logo = QLabel("No Logo")
        self.company_logo.setFixedSize(70, 70)
        self.company_logo.setStyleSheet("border-radius: 35px; background-color: #2a2a2a; color: #666;")
        self.company_logo.setAlignment(Qt.AlignCenter)
        company_layout.addWidget(self.company_logo)
        
        info_vbox = QVBoxLayout()
        self.company_name_display = QLabel("Mother Company")
        self.company_name_display.setStyleSheet("font-size: 20px; font-weight: bold; color: #BB86FC;")
        self.company_details_display = QLabel("Select a company to see details")
        self.company_details_display.setStyleSheet("color: #999;")
        info_vbox.addWidget(self.company_name_display)
        info_vbox.addWidget(self.company_details_display)
        company_layout.addLayout(info_vbox, 1)
        
        tax_vbox = QVBoxLayout()
        tax_vbox.setAlignment(Qt.AlignRight)
        tax_vbox.addWidget(QLabel("TAX ID"), 0, Qt.AlignRight)
        self.company_tax_display = QLabel("N/A")
        self.company_tax_display.setStyleSheet("font-weight: bold; color: #f59e0b; font-size: 16px;")
        tax_vbox.addWidget(self.company_tax_display, 0, Qt.AlignRight)
        company_layout.addLayout(tax_vbox)
        
        layout.addWidget(company_bar)

        # === 2. CONFIGURATION & CLIENT INFO (Grid System) ===
        config_gb = QGroupBox("📋 General Information")
        grid = QGridLayout(config_gb)
        grid.setSpacing(15)
        grid.setContentsMargins(20, 20, 20, 20)

        # Row 0: Invoice Basic
        grid.addWidget(QLabel("Invoice Type:"), 0, 0)
        self.inv_type_cb = QComboBox()
        self.inv_type_cb.addItems(["📅 Monthly", "📊 Daily"])
        self.inv_type_cb.currentTextChanged.connect(self.on_invoice_type_changed)
        grid.addWidget(self.inv_type_cb, 0, 1)

        grid.addWidget(QLabel("Mother Co:"), 0, 2)
        self.mother_company_cb = QComboBox()
        self.mother_company_cb.currentIndexChanged.connect(self.on_mother_company_selected)
        grid.addWidget(self.mother_company_cb, 0, 3)

        grid.addWidget(QLabel("Inv No:"), 0, 4)
        self.inv_no = QLineEdit()
        self.inv_no.setReadOnly(True)
        self.inv_no.setPlaceholderText("Auto-generated")
        grid.addWidget(self.inv_no, 0, 5)

        # Row 1: Service & Date
        grid.addWidget(QLabel("Service:"), 1, 0)
        self.service_cat_cb = QComboBox()
        self.service_cat_cb.setEditable(True)
        self.service_cat_cb.addItems(["🛡️ Security", "🧹 Cleaning", "🔧 Maintenance"])
        grid.addWidget(self.service_cat_cb, 1, 1)

        grid.addWidget(QLabel("Date:"), 1, 2)
        self.invoice_date = QDateEdit()
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.dateChanged.connect(self.calculate_totals)
        grid.addWidget(self.invoice_date, 1, 3)

        grid.addWidget(QLabel("Status:"), 1, 4)
        self.received_status = QLabel("📥 Not Received")
        self.received_status.setStyleSheet("color: #f59e0b; font-weight: bold;")
        grid.addWidget(self.received_status, 1, 5)

        # Row 2: Title (Full Width)
        grid.addWidget(QLabel("Invoice Title:"), 2, 0)
        self.inv_title = QLineEdit("PROFESSIONAL SERVICE INVOICE")
        grid.addWidget(self.inv_title, 2, 1, 1, 5)

        layout.addWidget(config_gb)

        # === 3. CLIENT SECTION ===
        client_gb = QGroupBox("🏢 Client Information")
        client_grid = QGridLayout(client_gb)
        client_grid.setSpacing(12)

        client_grid.addWidget(QLabel("Client Co:"), 0, 0)
        self.client_cb = QComboBox()
        self.client_cb.setEditable(True)
        self.client_cb.currentIndexChanged.connect(self.on_client_selected)
        client_grid.addWidget(self.client_cb, 0, 1)

        client_grid.addWidget(QLabel("Address:"), 0, 2)
        self.addr_cb = QComboBox()
        self.addr_cb.setEditable(True)
        client_grid.addWidget(self.addr_cb, 0, 3)

        # Contact Details Row
        contact_lay = QHBoxLayout()
        self.contact_name = QLineEdit(); self.contact_name.setPlaceholderText("Name")
        self.contact_pos = QLineEdit(); self.contact_pos.setPlaceholderText("Position")
        self.contact_ph = QLineEdit(); self.contact_ph.setPlaceholderText("Phone")
        self.contact_em = QLineEdit(); self.contact_em.setPlaceholderText("Email")
        
        self.show_name = QCheckBox(); self.show_pos = QCheckBox()
        self.show_ph = QCheckBox(); self.show_em = QCheckBox()

        for w, c in [(self.contact_name, self.show_name), (self.contact_pos, self.show_pos), 
                     (self.contact_ph, self.show_ph), (self.contact_em, self.show_em)]:
            contact_lay.addWidget(w)
            contact_lay.addWidget(c)
        
        client_grid.addWidget(QLabel("Contact:"), 1, 0)
        client_grid.addLayout(contact_lay, 1, 1, 1, 3)

        layout.addWidget(client_gb)

        # === 4. SERVICE DETAILS (TABLE) ===
        items_gb = QGroupBox("📦 Service Details")
        items_lay = QVBoxLayout(items_gb)
        
        top_table_lay = QHBoxLayout()
        self.work_day_check = QCheckBox("✅ Enable Working Days Calculation")
        self.work_day_check.stateChanged.connect(self.on_working_days_toggled)
        top_table_lay.addWidget(self.work_day_check)
        top_table_lay.addStretch()
        items_lay.addLayout(top_table_lay)
        
        self.table = QTableWidget(0, 5)
        self.table.setMinimumHeight(280)
        self.table.verticalHeader().setDefaultSectionSize(45) # Row အမြင့်ကို ပုံသေညှိ
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.itemChanged.connect(self.on_cell_changed)
        
        self.update_table_headers()
        items_lay.addWidget(self.table)
        
        self.add_btn = QPushButton("➕ Add New Line")
        self.add_btn.setFixedWidth(150)
        self.add_btn.setStyleSheet("background-color: #333; height: 35px;")
        self.add_btn.clicked.connect(self.add_item_row)
        items_lay.addWidget(self.add_btn)
        
        layout.addWidget(items_gb)

        # === 5. FINANCIAL SUMMARY ===
        summary_gb = QGroupBox("💰 Summary")
        summary_lay = QHBoxLayout(summary_gb)
        
        # Financial Cards
        def create_card(label, color):
            frame = QFrame()
            frame.setStyleSheet(f"background-color: #1a1a1a; border-radius: 8px; border-left: 4px solid {color};")
            lay = QVBoxLayout(frame)
            title = QLabel(label); title.setStyleSheet("font-size: 11px; color: #888;")
            val = QLabel("0 MMK"); val.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {color};")
            lay.addWidget(title); lay.addWidget(val)
            return frame, val

        sub_f, self.subtotal_lbl = create_card("SUBTOTAL", "#BB86FC")
        tax_f, self.tax_lbl = create_card("COMMERCIAL TAX (5%)", "#f59e0b")
        total_f, self.grand_total_lbl = create_card("GRAND TOTAL", "#10b981")

        summary_lay.addWidget(sub_f, 1)
        summary_lay.addWidget(tax_f, 1)
        
        # Middle (Tax Toggle & Advance)
        mid_vbox = QVBoxLayout()
        self.tax_check = QCheckBox("Apply Tax")
        self.tax_check.stateChanged.connect(self.calculate_totals)
        
        adv_hbox = QHBoxLayout()
        self.advance_text = QLineEdit(); self.advance_text.setPlaceholderText("Advance Description")
        self.advance_amt = QLineEdit("0"); self.advance_amt.setFixedWidth(100)
        self.advance_amt.textChanged.connect(self.calculate_totals)
        adv_hbox.addWidget(self.advance_text); adv_hbox.addWidget(self.advance_amt)
        
        mid_vbox.addWidget(self.tax_check)
        mid_vbox.addLayout(adv_hbox)
        summary_lay.addLayout(mid_vbox, 1)
        
        summary_lay.addWidget(total_f, 1)
        layout.addWidget(summary_gb)

        # Final stretch and Scroll setup
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # === FOOTER BUTTONS ===
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #333;")
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(30, 0, 30, 0)

        self.list_btn = QPushButton("📋 Invoice List")
        self.print_btn = QPushButton("🖨️ Print")
        self.export_btn = QPushButton("📊 Export")
        self.save_btn = QPushButton("💾 Save Invoice")
        
        self.save_btn.setStyleSheet("background-color: #10b981; font-weight: bold; width: 150px; height: 45px;")
        
        for btn in [self.list_btn, self.print_btn, self.export_btn]:
            btn.setFixedHeight(40)
            btn.setFixedWidth(110)
            footer_lay.addWidget(btn)
        
        footer_lay.addStretch()
        footer_lay.addWidget(self.save_btn)
        main_layout.addWidget(footer)

        # Connections
        self.list_btn.clicked.connect(self.show_invoice_list)
        self.save_btn.clicked.connect(self.save_invoice)
        
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
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
            headers.extend(["Start Date", "End Date", "Days"])
        elif use_work_days:
            headers.append("Days")
        
        headers.extend(["Qty", "Unit Price", "Amount", "Del"])
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        header = self.table.horizontalHeader()
        
        # Description column - အကျယ်ဆုံး
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Column widths သတ်မှတ်မယ်
        for i in range(1, len(headers)):
            if headers[i] == "Del":
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 50)  # Delete button column
            elif headers[i] in ["Qty", "Days"]:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 80)  # နံပါတ်ထည့်တဲ့ column
            elif headers[i] == "Unit Price":
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 120)  # ဈေးနှုန်းထည့်တဲ့ column
            elif headers[i] == "Amount":
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 130)  # စုစုပေါင်းပြတဲ့ column
            elif headers[i] in ["Start Date", "End Date"]:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 110)  # ရက်စွဲ columns
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
            del_btn = QPushButton("🗑️")
            del_btn.setStyleSheet("color: #ef4444; border: none; font-size: 16px; background: transparent;")
            del_btn.clicked.connect(self.delete_specific_row)
            self.table.setCellWidget(row, del_idx, del_btn)
        
        # Start/End Dates if Daily
        is_daily = self.inv_type_cb.currentText() == "📊 Daily"
        if is_daily:
            start_idx = self.get_col_index("Start Date")
            if start_idx != -1:
                for i in range(2):
                    de = QDateEdit()
                    de.setCalendarPopup(True)
                    de.setDate(QDate.currentDate())
                    de.setStyleSheet("""
                        QDateEdit {
                            font-size: 12px;
                            padding: 4px;
                            min-height: 25px;
                        }
                    """)
                    de.dateChanged.connect(lambda checked, r=row: self.calculate_daily_days(r))
                    self.table.setCellWidget(row, start_idx + i, de)
        
        # ကျန်တဲ့ columns တွေအတွက် items တွေကို editable ဖြစ်အောင်လုပ်မယ်
        qty_idx = self.get_col_index("Qty")
        price_idx = self.get_col_index("Unit Price")
        days_idx = self.get_col_index("Days")
        
        # Qty column
        if qty_idx != -1:
            item = self.table.item(row, qty_idx)
            if not item:
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(row, qty_idx, item)
        
        # Unit Price column
        if price_idx != -1:
            item = self.table.item(row, price_idx)
            if not item:
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(row, price_idx, item)
        
        # Days column
        if days_idx != -1:
            item = self.table.item(row, days_idx)
            if not item:
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(row, days_idx, item)

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
        for r in range(self.table.rowCount()): self.refresh_row_widgets(r)
        self.calculate_totals()
        
        for row, data in enumerate(saved_data):
            self.refresh_row_widgets(row)
            self.table.setItem(row, 0, QTableWidgetItem(data["desc"]))
            
            nq = self.get_col_index("Qty")
            if nq != -1:
                if not self.table.item(row, nq):
                    item = QTableWidgetItem(data["qty"])
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, nq, item)
                else:
                    self.table.item(row, nq).setText(data["qty"])
            
            np = self.get_col_index("Unit Price")
            if np != -1:
                if not self.table.item(row, np):
                    item = QTableWidgetItem(data["price"])
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, np, item)
                else:
                    self.table.item(row, np).setText(data["price"])
            
            nd = self.get_col_index("Days")
            if nd != -1:
                if not self.table.item(row, nd):
                    item = QTableWidgetItem(data["days"])
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, nd, item)
                else:
                    self.table.item(row, nd).setText(data["days"])
        
        self.updating_totals = False
        self.calculate_totals()

    def add_item_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.refresh_row_widgets(row)

    def delete_specific_row(self):
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
        item = self.table.item(row, 0)
        if item:
            item.setText("")
        self.refresh_row_widgets(row)
        self.calculate_totals()

    def on_cell_changed(self, item):
        # Numeric column တွေမှာ စာရိုက်ရင် total ပြန်တွက်ဖို့
        if not self.updating_totals:
            self.calculate_totals()
            
            qty_idx = self.get_col_index("Qty")
            price_idx = self.get_col_index("Unit Price")
            days_idx = self.get_col_index("Days")
            
            # If Qty or Unit Price changed, update amount
            if col == qty_idx or col == price_idx:
                self.calculate_totals()
            
            # If Days changed in working days mode
            if col == days_idx:
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
            end_widget = self.table.cellWidget(row, s_idx + 1)
            
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
            
            # === ပျောက်နေတဲ့ data တွေကို ဖြည့်မယ် ===
            # Title (inv_title)
            if invoice['inv_title']:
                self.inv_title.setText(invoice['inv_title'])
            else:
                self.inv_title.setText("PROFESSIONAL SERVICE INVOICE")
            
            # Service Type (service_type)
            if invoice['service_type']:
                # service_type ကို combo box မှာရှာမယ်
                service_text = invoice['service_type']
                found_service = False
                for i in range(self.service_cat_cb.count()):
                    # Emoji ပါတဲ့ items တွေကို စစ်မယ်
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

            # ── BUG 1 FIX: service_type ထဲက emoji ကိုဖြုတ်မယ် ──────────────
            raw_service = self.service_cat_cb.currentText()
            # emoji နဲ့ space ကို strip (🛡️ Security → Security)
            service_type_clean = raw_service.split(' ', 1)[-1].strip() if ' ' in raw_service else raw_service.strip()

            # ── BUG 2 FIX: inv_title ကို pass လုပ်မယ် ──────────────────────
            inv_title_text = self.inv_title.text().strip()

            invoice_data = {
                'mother_company': {
                    'name': self.company_name_display.text(),
                    'phone': (
                        self.company_details_display.text()
                        .split('|')[0].replace('📞', '').strip()
                        if '📞' in self.company_details_display.text() else ''
                    ),
                    'email': (
                        self.company_details_display.text()
                        .split('|')[1].replace('✉️', '').strip()
                        if '✉️' in self.company_details_display.text() else ''
                    ),
                    'address': (
                        self.company_details_display.text()
                        .split('|')[2].replace('📍', '').strip()
                        if '📍' in self.company_details_display.text() else ''
                    ),
                    'logo': self.selected_mother_company.get('logo') if self.selected_mother_company else None
                },
                'client': {
                    'company_name': self.client_cb.currentText(),
                    'address': self.addr_cb.currentText(),
                    'contact_name': self.contact_name.text(),
                    'contact_pos': self.contact_pos.text(),
                    'contact_ph': self.contact_ph.text(),
                    'contact_email': self.contact_em.text(),
                    'show_position': self.show_pos.isChecked(),
                    'show_phone': self.show_ph.isChecked(),
                    'show_email': self.show_em.isChecked()
                },
                'invoice': {
                    'number': self.inv_no.text(),
                    'date': self.invoice_date.date().toString("dd MMM yyyy"),
                    'service_type': service_type_clean,
                    'inv_title': inv_title_text,
                },
                'payment': {
                    'bank_name':   self.selected_mother_company.get('bank_name',   '') if self.selected_mother_company else '',
                    'beneficiary': self.selected_mother_company.get('beneficiary', '') if self.selected_mother_company else '',
                    'account_no':  self.selected_mother_company.get('account_no',  '') if self.selected_mother_company else '',
                    'kpay_no':     self.selected_mother_company.get('kpay_no',     '') if self.selected_mother_company else '',
                },
                'items': [],
                'totals': {}
            }

            # ── Items စုဆောင်းမယ် ───────────────────────────────────────────
            qty_idx   = self.get_col_index("Qty")
            price_idx = self.get_col_index("Unit Price")
            amt_idx   = self.get_col_index("Amount")

            for row in range(self.table.rowCount()):
                desc_item  = self.table.item(row, 0)
                qty_item   = self.table.item(row, qty_idx)   if qty_idx   != -1 else None
                price_item = self.table.item(row, price_idx) if price_idx != -1 else None
                amt_item   = self.table.item(row, amt_idx)   if amt_idx   != -1 else None

                if desc_item and desc_item.text().strip():
                    def _to_float(item_obj, remove_comma=True):
                        try:
                            t = item_obj.text().replace(',', '') if remove_comma else item_obj.text()
                            return float(t)
                        except:
                            return 0.0

                    invoice_data['items'].append({
                        'description': desc_item.text(),
                        'qty':        _to_float(qty_item)   if qty_item   else 0,
                        'unit_price': _to_float(price_item) if price_item else 0,
                        'amount':     _to_float(amt_item)   if amt_item   else 0,
                    })

            # ── Totals တွက်မယ် ──────────────────────────────────────────────
            subtotal    = sum(i['amount'] for i in invoice_data['items'])
            tax         = subtotal * 0.05 if self.tax_check.isChecked() else 0
            adv_text    = self.advance_amt.text().replace(',', '')
            advance     = float(adv_text) if adv_text else 0

            grand_total = subtotal + tax - advance

            # ── BUG 3 FIX: number_to_words_mm() ကိုခေါ်မယ် ─────────────────
            invoice_data['totals'] = {
                'subtotal':        subtotal,
                'tax':             tax,
                'advance':         advance,
                'grand_total':     grand_total,
                'amount_in_words': number_to_words_mm(int(grand_total)),  # BUG 3 FIX
            }

            # ── File save dialog ─────────────────────────────────────────────
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice PDF",
                f"invoice_{self.inv_no.text()}.pdf",
                "PDF Files (*.pdf)"
            )

            if file_path:
                generator = InvoicePDFGenerator(file_path)
                generator.create_invoice(invoice_data)
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "✅ Success",
                    f"Invoice PDF saved!\n\n{file_path}"
                )

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")
            import traceback
            traceback.print_exc()
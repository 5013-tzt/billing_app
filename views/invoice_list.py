import sqlite3
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QAbstractItemView,
    QLineEdit, QWidget, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from database import get_db

class InvoiceListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Invoice List")
        self.resize(1400, 700)
        self.setMinimumSize(1200, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-weight: bold;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by invoice no, company, service type, or title...")
        self.search_input.setMinimumWidth(350)
        self.search_input.textChanged.connect(self.filter_invoices)
        search_layout.addWidget(self.search_input)
        
        search_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setFixedWidth(120)
        self.refresh_btn.setFixedHeight(35)
        self.refresh_btn.clicked.connect(self.load_invoices)
        search_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Table - Column 9 ခု
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Invoice No", "Date", "Company", "Service Type", "Title", "Amount", "Status", "Actions"
        ])
        
        # Table settings - Column widths ချိန်ညှိခြင်း
        header = self.table.horizontalHeader()
        
        # Fixed width columns
        header.setSectionResizeMode(0, QHeaderView.Fixed)      # ID
        header.setSectionResizeMode(1, QHeaderView.Fixed)      # Invoice No
        header.setSectionResizeMode(2, QHeaderView.Fixed)      # Date
        header.setSectionResizeMode(4, QHeaderView.Fixed)      # Service Type
        header.setSectionResizeMode(5, QHeaderView.Fixed)      # Title
        header.setSectionResizeMode(6, QHeaderView.Fixed)      # Amount
        header.setSectionResizeMode(7, QHeaderView.Fixed)      # Status
        header.setSectionResizeMode(8, QHeaderView.Fixed)      # Actions
        
        # Company column - Stretch လုပ်မယ်
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        # Set specific widths
        self.table.setColumnWidth(0, 50)      # ID
        self.table.setColumnWidth(1, 120)     # Invoice No
        self.table.setColumnWidth(2, 90)      # Date
        self.table.setColumnWidth(4, 100)     # Service Type
        self.table.setColumnWidth(5, 150)     # Title
        self.table.setColumnWidth(6, 120)     # Amount
        self.table.setColumnWidth(7, 80)      # Status
        self.table.setColumnWidth(8, 120)     # Actions
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        layout.addWidget(self.table)
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_pdf_btn = QPushButton("💾 Save as PDF")
        self.save_pdf_btn.setFixedHeight(40)
        self.save_pdf_btn.setFixedWidth(150)
        self.save_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_pdf_btn.clicked.connect(self.save_invoice_as_pdf)
        button_layout.addWidget(self.save_pdf_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setFixedHeight(40)
        self.edit_btn.setFixedWidth(120)
        self.edit_btn.setStyleSheet("color: #f39c12; font-weight: bold;")
        self.edit_btn.clicked.connect(self.edit_selected_invoice)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setFixedWidth(120)
        self.delete_btn.setStyleSheet("color: #dc3545; font-weight: bold;")
        self.delete_btn.clicked.connect(self.delete_selected_invoice)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedHeight(40)
        self.close_btn.setFixedWidth(120)
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Load data
        self.load_invoices()
    
    def load_invoices(self):
        """
        Invoice list ကို database ကနေ load မယ်။

        BUG FIX: SQL query မှာ service_type အဖြစ်
                 invoice_items.description ကို subquery နဲ့ alias လုပ်ထားတာ မှားနေတာ —
                 invoices.service_type column တိုက်ရိုက်ယူမယ်။
        """
        try:
            self.table.setRowCount(0)

            conn = get_db()

            rows = conn.execute("""
                SELECT
                    i.id,
                    i.invoice_no,
                    i.invoice_date,
                    i.company_name,
                    i.service_type,    -- BUG FIX: invoices.service_type တိုက်ရိုက်
                    i.inv_title,
                    i.grand_total,
                    i.status
                FROM invoices i
                ORDER BY i.id DESC
            """).fetchall()

            for row in rows:
                self.add_invoice_row(row)

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load invoices: {str(e)}")
            print(f"SQL Error: {e}")
    
    def add_invoice_row(self, row_data):
        """Invoice row တစ်ခုထည့်မယ် (Column 9 ခု)"""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # ID (0)
        id_item = QTableWidgetItem(str(row_data[0]))
        id_item.setData(Qt.UserRole, row_data[0])
        self.table.setItem(row_position, 0, id_item)
        
        # Invoice No (1)
        inv_no_item = QTableWidgetItem(row_data[1] if row_data[1] else "")
        inv_no_item.setData(Qt.UserRole, row_data[1])
        self.table.setItem(row_position, 1, inv_no_item)
        
        # Date (2)
        date_item = QTableWidgetItem(row_data[2] if row_data[2] else "")
        self.table.setItem(row_position, 2, date_item)
        
        # Company (3) - Stretch column
        company_item = QTableWidgetItem(row_data[3] if row_data[3] else "")
        self.table.setItem(row_position, 3, company_item)
        
        # Service Type (4) - from first invoice item
        service_item = QTableWidgetItem(row_data[4] if row_data[4] else "N/A")
        self.table.setItem(row_position, 4, service_item)
        
        # Title (5) - from invoices
        title_item = QTableWidgetItem(row_data[5] if row_data[5] else "")
        self.table.setItem(row_position, 5, title_item)
        
        # Amount (6)
        amount = float(row_data[6]) if row_data[6] else 0
        amount_item = QTableWidgetItem(f"{amount:,.0f} MMK")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amount_item.setData(Qt.UserRole, amount)
        self.table.setItem(row_position, 6, amount_item)
        
        # Status (7)
        status_text = row_data[7] if row_data[7] else "Pending"
        status_item = QTableWidgetItem(status_text)
        
        # အရောင်သတ်မှတ်ခြင်း
        if status_text.lower() == "paid":
            status_item.setForeground(Qt.darkGreen)
            status_item.setBackground(QColor(230, 255, 230))
        elif status_text.lower() == "pending":
            status_item.setForeground(QColor(255, 140, 0))
            status_item.setBackground(QColor(255, 245, 230))
        else:
            status_item.setForeground(Qt.darkBlue)
            status_item.setBackground(QColor(230, 240, 255))
            
        self.table.setItem(row_position, 7, status_item)
        
        # Actions (8)
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(2, 2, 2, 2)
        actions_layout.setSpacing(2)
        
        # PDF Save button
        pdf_btn = QPushButton("💾")
        pdf_btn.setFixedSize(30, 30)
        pdf_btn.setToolTip("Save as PDF")
        pdf_btn.setStyleSheet("color: #10b981;")
        pdf_btn.clicked.connect(lambda checked, r=row_position: self.save_invoice_pdf_at_row(r))
        actions_layout.addWidget(pdf_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 30)
        edit_btn.setToolTip("Edit")
        edit_btn.setStyleSheet("color: #f39c12;")
        edit_btn.clicked.connect(lambda checked, r=row_position: self.edit_invoice_at_row(r))
        actions_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setToolTip("Delete")
        delete_btn.setStyleSheet("color: #dc3545;")
        delete_btn.clicked.connect(lambda checked, r=row_position: self.delete_invoice_at_row(r))
        actions_layout.addWidget(delete_btn)
        
        self.table.setCellWidget(row_position, 8, actions_widget)
    
    def filter_invoices(self):
        """Search input နဲ့ filter လုပ်မယ်"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = False
            for col in [1, 2, 3, 4, 5]:  # Invoice No, Date, Company, Service Type, Title
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    # အောက်ပါ method တွေအားလုံး မူလအတိုင်းပဲကျန်ပါတယ်
    def get_selected_invoice_id(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            id_item = self.table.item(current_row, 0)
            if id_item:
                return int(id_item.text())
        return None
    
    def save_invoice_as_pdf(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.save_invoice_pdf_at_row(current_row)
        else:
            QMessageBox.information(self, "Info", "Please select an invoice to save as PDF")
    
    def save_invoice_pdf_at_row(self, row):
        try:
            inv_id_item = self.table.item(row, 0)
            inv_no_item = self.table.item(row, 1)
            
            if not inv_id_item or not inv_no_item:
                return
            
            invoice_id = int(inv_id_item.text())
            invoice_no = inv_no_item.text()
            
            invoice_data = self.get_invoice_data_for_pdf(invoice_id)
            
            if not invoice_data:
                QMessageBox.warning(self, "Error", "Could not load invoice data")
                return
            
            from PySide6.QtWidgets import QFileDialog
            
            default_filename = f"invoice_{invoice_no}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'
                
                from .pdf_generator import InvoicePDFGenerator
                generator = InvoicePDFGenerator(file_path)
                generator.create_invoice(invoice_data)
                
                QMessageBox.information(
                    self,
                    "✅ Success",
                    f"Invoice PDF saved successfully!\n\nFile: {file_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def get_invoice_data_for_pdf(self, invoice_id):
        """
        Database ကနေ invoice data ယူပြီး PDF generator အတွက် format လုပ်မယ်။

        BUG 1 FIX: load_invoices() SQL မှာ invoice_items.description ကို
                   service_type အဖြစ် alias လုပ်ထားလို့ မှားနေတာ —
                   ဒီ method မှာ invoices.service_type တိုက်ရိုက်ယူမယ်။

        BUG 2 FIX: invoice dict ထဲမှာ 'service_type' empty ပေးထားပြီး
                   'inv_title' လုံးဝမပါဘဲ 'subject' ပဲပါနေတာ ပြင်မယ်။
        """
        try:
            conn = get_db()

            invoice = conn.execute('''
                SELECT i.*,
                    c.c1_name, c.c1_pos, c.c1_ph, c.c1_em,
                    m.name        AS mother_name,
                    m.phone       AS mother_phone,
                    m.email       AS mother_email,
                    m.address     AS mother_address,
                    m.logo        AS mother_logo,
                    m.bank_name   AS mother_bank_name,
                    m.beneficiary AS mother_beneficiary,
                    m.account_no  AS mother_account_no,
                    m.kpay_no     AS mother_kpay_no
                FROM invoices i
                LEFT JOIN clients  c ON i.client_id          = c.id
                LEFT JOIN companies m ON i.mother_company_id = m.id
                WHERE i.id = ?
            ''', (invoice_id,)).fetchone()

            if not invoice:
                conn.close()
                return None

            items = conn.execute('''
                SELECT * FROM invoice_items
                WHERE invoice_id = ?
                ORDER BY id
            ''', (invoice_id,)).fetchall()

            conn.close()

            # ── BUG 1 FIX: invoices.service_type တိုက်ရိုက်ယူ ─────────────
            service_type = invoice['service_type'] or ''

            # ── BUG 2 FIX: inv_title ကို pass လုပ်မယ် ───────────────────────
            inv_title = invoice['inv_title'] or ''

            # amount_in_words generate ─────────────────────────────────────
            from .pdf_generator import number_to_words_mm
            grand_total = invoice['grand_total'] or 0
            amount_words = number_to_words_mm(int(grand_total))

            invoice_data = {
                'mother_company': {
                    'name':    invoice['mother_name']    or '',
                    'phone':   invoice['mother_phone']   or '',
                    'email':   invoice['mother_email']   or '',
                    'address': invoice['mother_address'] or '',
                    'logo':    invoice['mother_logo']    or ''
                },
                'client': {
                    'company_name':  invoice['company_name']  or '',
                    'address':       invoice['address']        or '',
                    'contact_name':  invoice['contact_name']  or invoice['c1_name'] or '',
                    'contact_pos':   invoice['contact_pos']   or invoice['c1_pos']  or '',
                    'contact_ph':    invoice['contact_ph']    or invoice['c1_ph']   or '',
                    'contact_email': invoice['contact_email'] or invoice['c1_em']   or '',
                    'show_position': bool(invoice['contact_pos']),
                    'show_phone':    bool(invoice['contact_ph']),
                    'show_email':    bool(invoice['contact_email'])
                },
                'invoice': {
                    'number':       invoice['invoice_no']   or '',
                    'date':         invoice['invoice_date'] or '',
                    'service_type': service_type,
                    'inv_title':    inv_title,
                },
                # ↓ ဒီနေရာမှာ ထည့်ရမယ်
                'payment': {
                    'bank_name':   invoice['mother_bank_name']   or '',
                    'beneficiary': invoice['mother_beneficiary'] or '',
                    'account_no':  invoice['mother_account_no']  or '',
                    'kpay_no':     invoice['mother_kpay_no']     or '',
                },
                'items': [],
                'totals': {
                    'subtotal':        invoice['subtotal']    or 0,
                    'tax':             invoice['tax']         or 0,
                    'advance':         invoice['advance']     or 0,
                    'grand_total':     grand_total,
                    'amount_in_words': amount_words           # BUG 3 FIX
                }
            }

            for item in items:
                invoice_data['items'].append({
                    'description': item['description'] or '',
                    'qty':         item['qty']         or 0,
                    'unit_price':  item['unit_price']  or 0,
                    'amount':      item['amount']      or 0
                })

            return invoice_data

        except Exception as e:
            print(f"Error getting invoice data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def edit_selected_invoice(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.edit_invoice_at_row(current_row)
        else:
            QMessageBox.information(self, "Info", "Please select an invoice to edit")
    
    def edit_invoice_at_row(self, row):
        inv_id_item = self.table.item(row, 0)
        if not inv_id_item:
            return
        
        try:
            invoice_id = int(inv_id_item.text())
            
            from .invoice import InvoiceDialog
            dialog = InvoiceDialog(self, invoice_id=invoice_id, mode='edit')
            result = dialog.exec()
            
            if result == QDialog.Accepted:
                self.load_invoices()
                QMessageBox.information(self, "✅ Success", "Invoice updated successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit invoice: {str(e)}")
    
    def delete_selected_invoice(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.delete_invoice_at_row(current_row)
        else:
            QMessageBox.information(self, "Info", "Please select an invoice to delete")
    
    def delete_invoice_at_row(self, row):
        if row < 0 or row >= self.table.rowCount():
            return
        
        inv_no_item = self.table.item(row, 1)
        inv_id_item = self.table.item(row, 0)
        
        if not inv_no_item or not inv_id_item:
            QMessageBox.warning(self, "Error", "Invalid invoice data!")
            return
        
        invoice_no = inv_no_item.text()
        invoice_id = int(inv_id_item.text())
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete invoice {invoice_no}?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = get_db()
                conn.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
                conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
                conn.commit()
                conn.close()
                
                self.table.removeRow(row)
                QMessageBox.information(self, "✅ Success", f"Invoice {invoice_no} deleted successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")
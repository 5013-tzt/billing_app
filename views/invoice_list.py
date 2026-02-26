import sqlite3
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QAbstractItemView,
    QLineEdit, QWidget, QFileDialog, QStyle
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from database import get_db


def _icon(widget, sp):
    """QStyle.StandardPixmap ကနေ icon ယူမယ် — font/emoji dependency မရှိ"""
    return widget.style().standardIcon(sp)


class InvoiceListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Invoice List")
        self.resize(1400, 700)
        self.setMinimumSize(1200, 600)

        from .styles import STYLESHEET
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        lbl = QLabel("Search:")
        lbl.setStyleSheet("font-weight: bold;")
        search_layout.addWidget(lbl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by invoice no, company, service type, or title..."
        )
        self.search_input.setMinimumWidth(350)
        self.search_input.textChanged.connect(self.filter_invoices)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        # SP_BrowserReload — Windows/Mac/Linux အားလုံးပါ
        self.refresh_btn = QPushButton(" Refresh")
        self.refresh_btn.setIcon(_icon(self, QStyle.SP_BrowserReload))
        self.refresh_btn.setIconSize(QSize(16, 16))
        self.refresh_btn.setFixedWidth(110)
        self.refresh_btn.setFixedHeight(35)
        self.refresh_btn.clicked.connect(self.load_invoices)
        search_layout.addWidget(self.refresh_btn)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Invoice No", "Date", "Company",
            "Service Type", "Title", "Amount", "Status", "Actions"
        ])

        hdr = self.table.horizontalHeader()
        for col in [0, 1, 2, 4, 5, 6, 7, 8]:
            hdr.setSectionResizeMode(col, QHeaderView.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 95)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 155)
        self.table.setColumnWidth(6, 130)
        self.table.setColumnWidth(7, 85)
        self.table.setColumnWidth(8, 148)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setDefaultSectionSize(38)
        layout.addWidget(self.table)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # SP_DialogSaveButton — floppy/save icon, cross-platform
        self.save_pdf_btn = QPushButton(" Save as PDF")
        self.save_pdf_btn.setIcon(_icon(self, QStyle.SP_DialogSaveButton))
        self.save_pdf_btn.setIconSize(QSize(18, 18))
        self.save_pdf_btn.setFixedHeight(40)
        self.save_pdf_btn.setFixedWidth(155)
        self.save_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981; color: white;
                font-weight: bold; border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.save_pdf_btn.clicked.connect(self.save_invoice_as_pdf)
        btn_layout.addWidget(self.save_pdf_btn)

        # SP_FileDialogDetailedView — edit/detail icon, cross-platform
        self.edit_btn = QPushButton(" Edit")
        self.edit_btn.setIcon(_icon(self, QStyle.SP_FileDialogDetailedView))
        self.edit_btn.setIconSize(QSize(18, 18))
        self.edit_btn.setFixedHeight(40)
        self.edit_btn.setFixedWidth(110)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b; color: white;
                font-weight: bold; border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #d97706; }
        """)
        self.edit_btn.clicked.connect(self.edit_selected_invoice)
        btn_layout.addWidget(self.edit_btn)

        # SP_TrashIcon — trash icon (Windows 10+ native, fallback on older)
        self.delete_btn = QPushButton(" Delete")
        self.delete_btn.setIcon(_icon(self, QStyle.SP_DialogCloseButton))
        self.delete_btn.setIconSize(QSize(18, 18))
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setFixedWidth(110)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444; color: white;
                font-weight: bold; border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #dc2626; }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_invoice)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedHeight(40)
        self.close_btn.setFixedWidth(100)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)
        self.load_invoices()

    def load_invoices(self):
        try:
            self.table.setRowCount(0)
            conn = get_db()
            rows = conn.execute("""
                SELECT i.id, i.invoice_no, i.invoice_date, i.company_name,
                       i.service_type, i.inv_title, i.grand_total, i.status
                FROM invoices i ORDER BY i.id DESC
            """).fetchall()
            for row in rows:
                self.add_invoice_row(row)
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load invoices:\n{str(e)}")

    def add_invoice_row(self, row_data):
        rp = self.table.rowCount()
        self.table.insertRow(rp)

        id_item = QTableWidgetItem(str(row_data[0]))
        id_item.setData(Qt.UserRole, row_data[0])
        self.table.setItem(rp, 0, id_item)

        no_item = QTableWidgetItem(row_data[1] or "")
        no_item.setData(Qt.UserRole, row_data[1])
        self.table.setItem(rp, 1, no_item)

        for col, val in enumerate([row_data[2], row_data[3],
                                    row_data[4] or "N/A", row_data[5] or ""], 2):
            self.table.setItem(rp, col, QTableWidgetItem(val or ""))

        amount = float(row_data[6]) if row_data[6] else 0
        amt = QTableWidgetItem(f"{amount:,.0f} MMK")
        amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amt.setData(Qt.UserRole, amount)
        self.table.setItem(rp, 6, amt)

        status = row_data[7] or "Pending"
        st = QTableWidgetItem(status)
        if status.lower() == "paid":
            st.setForeground(QColor(22, 163, 74))
            st.setBackground(QColor(220, 252, 231))
        elif status.lower() == "pending":
            st.setForeground(QColor(217, 119, 6))
            st.setBackground(QColor(254, 243, 199))
        else:
            st.setForeground(QColor(37, 99, 235))
            st.setBackground(QColor(219, 234, 254))
        self.table.setItem(rp, 7, st)

        # Action buttons — QStyle icons (OS native, font-independent)
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(3, 3, 3, 3)
        hl.setSpacing(3)

        BTN = QSize(40, 30)
        ICO = QSize(15, 15)

        b_pdf = QPushButton()
        b_pdf.setIcon(_icon(self, QStyle.SP_DialogSaveButton))
        b_pdf.setIconSize(ICO)
        b_pdf.setFixedSize(BTN)
        b_pdf.setToolTip("Save as PDF")
        b_pdf.setStyleSheet(
            "QPushButton{background:#10b981;border:none;border-radius:4px;}"
            "QPushButton:hover{background:#059669;}"
        )
        b_pdf.clicked.connect(lambda _, r=rp: self.save_invoice_pdf_at_row(r))
        hl.addWidget(b_pdf)

        b_edit = QPushButton()
        b_edit.setIcon(_icon(self, QStyle.SP_FileDialogDetailedView))
        b_edit.setIconSize(ICO)
        b_edit.setFixedSize(BTN)
        b_edit.setToolTip("Edit Invoice")
        b_edit.setStyleSheet(
            "QPushButton{background:#f59e0b;border:none;border-radius:4px;}"
            "QPushButton:hover{background:#d97706;}"
        )
        b_edit.clicked.connect(lambda _, r=rp: self.edit_invoice_at_row(r))
        hl.addWidget(b_edit)

        b_del = QPushButton()
        b_del.setIcon(_icon(self, QStyle.SP_DialogCloseButton))
        b_del.setIconSize(ICO)
        b_del.setFixedSize(BTN)
        b_del.setToolTip("Delete Invoice")
        b_del.setStyleSheet(
            "QPushButton{background:#ef4444;border:none;border-radius:4px;}"
            "QPushButton:hover{background:#dc2626;}"
        )
        b_del.clicked.connect(lambda _, r=rp: self.delete_invoice_at_row(r))
        hl.addWidget(b_del)

        self.table.setCellWidget(rp, 8, w)

    def filter_invoices(self):
        txt = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            show = any(
                self.table.item(row, c) and txt in self.table.item(row, c).text().lower()
                for c in [1, 2, 3, 4, 5]
            )
            self.table.setRowHidden(row, not show)

    def save_invoice_as_pdf(self):
        row = self.table.currentRow()
        if row >= 0:
            self.save_invoice_pdf_at_row(row)
        else:
            QMessageBox.information(self, "Info", "Please select an invoice first.")

    def save_invoice_pdf_at_row(self, row):
        try:
            id_i = self.table.item(row, 0)
            no_i = self.table.item(row, 1)
            if not id_i or not no_i:
                return
            data = self.get_invoice_data_for_pdf(int(id_i.text()))
            if not data:
                QMessageBox.warning(self, "Error", "Could not load invoice data.")
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Invoice PDF",
                f"invoice_{no_i.text()}.pdf", "PDF Files (*.pdf)"
            )
            if path:
                if not path.lower().endswith(".pdf"):
                    path += ".pdf"
                from .pdf_generator import InvoicePDFGenerator
                InvoicePDFGenerator(path).create_invoice(data)
                QMessageBox.information(self, "Success", f"PDF saved!\n\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{str(e)}")
            import traceback; traceback.print_exc()

    def get_invoice_data_for_pdf(self, invoice_id):
        try:
            conn = get_db()
            inv = conn.execute('''
                SELECT i.*,
                    c.c1_name, c.c1_pos, c.c1_ph, c.c1_em,
                    m.name AS mother_name, m.phone AS mother_phone,
                    m.email AS mother_email, m.address AS mother_address,
                    m.logo AS mother_logo, m.bank_name AS mother_bank_name,
                    m.beneficiary AS mother_beneficiary,
                    m.account_no AS mother_account_no,
                    m.kpay_no AS mother_kpay_no
                FROM invoices i
                LEFT JOIN clients   c ON i.client_id         = c.id
                LEFT JOIN companies m ON i.mother_company_id = m.id
                WHERE i.id = ?
            ''', (invoice_id,)).fetchone()

            if not inv:
                conn.close()
                return None

            items = conn.execute(
                "SELECT * FROM invoice_items WHERE invoice_id=? ORDER BY id",
                (invoice_id,)
            ).fetchall()
            conn.close()

            from .pdf_generator import number_to_words_mm
            grand_total = inv['grand_total'] or 0

            return {
                'mother_company': {
                    'name': inv['mother_name'] or '',
                    'phone': inv['mother_phone'] or '',
                    'email': inv['mother_email'] or '',
                    'address': inv['mother_address'] or '',
                    'logo': inv['mother_logo'] or '',
                    'bank_name': inv['mother_bank_name'] or '',
                    'beneficiary': inv['mother_beneficiary'] or '',
                    'account_no': inv['mother_account_no'] or '',
                    'kpay_no': inv['mother_kpay_no'] or '',
                },
                'client': {
                    'company_name': inv['company_name'] or '',
                    'address': inv['address'] or '',
                    'contact_name': inv['contact_name'] or inv['c1_name'] or '',
                    'contact_pos': inv['contact_pos'] or inv['c1_pos'] or '',
                    'contact_ph': inv['contact_ph'] or inv['c1_ph'] or '',
                    'contact_email': inv['contact_email'] or inv['c1_em'] or '',
                    'show_position': bool(inv['contact_pos']),
                    'show_phone': bool(inv['contact_ph']),
                    'show_email': bool(inv['contact_email']),
                },
                'invoice': {
                    'number': inv['invoice_no'] or '',
                    'date': inv['invoice_date'] or '',
                    'service_type': inv['service_type'] or '',
                    'inv_title': inv['inv_title'] or '',
                },
                'payment': {
                    'bank_name': inv['mother_bank_name'] or '',
                    'beneficiary': inv['mother_beneficiary'] or '',
                    'account_no': inv['mother_account_no'] or '',
                    'kpay_no': inv['mother_kpay_no'] or '',
                },
                'items': [
                    {
                        'description': it['description'] or '',
                        'qty': it['qty'] or 0,
                        'unit_price': it['unit_price'] or 0,
                        'amount': it['amount'] or 0,
                    }
                    for it in items
                ],
                'totals': {
                    'subtotal': inv['subtotal'] or 0,
                    'tax': inv['tax'] or 0,
                    'advance': inv['advance'] or 0,
                    'grand_total': grand_total,
                    'amount_in_words': number_to_words_mm(int(grand_total)),
                },
            }
        except Exception as e:
            print(f"Error: {e}")
            import traceback; traceback.print_exc()
            return None

    def edit_selected_invoice(self):
        row = self.table.currentRow()
        if row >= 0:
            self.edit_invoice_at_row(row)
        else:
            QMessageBox.information(self, "Info", "Please select an invoice first.")

    def edit_invoice_at_row(self, row):
        id_i = self.table.item(row, 0)
        if not id_i:
            return
        try:
            from .invoice import InvoiceDialog
            dlg = InvoiceDialog(self, invoice_id=int(id_i.text()), mode='edit')
            if dlg.exec() == QDialog.Accepted:
                self.load_invoices()
                QMessageBox.information(self, "Success", "Invoice updated!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit:\n{str(e)}")

    def delete_selected_invoice(self):
        row = self.table.currentRow()
        if row >= 0:
            self.delete_invoice_at_row(row)
        else:
            QMessageBox.information(self, "Info", "Please select an invoice first.")

    def delete_invoice_at_row(self, row):
        if not (0 <= row < self.table.rowCount()):
            return
        id_i = self.table.item(row, 0)
        no_i = self.table.item(row, 1)
        if not id_i or not no_i:
            return
        invoice_no = no_i.text()
        invoice_id = int(id_i.text())

        if QMessageBox.question(
            self, "Confirm Delete",
            f"Delete invoice {invoice_no}?\n\nThis cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                conn = get_db()
                conn.execute("DELETE FROM invoice_items WHERE invoice_id=?", (invoice_id,))
                conn.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
                conn.commit()
                conn.close()
                self.table.removeRow(row)
                QMessageBox.information(self, "Success",
                                        f"Invoice {invoice_no} deleted!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete:\n{str(e)}")
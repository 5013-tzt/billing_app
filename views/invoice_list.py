import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QAbstractItemView,
    QLineEdit, QWidget, QFileDialog, QStyle, QInputDialog,
    QComboBox, QTextEdit, QDateEdit, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QColor, QFont
from database import get_db


def _icon(widget, sp):
    return widget.style().standardIcon(sp)


class InvoiceListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Invoice List")
        self.resize(1450, 700)
        self.setMinimumSize(1250, 600)

        from .styles import STYLESHEET
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # ── Search bar ────────────────────────────────────────────────
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

        self.refresh_btn = QPushButton(" Refresh")
        self.refresh_btn.setIcon(_icon(self, QStyle.SP_BrowserReload))
        self.refresh_btn.setIconSize(QSize(16, 16))
        self.refresh_btn.setFixedWidth(110)
        self.refresh_btn.setFixedHeight(35)
        self.refresh_btn.clicked.connect(self.load_invoices)
        search_layout.addWidget(self.refresh_btn)
        layout.addLayout(search_layout)

        # ── Table (10 columns — added Receipt col) ────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Invoice No", "Date", "Company",
            "Service Type", "Title", "Amount", "Status", "Paid Date", "Actions"
        ])

        hdr = self.table.horizontalHeader()
        for col in [0, 1, 2, 4, 5, 6, 7, 8, 9]:
            hdr.setSectionResizeMode(col, QHeaderView.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 125)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 145)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 90)   # Paid Date
        self.table.setColumnWidth(9, 185)  # Actions (4 buttons)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setDefaultSectionSize(38)
        layout.addWidget(self.table)

        # ── Bottom buttons ────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        BTN_H = 40

        # Invoice PDF
        self.save_pdf_btn = QPushButton(" Invoice PDF")
        self.save_pdf_btn.setIcon(_icon(self, QStyle.SP_DialogSaveButton))
        self.save_pdf_btn.setIconSize(QSize(18, 18))
        self.save_pdf_btn.setFixedHeight(BTN_H)
        self.save_pdf_btn.setFixedWidth(145)
        self.save_pdf_btn.setStyleSheet("""
            QPushButton { background:#10b981; color:white; font-weight:bold;
                          border:none; border-radius:4px; }
            QPushButton:hover { background:#059669; }
        """)
        self.save_pdf_btn.clicked.connect(self.save_invoice_as_pdf)
        btn_layout.addWidget(self.save_pdf_btn)

        # Mark as Paid
        self.mark_paid_btn = QPushButton(" Mark as Paid")
        self.mark_paid_btn.setIcon(_icon(self, QStyle.SP_DialogApplyButton))
        self.mark_paid_btn.setIconSize(QSize(18, 18))
        self.mark_paid_btn.setFixedHeight(BTN_H)
        self.mark_paid_btn.setFixedWidth(150)
        self.mark_paid_btn.setStyleSheet("""
            QPushButton { background:#2563eb; color:white; font-weight:bold;
                          border:none; border-radius:4px; }
            QPushButton:hover { background:#1d4ed8; }
        """)
        self.mark_paid_btn.clicked.connect(self.mark_selected_as_paid)
        btn_layout.addWidget(self.mark_paid_btn)

        # Receipt PDF
        self.receipt_btn = QPushButton(" Receipt")
        self.receipt_btn.setIcon(_icon(self, QStyle.SP_FileDialogContentsView))
        self.receipt_btn.setIconSize(QSize(18, 18))
        self.receipt_btn.setFixedHeight(BTN_H)
        self.receipt_btn.setFixedWidth(120)
        self.receipt_btn.setStyleSheet("""
            QPushButton { background:#7c3aed; color:white; font-weight:bold;
                          border:none; border-radius:4px; }
            QPushButton:hover { background:#6d28d9; }
        """)
        self.receipt_btn.clicked.connect(self.save_receipt_pdf)
        btn_layout.addWidget(self.receipt_btn)

        # Edit
        self.edit_btn = QPushButton(" Edit")
        self.edit_btn.setIcon(_icon(self, QStyle.SP_FileDialogDetailedView))
        self.edit_btn.setIconSize(QSize(18, 18))
        self.edit_btn.setFixedHeight(BTN_H)
        self.edit_btn.setFixedWidth(100)
        self.edit_btn.setStyleSheet("""
            QPushButton { background:#f59e0b; color:white; font-weight:bold;
                          border:none; border-radius:4px; }
            QPushButton:hover { background:#d97706; }
        """)
        self.edit_btn.clicked.connect(self.edit_selected_invoice)
        btn_layout.addWidget(self.edit_btn)

        # Delete
        self.delete_btn = QPushButton(" Delete")
        self.delete_btn.setIcon(_icon(self, QStyle.SP_DialogCloseButton))
        self.delete_btn.setIconSize(QSize(18, 18))
        self.delete_btn.setFixedHeight(BTN_H)
        self.delete_btn.setFixedWidth(100)
        self.delete_btn.setStyleSheet("""
            QPushButton { background:#ef4444; color:white; font-weight:bold;
                          border:none; border-radius:4px; }
            QPushButton:hover { background:#dc2626; }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_invoice)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedHeight(BTN_H)
        self.close_btn.setFixedWidth(90)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)
        self.load_invoices()

    # ── Data ──────────────────────────────────────────────────────────

    def load_invoices(self):
        try:
            self.table.setRowCount(0)
            conn = get_db()
            rows = conn.execute("""
                SELECT i.id, i.invoice_no, i.invoice_date, i.company_name,
                       i.service_type, i.inv_title, i.grand_total, i.status,
                       i.paid_date
                FROM invoices i ORDER BY i.id DESC
            """).fetchall()
            for row in rows:
                self.add_invoice_row(row)
            conn.close()
        except Exception as e:
            # paid_date column မရှိသေးရင် fallback
            try:
                conn = get_db()
                rows = conn.execute("""
                    SELECT i.id, i.invoice_no, i.invoice_date, i.company_name,
                           i.service_type, i.inv_title, i.grand_total, i.status,
                           NULL as paid_date
                    FROM invoices i ORDER BY i.id DESC
                """).fetchall()
                for row in rows:
                    self.add_invoice_row(row)
                conn.close()
            except Exception as e2:
                QMessageBox.warning(self, "Error", f"Failed to load:\n{str(e2)}")

    def add_invoice_row(self, row_data):
        rp = self.table.rowCount()
        self.table.insertRow(rp)

        # ID
        id_item = QTableWidgetItem(str(row_data[0]))
        id_item.setData(Qt.UserRole, row_data[0])
        self.table.setItem(rp, 0, id_item)

        # Invoice No
        no_item = QTableWidgetItem(row_data[1] or "")
        no_item.setData(Qt.UserRole, row_data[1])
        self.table.setItem(rp, 1, no_item)

        # Date / Company / Service / Title
        for col, val in enumerate([row_data[2], row_data[3],
                                    row_data[4] or "N/A", row_data[5] or ""], 2):
            self.table.setItem(rp, col, QTableWidgetItem(val or ""))

        # Amount
        amount = float(row_data[6]) if row_data[6] else 0
        amt = QTableWidgetItem(f"{amount:,.0f} MMK")
        amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amt.setData(Qt.UserRole, amount)
        self.table.setItem(rp, 6, amt)

        # Status
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

        # Paid Date (col 8)
        paid_date = row_data[8] if len(row_data) > 8 else None
        pd_item = QTableWidgetItem(paid_date or "")
        if paid_date:
            pd_item.setForeground(QColor(22, 163, 74))
        self.table.setItem(rp, 8, pd_item)

        # ── Action buttons (col 9) ────────────────────────────────────
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(2, 2, 2, 2)
        hl.setSpacing(2)

        ICO = QSize(14, 14)

        # Invoice PDF — green
        b_pdf = QPushButton()
        b_pdf.setIcon(_icon(self, QStyle.SP_DialogSaveButton))
        b_pdf.setIconSize(ICO)
        b_pdf.setFixedSize(40, 30)
        b_pdf.setToolTip("Save Invoice as PDF")
        b_pdf.setStyleSheet("QPushButton{background:#10b981;border:none;border-radius:4px;}"
                            "QPushButton:hover{background:#059669;}")
        b_pdf.clicked.connect(lambda _, r=rp: self.save_invoice_pdf_at_row(r))
        hl.addWidget(b_pdf)

        # Mark as Paid — blue (Pending ဆိုရင်သာ active)
        b_paid = QPushButton()
        b_paid.setIcon(_icon(self, QStyle.SP_DialogApplyButton))
        b_paid.setIconSize(ICO)
        b_paid.setFixedSize(40, 30)
        b_paid.setToolTip("Mark as Paid")
        if status.lower() == "paid":
            b_paid.setStyleSheet("QPushButton{background:#94a3b8;border:none;border-radius:4px;}")
            b_paid.setEnabled(False)
        else:
            b_paid.setStyleSheet("QPushButton{background:#2563eb;border:none;border-radius:4px;}"
                                 "QPushButton:hover{background:#1d4ed8;}")
        b_paid.clicked.connect(lambda _, r=rp: self.mark_paid_at_row(r))
        hl.addWidget(b_paid)

        # Receipt PDF — purple (Paid ဆိုရင်သာ active)
        b_rcpt = QPushButton()
        b_rcpt.setIcon(_icon(self, QStyle.SP_FileDialogContentsView))
        b_rcpt.setIconSize(ICO)
        b_rcpt.setFixedSize(40, 30)
        b_rcpt.setToolTip("Save Receipt PDF")
        if status.lower() == "paid":
            b_rcpt.setStyleSheet("QPushButton{background:#7c3aed;border:none;border-radius:4px;}"
                                 "QPushButton:hover{background:#6d28d9;}")
        else:
            b_rcpt.setStyleSheet("QPushButton{background:#94a3b8;border:none;border-radius:4px;}")
            b_rcpt.setEnabled(False)
        b_rcpt.clicked.connect(lambda _, r=rp: self.save_receipt_pdf_at_row(r))
        hl.addWidget(b_rcpt)

        # Edit — amber
        b_edit = QPushButton()
        b_edit.setIcon(_icon(self, QStyle.SP_FileDialogDetailedView))
        b_edit.setIconSize(ICO)
        b_edit.setFixedSize(36, 30)
        b_edit.setToolTip("Edit Invoice")
        b_edit.setStyleSheet("QPushButton{background:#f59e0b;border:none;border-radius:4px;}"
                             "QPushButton:hover{background:#d97706;}")
        b_edit.clicked.connect(lambda _, r=rp: self.edit_invoice_at_row(r))
        hl.addWidget(b_edit)

        # Delete — red
        b_del = QPushButton()
        b_del.setIcon(_icon(self, QStyle.SP_DialogCloseButton))
        b_del.setIconSize(ICO)
        b_del.setFixedSize(36, 30)
        b_del.setToolTip("Delete Invoice")
        b_del.setStyleSheet("QPushButton{background:#ef4444;border:none;border-radius:4px;}"
                            "QPushButton:hover{background:#dc2626;}")
        b_del.clicked.connect(lambda _, r=rp: self.delete_invoice_at_row(r))
        hl.addWidget(b_del)

        self.table.setCellWidget(rp, 9, w)

    # ── Filter ────────────────────────────────────────────────────────

    def filter_invoices(self):
        txt = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            show = any(
                self.table.item(row, c) and txt in self.table.item(row, c).text().lower()
                for c in [1, 2, 3, 4, 5]
            )
            self.table.setRowHidden(row, not show)

    # ── Mark as Paid ──────────────────────────────────────────────────

    def mark_selected_as_paid(self):
        row = self.table.currentRow()
        if row >= 0:
            self.mark_paid_at_row(row)
        else:
            QMessageBox.information(self, "Info", "Please select a Pending invoice first.")

    def mark_paid_at_row(self, row):
        id_i = self.table.item(row, 0)
        no_i = self.table.item(row, 1)
        co_i = self.table.item(row, 3)
        am_i = self.table.item(row, 6)
        st_i = self.table.item(row, 7)
        if not id_i:
            return

        invoice_id     = int(id_i.text())
        invoice_no     = no_i.text() if no_i else ""
        client_name    = co_i.text() if co_i else ""
        amount_text    = am_i.text() if am_i else "0"
        current_status = st_i.text() if st_i else ""

        if current_status.lower() == "paid":
            QMessageBox.information(self, "Info",
                                    f"Invoice {invoice_no} is already Paid.")
            return

        dlg = MarkAsPaidDialog(self, invoice_no, client_name, amount_text)
        if dlg.exec() != QDialog.Accepted:
            return

        paid_date      = dlg.get_paid_date()
        payment_method = dlg.get_payment_method()
        payment_note   = dlg.get_payment_note()

        try:
            conn = get_db()

            # ── Receipt No auto-generate: RE-YY#### ──────────────────
            year_suffix = datetime.now().strftime('%y')   # e.g. "26"
            last = conn.execute(
                "SELECT receipt_no FROM invoices WHERE receipt_no LIKE ? ORDER BY receipt_no DESC LIMIT 1",
                (f"RE-{year_suffix}%",)
            ).fetchone()
            if last and last[0]:
                try:
                    seq = int(last[0][len(f"RE-{year_suffix}"):]) + 1
                except ValueError:
                    seq = 1
            else:
                seq = 1
            receipt_no = f"RE-{year_suffix}{seq:04d}"

            conn.execute(
                "UPDATE invoices SET status=?, paid_date=?, payment_method=?, payment_note=?, receipt_no=? WHERE id=?",
                ("Paid", paid_date, payment_method, payment_note, receipt_no, invoice_id)
            )
            conn.commit()
            conn.close()
            self.load_invoices()
            QMessageBox.information(
                self, "✅ Success",
                f"Invoice {invoice_no} marked as Paid!\nReceipt No: {receipt_no}\nPayment date: {paid_date}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update status:\n{str(e)}")

    # ── Invoice PDF ───────────────────────────────────────────────────

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
                QMessageBox.information(self, "Success", f"Invoice PDF saved!\n\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed:\n{str(e)}")
            import traceback; traceback.print_exc()

    # ── Receipt PDF ───────────────────────────────────────────────────

    def save_receipt_pdf(self):
        row = self.table.currentRow()
        if row >= 0:
            st_i = self.table.item(row, 7)
            if st_i and st_i.text().lower() == "paid":
                self.save_receipt_pdf_at_row(row)
            else:
                QMessageBox.information(
                    self, "Info",
                    "Please select a Paid invoice to generate receipt.\n"
                    "Mark the invoice as Paid first."
                )
        else:
            QMessageBox.information(self, "Info", "Please select an invoice first.")

    def save_receipt_pdf_at_row(self, row):
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
                self, "Save Receipt PDF",
                f"receipt_{no_i.text()}.pdf", "PDF Files (*.pdf)"
            )
            if path:
                if not path.lower().endswith(".pdf"):
                    path += ".pdf"
                from .pdf_generator import InvoicePDFGenerator
                InvoicePDFGenerator(path).create_receipt(data)
                QMessageBox.information(self, "Success", f"Receipt PDF saved!\n\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed:\n{str(e)}")
            import traceback; traceback.print_exc()

    # ── Get invoice data ──────────────────────────────────────────────

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

            # paid_date — column မရှိသေးရင် safe ယူမယ်
            try:
                paid_date = inv['paid_date'] or ""
            except Exception:
                paid_date = ""

            try:
                payment_method = inv['payment_method'] or ""
            except Exception:
                payment_method = ""

            try:
                receipt_no = inv['receipt_no'] or ""
            except Exception:
                receipt_no = ""

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
                    # toggle မနှိပ်ဘဲ save = NULL → "Valued Client"
                    'contact_name':  inv['contact_name'] or None,
                    'contact_pos':   inv['contact_pos']  or None,
                    'contact_ph':    inv['contact_ph']   or None,
                    'contact_email': inv['contact_email'] or None,
                    'show_position': bool(inv['contact_pos']),
                    'show_phone':    bool(inv['contact_ph']),
                    'show_email':    bool(inv['contact_email']),
                    'show_name':     bool(inv['contact_name']),
                },
                'invoice': {
                    'number': inv['invoice_no'] or '',
                    'date': inv['invoice_date'] or '',
                    'service_type': inv['service_type'] or '',
                    'inv_title': inv['inv_title'] or '',
                    'status': inv['status'] or 'Pending',
                    'paid_date': paid_date,
                    'payment_method': payment_method or 'Bank Transfer',
                    'receipt_no': receipt_no,
                },
                'payment': {
                    'bank_name': inv['mother_bank_name'] or '',
                    'beneficiary': inv['mother_beneficiary'] or '',
                    'account_no': inv['mother_account_no'] or '',
                    'kpay_no': inv['mother_kpay_no'] or '',
                },
                'items': [
                    {
                        'description':   it['description'] or '',
                        'qty':           it['qty'] or 0,
                        'unit_price':    it['unit_price'] or 0,
                        'amount':        it['amount'] or 0,
                        'days':          it['days'] if it['days'] else None,
                        'start_date':    it['start_date'] or '',
                        'end_date':      it['end_date'] or '',
                        'is_daily':      (inv['inv_type'] or '') == '📊 Daily',
                        'use_work_days': bool(inv['use_work_days']) and (inv['inv_type'] or '') != '📊 Daily',
                        'days_in_month': None,
                    }
                    for it in items
                ],
                'totals': {
                    'subtotal': inv['subtotal'] or 0,
                    'tax': inv['tax'] or 0,
                    'advance': inv['advance'] or 0,
                    'advance_text': inv['advance_text'] or 'ADVANCE',
                    'grand_total': grand_total,
                    'amount_in_words': number_to_words_mm(int(grand_total)),
                },
            }
        except Exception as e:
            print(f"Error: {e}")
            import traceback; traceback.print_exc()
            return None

    # ── Edit ──────────────────────────────────────────────────────────

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
            QMessageBox.critical(self, "Error", f"Failed:\n{str(e)}")

    # ── Delete ────────────────────────────────────────────────────────

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
                QMessageBox.information(self, "Success", f"Invoice {invoice_no} deleted!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed:\n{str(e)}")

# ══════════════════════════════════════════════════════════════════════
# Mark as Paid — Professional Payment Dialog
# ══════════════════════════════════════════════════════════════════════

class MarkAsPaidDialog(QDialog):
    """Invoice ငွေရရှိမှုမှတ်တမ်း dialog — ပုံပြထားတဲ့ design အတိုင်း"""

    PAYMENT_METHODS = [
        "Bank Transfer (KBZ/CB/AYA)",
        "Bank Transfer (KBZ)",
        "Bank Transfer (CB Bank)",
        "Bank Transfer (AYA Bank)",
        "Bank Transfer (MAB)",
        "KPay",
        "Wave Pay",
        "Cash",
        "Cheque",
        "Other",
    ]

    def __init__(self, parent=None, invoice_no="", client_name="", amount_text="0"):
        super().__init__(parent)
        self.setWindowTitle("Mark as Paid")
        self.setFixedWidth(520)
        self.setModal(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

        # ── Overall layout ────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Green header bar ──────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background-color: #16a34a; border-radius: 0px;")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 0, 20, 0)

        emoji = QLabel("💰")
        emoji.setStyleSheet("background: transparent; font-size: 20px;")
        h_lay.addWidget(emoji)

        title_lbl = QLabel(f"Payment for {invoice_no}")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet("color: white; background: transparent;")
        h_lay.addWidget(title_lbl, 1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                color: white; background: transparent;
                border: none; font-size: 16px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 4px; }
        """)
        close_btn.clicked.connect(self.reject)
        h_lay.addWidget(close_btn)

        root.addWidget(header)

        # ── Body ──────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: #ffffff;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 20, 24, 8)
        body_lay.setSpacing(14)

        lbl_font = QFont()
        lbl_font.setPointSize(10)
        lbl_font.setBold(True)

        field_font = QFont()
        field_font.setPointSize(10)

        field_style = """
            QLineEdit, QDateEdit, QComboBox, QTextEdit {
                border: 1.5px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 10pt;
                background: #f9fafb;
                color: #111827;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1.5px solid #16a34a;
                background: #ffffff;
            }
            QLineEdit[readOnly="true"] {
                background: #f3f4f6;
                color: #6b7280;
            }
        """

        # Client Name (read-only)
        body_lay.addWidget(self._label("Client Name", lbl_font))
        self.client_field = QLineEdit(client_name)
        self.client_field.setReadOnly(True)
        self.client_field.setMinimumHeight(40)
        self.client_field.setFont(field_font)
        self.client_field.setStyleSheet(field_style)
        body_lay.addWidget(self.client_field)

        # Received Date + Amount row
        row1 = QHBoxLayout()
        row1.setSpacing(14)

        date_col = QVBoxLayout()
        date_col.setSpacing(6)
        date_col.addWidget(self._label("Received Date", lbl_font))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        self.date_edit.setMinimumHeight(40)
        self.date_edit.setFont(field_font)
        self.date_edit.setStyleSheet(field_style)
        date_col.addWidget(self.date_edit)
        row1.addLayout(date_col, 1)

        amt_col = QVBoxLayout()
        amt_col.setSpacing(6)
        amt_col.addWidget(self._label("Amount (MMK)", lbl_font))
        self.amount_field = QLineEdit(amount_text)
        self.amount_field.setReadOnly(True)
        self.amount_field.setMinimumHeight(40)
        self.amount_field.setFont(field_font)
        self.amount_field.setStyleSheet(field_style)
        amt_col.addWidget(self.amount_field)
        row1.addLayout(amt_col, 1)

        body_lay.addLayout(row1)

        # Payment Method
        body_lay.addWidget(self._label("Payment Method", lbl_font))
        self.method_cb = QComboBox()
        self.method_cb.addItems(self.PAYMENT_METHODS)
        self.method_cb.setMinimumHeight(40)
        self.method_cb.setFont(field_font)
        self.method_cb.setStyleSheet(field_style + """
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow { width: 12px; height: 12px; }
        """)
        body_lay.addWidget(self.method_cb)

        # Note / Remarks
        body_lay.addWidget(self._label("Note / Remarks", lbl_font))
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Enter reference (e.g. Transaction ID)")
        self.note_edit.setFixedHeight(80)
        self.note_edit.setFont(field_font)
        self.note_edit.setStyleSheet(field_style)
        body_lay.addWidget(self.note_edit)

        root.addWidget(body)

        # ── Divider ───────────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: #e5e7eb;")
        root.addWidget(div)

        # ── Footer buttons ────────────────────────────────────────────
        footer = QWidget()
        footer.setStyleSheet("background: #ffffff;")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(24, 12, 24, 16)
        f_lay.setSpacing(12)
        f_lay.addStretch()

        btn_font = QFont()
        btn_font.setPointSize(10)
        btn_font.setBold(True)

        close_action = QPushButton("Close")
        close_action.setFixedHeight(42)
        close_action.setMinimumWidth(100)
        close_action.setFont(btn_font)
        close_action.setStyleSheet("""
            QPushButton {
                background: #4b5563; color: white;
                border: none; border-radius: 6px;
            }
            QPushButton:hover { background: #374151; }
        """)
        close_action.clicked.connect(self.reject)
        f_lay.addWidget(close_action)

        confirm_btn = QPushButton("Confirm Payment")
        confirm_btn.setFixedHeight(42)
        confirm_btn.setMinimumWidth(150)
        confirm_btn.setFont(btn_font)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: #16a34a; color: white;
                border: none; border-radius: 6px;
            }
            QPushButton:hover { background: #15803d; }
        """)
        confirm_btn.clicked.connect(self.accept)
        f_lay.addWidget(confirm_btn)

        root.addWidget(footer)

    def _label(self, text, font):
        lbl = QLabel(text)
        lbl.setFont(font)
        lbl.setStyleSheet("color: #111827;")
        return lbl

    def get_paid_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")

    def get_payment_method(self):
        return self.method_cb.currentText()

    def get_payment_note(self):
        return self.note_edit.toPlainText().strip()
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QPushButton, QLineEdit,
    QTextEdit, QMessageBox, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout,
    QLabel, QScrollArea, QFileDialog, QFrame
)
from PySide6.QtCore import Qt
import pandas as pd
from database import get_db
from .styles import STYLESHEET


class ClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👥 Client Database Management")
        self.resize(1200, 900)  # ပိုကြီးအောင် ပြင်ထား
        self.setMinimumSize(1000, 800)
        self.setStyleSheet(STYLESHEET)
        self.current_id = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ── Table Section ──────────────────────────────────────────────
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.StyledPanel)
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setSpacing(10)
        table_layout.setContentsMargins(15, 15, 15, 15)

        header_row = QHBoxLayout()
        title_label = QLabel("📋 Client List")
        title_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #2c3e50;
        """)
        header_row.addWidget(title_label)
        header_row.addStretch()

        self.export_btn = QPushButton("📊 Export Excel")
        self.export_btn.setFixedHeight(35)
        self.export_btn.setFixedWidth(140)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 13px;
                border: none;
                padding: 5px 10px;
            }
            QPushButton:hover { 
                background-color: #e67e22; 
            }
            QPushButton:pressed { 
                background-color: #d35400; 
            }
        """)
        self.export_btn.clicked.connect(self.export_to_excel)
        header_row.addWidget(self.export_btn)
        table_layout.addLayout(header_row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Abbr", "Company", "Address", "Contact"])
        self.table.setMinimumHeight(180)
        self.table.setMaximumHeight(220)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #e0e0e0;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 5px;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #3498db;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.itemSelectionChanged.connect(self.load_selected)
        table_layout.addWidget(self.table)
        main_layout.addWidget(table_frame)

        # ── Form Section ───────────────────────────────────────────────
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QFrame.NoFrame)
        form_scroll.setMinimumHeight(450)
        form_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        form_widget = QWidget()
        form_widget.setStyleSheet("background-color: white;")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(10, 10, 10, 10)

        # Basic Info
        basic_frame = QFrame()
        basic_frame.setFrameShape(QFrame.StyledPanel)
        basic_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        basic_row = QHBoxLayout(basic_frame)
        basic_row.setSpacing(15)

        basic_row.addWidget(QLabel("🏢 Company:"))
        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("Company name")
        self.name_in.setMinimumWidth(300)
        self.name_in.setMinimumHeight(35)
        self.name_in.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        basic_row.addWidget(self.name_in)

        basic_row.addWidget(QLabel("📝 Abbr:"))
        self.abbr_in = QLineEdit()
        self.abbr_in.setPlaceholderText("ABC")
        self.abbr_in.setMaxLength(3)
        self.abbr_in.setFixedWidth(80)
        self.abbr_in.setMinimumHeight(35)
        self.abbr_in.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        basic_row.addWidget(self.abbr_in)

        basic_row.addStretch()
        form_layout.addWidget(basic_frame)

        # Addresses
        addr_frame = QFrame()
        addr_frame.setFrameShape(QFrame.StyledPanel)
        addr_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        addr_layout = QVBoxLayout(addr_frame)
        addr_layout.setSpacing(10)

        addr_header = QHBoxLayout()
        addr_label = QLabel("📍 Addresses (3 locations)")
        addr_label.setStyleSheet("font-size: 14px; color: #2c3e50; font-weight: bold;")
        addr_header.addWidget(addr_label)
        addr_header.addStretch()
        addr_layout.addLayout(addr_header)

        self.addrs = []
        for i, lbl in enumerate(["Address 1:", "Address 2:", "Address 3:"]):
            addr_row = QHBoxLayout()
            addr_row.addWidget(QLabel(lbl), 1)

            addr_text = QTextEdit()
            addr_text.setPlaceholderText(f"Enter address {i + 1} (multiple lines allowed)")
            addr_text.setMinimumHeight(70)
            addr_text.setMaximumHeight(100)
            addr_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    padding: 8px;
                    background-color: white;
                    color: #2c3e50;
                    font-size: 13px;
                }
                QTextEdit:focus {
                    border: 2px solid #3498db;
                }
            """)
            addr_row.addWidget(addr_text, 5)
            addr_row.addStretch(1)
            addr_layout.addLayout(addr_row)
            self.addrs.append(addr_text)

        form_layout.addWidget(addr_frame)

        # Contacts
        contact_frame = QFrame()
        contact_frame.setFrameShape(QFrame.StyledPanel)
        contact_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setSpacing(10)

        contact_header = QHBoxLayout()
        contact_label = QLabel("📞 Contacts:")
        contact_label.setStyleSheet("font-size: 14px; color: #2c3e50; font-weight: bold;")
        contact_header.addWidget(contact_label)
        contact_header.addStretch()
        contact_layout.addLayout(contact_header)

        contact_grid = QGridLayout()
        contact_grid.setSpacing(8)

        # Headers
        for col, text in enumerate(["", "Person 1", "Person 2", "Person 3"]):
            lbl = QLabel(text)
            if col > 0:
                lbl.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 13px;")
            else:
                lbl.setStyleSheet("color: #2c3e50; font-size: 13px;")
            contact_grid.addWidget(lbl, 0, col)

        self.contacts = []
        field_labels = ["Name", "Position", "Phone", "Email"]
        field_keys  = ["n",    "p",        "ph",    "em"]

        for row, (field, key) in enumerate(zip(field_labels, field_keys)):
            row_label = QLabel(field + ":")
            row_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 13px;")
            contact_grid.addWidget(row_label, row + 1, 0)

            for col in range(3):
                if len(self.contacts) <= col:
                    self.contacts.append({})
                widget = QLineEdit()
                widget.setPlaceholderText(field)
                widget.setMinimumHeight(32)
                widget.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #d0d0d0;
                        border-radius: 4px;
                        padding: 6px;
                        background-color: white;
                        color: #2c3e50;
                        font-size: 13px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #3498db;
                    }
                """)
                self.contacts[col][key] = widget
                contact_grid.addWidget(widget, row + 1, col + 1)

        contact_layout.addLayout(contact_grid)
        form_layout.addWidget(contact_frame)

        form_layout.addStretch()
        form_scroll.setWidget(form_widget)
        main_layout.addWidget(form_scroll)

        # ── Buttons ────────────────────────────────────────────────────
        btn_frame = QFrame()
        btn_frame.setFrameShape(QFrame.NoFrame)
        btn_frame.setStyleSheet("QFrame { background-color: transparent; }")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(15)

        self.del_btn = QPushButton("🗑️ Delete Client")
        self.del_btn.setEnabled(False)
        self.del_btn.setFixedHeight(45)
        self.del_btn.setFixedWidth(150)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.del_btn.clicked.connect(self.delete_client)
        btn_layout.addWidget(self.del_btn)

        self.clear_btn = QPushButton("🔄 Clear / New")
        self.clear_btn.setFixedHeight(45)
        self.clear_btn.setFixedWidth(150)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_fields)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()

        self.save_btn = QPushButton("💾 Save Data")
        self.save_btn.setFixedHeight(50)
        self.save_btn.setFixedWidth(180)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #27ae60, stop:1 #229954);
            }
        """)
        self.save_btn.clicked.connect(self.save_client)
        btn_layout.addWidget(self.save_btn)

        main_layout.addWidget(btn_frame)

        self.refresh_table()

    # ── Methods (အောက်ပါအတိုင်း မူလအတိုင်းထား) ─────────────────────────────

    def export_to_excel(self):
        try:
            conn = get_db()
            df = pd.read_sql_query("""
                SELECT
                    id          as 'ID',
                    abbr        as 'Abbreviation',
                    name        as 'Company Name',
                    addr1       as 'Address 1',
                    addr2       as 'Address 2',
                    addr3       as 'Address 3',
                    c1_name     as 'Contact 1 Name',
                    c1_pos      as 'Contact 1 Position',
                    c1_ph       as 'Contact 1 Phone',
                    c1_em       as 'Contact 1 Email',
                    c2_name     as 'Contact 2 Name',
                    c2_pos      as 'Contact 2 Position',
                    c2_ph       as 'Contact 2 Phone',
                    c2_em       as 'Contact 2 Email',
                    c3_name     as 'Contact 3 Name',
                    c3_pos      as 'Contact 3 Position',
                    c3_ph       as 'Contact 3 Phone',
                    c3_em       as 'Contact 3 Email'
                FROM clients ORDER BY id DESC
            """, conn)
            conn.close()

            if df.empty:
                QMessageBox.warning(self, "No Data", "Export လုပ်ဖို့ data မရှိပါ!")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to Excel", "clients_database.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if file_path:
                df.to_excel(file_path, index=False, sheet_name="Clients")

                from openpyxl import load_workbook
                wb = load_workbook(file_path)
                ws = wb["Clients"]
                for column in ws.columns:
                    max_length = 0
                    col_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except Exception:
                            pass
                    ws.column_dimensions[col_letter].width = min(max_length + 2, 50)
                wb.save(file_path)

                QMessageBox.information(
                    self, "✅ Export Success!",
                    f"Data ကို Excel ဖိုင်အဖြစ် အောင်မြင်စွာ သိမ်းပြီး!\n\n📁 File: {file_path}"
                )

        except Exception as e:
            QMessageBox.critical(self, "❌ Export Error",
                                 f"Excel export လုပ်ရင်း ပြဿနာ!\n{str(e)}")

    def refresh_table(self):
        self.table.setRowCount(0)
        conn = get_db()
        rows = conn.execute(
            "SELECT id, abbr, name, addr1, c1_name FROM clients ORDER BY id DESC"
        ).fetchall()

        for i, r in enumerate(rows):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(r["abbr"] or ""))
            self.table.setItem(i, 2, QTableWidgetItem(r["name"] or ""))
            addr = r["addr1"] or ""
            if len(addr) > 40:
                addr = addr[:37] + "..."
            self.table.setItem(i, 3, QTableWidgetItem(addr))
            self.table.setItem(i, 4, QTableWidgetItem(r["c1_name"] or "N/A"))

        conn.close()

    def load_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return

        self.current_id = int(self.table.item(rows[0].row(), 0).text())
        self.del_btn.setEnabled(True)
        self.save_btn.setText("💾 Update Data")

        conn = get_db()
        c = conn.execute("SELECT * FROM clients WHERE id=?", (self.current_id,)).fetchone()
        if c:
            self.name_in.setText(c["name"] or "")
            self.abbr_in.setText(c["abbr"] or "")
            for i in range(3):
                self.addrs[i].setText(c[f"addr{i + 1}"] or "")
            for i, contact in enumerate(self.contacts):
                contact["n"].setText(c[f"c{i + 1}_name"] or "")
                contact["p"].setText(c[f"c{i + 1}_pos"]  or "")
                contact["ph"].setText(c[f"c{i + 1}_ph"]  or "")
                contact["em"].setText(c[f"c{i + 1}_em"]  or "")
        conn.close()

    def clear_fields(self):
        self.current_id = None
        self.name_in.clear()
        self.abbr_in.clear()
        for addr in self.addrs:
            addr.clear()
        for contact in self.contacts:
            for w in contact.values():
                w.clear()
        self.del_btn.setEnabled(False)
        self.save_btn.setText("💾 Save Data")
        self.table.clearSelection()

    def delete_client(self):
        if self.current_id and QMessageBox.question(
            self, "Confirm", "Delete this client?"
        ) == QMessageBox.Yes:
            conn = get_db()
            conn.execute("DELETE FROM clients WHERE id=?", (self.current_id,))
            conn.commit()
            conn.close()
            self.refresh_table()
            self.clear_fields()

    def save_client(self):
        if not self.name_in.text():
            QMessageBox.warning(self, "Error", "Company Name လိုအပ်ပါတယ်!")
            return

        vals = [self.name_in.text(), self.abbr_in.text()]
        for addr in self.addrs:
            vals.append(addr.toPlainText())
        for contact in self.contacts:
            vals.append(contact["n"].text())
            vals.append(contact["p"].text())
            vals.append(contact["ph"].text())
            vals.append(contact["em"].text())

        conn = get_db()
        if self.current_id:
            q = """
                UPDATE clients SET
                    name=?, abbr=?,
                    addr1=?, addr2=?, addr3=?,
                    c1_name=?, c1_pos=?, c1_ph=?, c1_em=?,
                    c2_name=?, c2_pos=?, c2_ph=?, c2_em=?,
                    c3_name=?, c3_pos=?, c3_ph=?, c3_em=?
                WHERE id=?
            """
            vals.append(self.current_id)
        else:
            q = """
                INSERT INTO clients (
                    name, abbr,
                    addr1, addr2, addr3,
                    c1_name, c1_pos, c1_ph, c1_em,
                    c2_name, c2_pos, c2_ph, c2_em,
                    c3_name, c3_pos, c3_ph, c3_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

        conn.execute(q, tuple(vals))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "✅ Success", "အောင်မြင်စွာ သိမ်းဆည်းပြီး!")
        self.refresh_table()
        self.clear_fields()
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QPushButton, QLineEdit, 
    QTextEdit, QMessageBox, QGroupBox, QHBoxLayout, 
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
        self.resize(1000, 800)
        self.setMinimumSize(900, 700)
        self.setStyleSheet(STYLESHEET)  # မူလအရောင်အတိုင်း
        self.current_id = None
        
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # === Table Section ===
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.StyledPanel)
        table_frame.setStyleSheet("QFrame { background-color: transparent; border-radius: 8px; padding: 8px; }")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setSpacing(8)
        
        # Table header with title and export button
        header_row = QHBoxLayout()
        title_label = QLabel("📋 Client List")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        header_row.addWidget(title_label)
        header_row.addStretch()
        
        self.export_btn = QPushButton("📊 Export Excel")
        self.export_btn.setFixedHeight(30)
        self.export_btn.setFixedWidth(120)
        self.export_btn.setStyleSheet("""
            QPushButton { 
                background-color: #f59e0b;
                color: white; 
                font-weight: bold; 
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #d97706; }
        """)
        self.export_btn.clicked.connect(self.export_to_excel)
        header_row.addWidget(self.export_btn)
        table_layout.addLayout(header_row)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Abbr", "Company", "Address", "Contact"])
        
        # Table styling
        self.table.setMinimumHeight(150)
        self.table.setMaximumHeight(200)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.itemSelectionChanged.connect(self.load_selected)
        table_layout.addWidget(self.table)
        main_layout.addWidget(table_frame)

        # === Form Section ===
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QFrame.NoFrame)
        form_scroll.setMinimumHeight(400)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 5, 0, 5)

        # 1. Basic Info - Single row
        basic_frame = QFrame()
        basic_frame.setFrameShape(QFrame.StyledPanel)
        basic_frame.setStyleSheet("QFrame { background-color: transparent; border-radius: 6px; padding: 8px; }")
        basic_row = QHBoxLayout(basic_frame)
        basic_row.setSpacing(15)
        
        # Company
        basic_row.addWidget(QLabel("🏢 Company:"))
        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("Company name")
        self.name_in.setMinimumWidth(250)
        basic_row.addWidget(self.name_in)
        
        # Abbr
        basic_row.addWidget(QLabel("📝 Abbr:"))
        self.abbr_in = QLineEdit()
        self.abbr_in.setPlaceholderText("ABC")
        self.abbr_in.setMaxLength(3)
        self.abbr_in.setFixedWidth(60)
        basic_row.addWidget(self.abbr_in)
        
        basic_row.addStretch()
        form_layout.addWidget(basic_frame)

        # 2. Addresses - 3 in a row
        addr_frame = QFrame()
        addr_frame.setFrameShape(QFrame.StyledPanel)
        addr_frame.setStyleSheet("QFrame { background-color: transparent; border-radius: 6px; padding: 8px; }")
        addr_layout = QHBoxLayout(addr_frame)
        addr_layout.setSpacing(8)
        
        addr_layout.addWidget(QLabel("📍 Addresses:"))
        
        self.addrs = []
        for i in range(3):
            addr_text = QLineEdit()
            addr_text.setPlaceholderText(f"Addr {i+1}")
            addr_layout.addWidget(addr_text)
            self.addrs.append(addr_text)
        
        form_layout.addWidget(addr_frame)

        # 3. Contacts - ယှဉ်ရက်ထားတဲ့ပုံစံ
        contact_frame = QFrame()
        contact_frame.setFrameShape(QFrame.StyledPanel)
        contact_frame.setStyleSheet("QFrame { background-color: transparent; border-radius: 6px; padding: 8px; }")
        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setSpacing(8)
        
        # Contact header
        contact_header = QHBoxLayout()
        contact_header.addWidget(QLabel("📞 Contacts:"))
        contact_header.addStretch()
        contact_layout.addLayout(contact_header)
        
        # Table-like contact layout
        contact_grid = QGridLayout()
        contact_grid.setSpacing(5)
        
        # Headers
        headers = ["", "Person 1", "Person 2", "Person 3"]
        for col in range(4):
            if col == 0:
                label = QLabel("")
            else:
                label = QLabel(headers[col])
                label.setStyleSheet("font-weight: bold; color: #475569;")
            contact_grid.addWidget(label, 0, col)
        
        self.contacts = []
        field_labels = ["Name", "Position", "Phone", "Email"]
        
        for row, field in enumerate(field_labels):
            # Row label
            row_label = QLabel(field + ":")
            row_label.setStyleSheet("color: #64748b;")
            contact_grid.addWidget(row_label, row + 1, 0)
            
            for col in range(3):
                if len(self.contacts) <= col:
                    self.contacts.append({})
                
                field_widget = QLineEdit()
                field_widget.setPlaceholderText(field)
                
                if field == "Name":
                    self.contacts[col]['n'] = field_widget
                elif field == "Position":
                    self.contacts[col]['p'] = field_widget
                elif field == "Phone":
                    self.contacts[col]['ph'] = field_widget
                elif field == "Email":
                    self.contacts[col]['em'] = field_widget
                
                contact_grid.addWidget(field_widget, row + 1, col + 1)
        
        contact_layout.addLayout(contact_grid)
        form_layout.addWidget(contact_frame)

        # Add stretch at the end
        form_layout.addStretch()
        
        form_scroll.setWidget(form_widget)
        main_layout.addWidget(form_scroll)

        # === Buttons Section ===
        btn_frame = QFrame()
        btn_frame.setFrameShape(QFrame.NoFrame)
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(10)
        
        self.del_btn = QPushButton("🗑️ Delete Client")
        self.del_btn.setEnabled(False)
        self.del_btn.setFixedHeight(40)
        self.del_btn.setFixedWidth(140)
        self.del_btn.clicked.connect(self.delete_client)
        btn_layout.addWidget(self.del_btn)
        
        self.clear_btn = QPushButton("🔄 Clear / New")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.setFixedWidth(140)
        self.clear_btn.clicked.connect(self.clear_fields)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Save Data")
        self.save_btn.setFixedHeight(45)
        self.save_btn.setFixedWidth(160)
        self.save_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #10b981, stop:1 #059669); 
                font-weight: bold; font-size: 14px; border-radius: 6px;
                color: white;
            }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #34d399, stop:1 #10b981); }
        """)
        self.save_btn.clicked.connect(self.save_client)
        btn_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(btn_frame)

        self.refresh_table()

    # အောက်ပါ method တွေအားလုံး မူလအတိုင်းပဲကျန်ပါတယ်
    def export_to_excel(self):
        """Table data ကို Excel ဖိုင်အဖြစ် ထုတ်ယူတယ်"""
        try:
            conn = get_db()
            df = pd.read_sql_query("""
                SELECT 
                    id as 'ID',
                    abbr as 'Abbreviation', 
                    name as 'Company Name',
                    addr1 as 'Address 1',
                    addr2 as 'Address 2',
                    addr3 as 'Address 3',
                    c1_name as 'Contact 1 Name',
                    c1_pos as 'Contact 1 Position',
                    c1_ph as 'Contact 1 Phone',
                    c1_em as 'Contact 1 Email',
                    c2_name as 'Contact 2 Name',
                    c2_pos as 'Contact 2 Position',
                    c2_ph as 'Contact 2 Phone',
                    c2_em as 'Contact 2 Email',
                    c3_name as 'Contact 3 Name',
                    c3_pos as 'Contact 3 Position',
                    c3_ph as 'Contact 3 Phone',
                    c3_em as 'Contact 3 Email'
                FROM clients 
                ORDER BY id DESC
            """, conn)
            conn.close()

            if df.empty:
                QMessageBox.warning(self, "No Data", "Export လုပ်ဖို့ data မရှိပါ!")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export to Excel", 
                "clients_database.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if file_path:
                df.to_excel(file_path, index=False, sheet_name='Clients')
                
                from openpyxl import load_workbook
                wb = load_workbook(file_path)
                ws = wb['Clients']
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width
                
                wb.save(file_path)
                QMessageBox.information(
                    self, 
                    "✅ Export Success!", 
                    f"Data ကို Excel ဖိုင်အဖြစ် အောင်မြင်စွာ သိမ်းပြီး!\n\n📁 File: {file_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Export Error", f"Excel export လုပ်ရင်း ပြဿနာ!\n{str(e)}")

    def refresh_table(self):
        self.table.setRowCount(0)
        conn = get_db()
        rows = conn.execute("""
            SELECT id, abbr, name, addr1, c1_name 
            FROM clients ORDER BY id DESC
        """).fetchall()
        
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(r['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(r['abbr'] or ""))
            self.table.setItem(i, 2, QTableWidgetItem(r['name'] or ""))
            
            addr = r['addr1'] or ""
            if len(addr) > 40:
                addr = addr[:37] + "..."
            self.table.setItem(i, 3, QTableWidgetItem(addr))
            
            self.table.setItem(i, 4, QTableWidgetItem(r['c1_name'] or "N/A"))
            
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
            self.name_in.setText(c['name'] or "")
            self.abbr_in.setText(c['abbr'] or "")
            
            for i in range(3): 
                self.addrs[i].setText(c[f'addr{i+1}'] or "")
            
            for i in range(3):
                if i < len(self.contacts):
                    if 'n' in self.contacts[i]:
                        self.contacts[i]['n'].setText(c[f'c{i+1}_name'] or "")
                    if 'p' in self.contacts[i]:
                        self.contacts[i]['p'].setText(c[f'c{i+1}_pos'] or "")
                    if 'ph' in self.contacts[i]:
                        self.contacts[i]['ph'].setText(c[f'c{i+1}_ph'] or "")
                    if 'em' in self.contacts[i]:
                        self.contacts[i]['em'].setText(c[f'c{i+1}_em'] or "")
                    
        conn.close()

    def clear_fields(self):
        self.current_id = None
        self.name_in.clear()
        self.abbr_in.clear()
        
        for addr in self.addrs: 
            addr.clear()
            
        for contact in self.contacts:
            if 'n' in contact:
                contact['n'].clear()
            if 'p' in contact:
                contact['p'].clear()
            if 'ph' in contact:
                contact['ph'].clear()
            if 'em' in contact:
                contact['em'].clear()
            
        self.del_btn.setEnabled(False)
        self.save_btn.setText("💾 Save Data")
        self.table.clearSelection()

    def delete_client(self):
        if self.current_id and QMessageBox.question(self, "Confirm", "Delete this client?") == QMessageBox.Yes:
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
            
        vals = [
            self.name_in.text(), 
            self.abbr_in.text()
        ]
        
        # Addresses
        for addr in self.addrs:
            vals.append(addr.text())
            
        # Contacts
        for contact in self.contacts:
            vals.append(contact.get('n', QLineEdit()).text())
            vals.append(contact.get('p', QLineEdit()).text())
            vals.append(contact.get('ph', QLineEdit()).text())
            vals.append(contact.get('em', QLineEdit()).text())
            
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
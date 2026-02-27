"""
Professional Dashboard with KPIs, Charts, and Analytics
========================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries
from database import get_db
from datetime import datetime
import calendar


class KPICard(QFrame):
    """KPI Summary Card Widget"""
    def __init__(self, title, value, subtitle="", icon="", color="#3b82f6"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }}
            QFrame:hover {{
                border: 2px solid {color};
            }}
        """)
        self.setMinimumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Icon + Title
        header_layout = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            icon_font = QFont()
            icon_font.setPointSize(24)
            icon_label.setFont(icon_font)
            icon_label.setStyleSheet(f"color: {color};")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #888;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(32)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_font = QFont()
            subtitle_font.setPointSize(9)
            subtitle_label.setFont(subtitle_font)
            subtitle_label.setStyleSheet("color: #666;")
            layout.addWidget(subtitle_label)
        
        layout.addStretch()


class Dashboard(QWidget):
    # Signals for navigation
    new_invoice_clicked = Signal()
    new_client_clicked = Signal()
    view_invoice_clicked = Signal(int)  # invoice_id
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_dashboard_data()
    
    def init_ui(self):
        """Initialize dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 Dashboard")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(120)
        refresh_btn.clicked.connect(self.load_dashboard_data)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #F9FAFB; }")
        
        container = QWidget()
        content_layout = QVBoxLayout(container)
        content_layout.setSpacing(20)
        
        # ═══════════════════════════════════════════════════════════
        # 1. KPI CARDS (4 cards in a row)
        # ═══════════════════════════════════════════════════════════
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        self.total_invoices_card = KPICard(
            "Total Invoices", "0", "", "📄", "#3b82f6"
        )
        kpi_layout.addWidget(self.total_invoices_card)
        
        self.total_revenue_card = KPICard(
            "Total Revenue", "0 MMK", "", "💰", "#10b981"
        )
        kpi_layout.addWidget(self.total_revenue_card)
        
        self.pending_paid_card = KPICard(
            "Pending / Paid", "0 / 0", "", "⏳", "#f59e0b"
        )
        kpi_layout.addWidget(self.pending_paid_card)
        
        self.month_revenue_card = KPICard(
            "This Month", "0 MMK", "", "📈", "#8b5cf6"
        )
        kpi_layout.addWidget(self.month_revenue_card)
        
        content_layout.addLayout(kpi_layout)
        
        # ═══════════════════════════════════════════════════════════
        # 2. CHARTS (2 columns: Bar Chart + Pie Chart)
        # ═══════════════════════════════════════════════════════════
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Monthly Revenue Bar Chart
        bar_chart_frame = QFrame()
        bar_chart_frame.setFrameShape(QFrame.StyledPanel)
        bar_chart_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        bar_chart_layout = QVBoxLayout(bar_chart_frame)
        
        bar_title = QLabel("📊 Monthly Revenue (Last 12 Months)")
        bar_title_font = QFont()
        bar_title_font.setPointSize(13)
        bar_title_font.setBold(True)
        bar_title.setFont(bar_title_font)
        bar_chart_layout.addWidget(bar_title)
        
        self.bar_chart_view = self.create_bar_chart()
        bar_chart_layout.addWidget(self.bar_chart_view)
        
        charts_layout.addWidget(bar_chart_frame, 2)
        
        # Paid vs Pending Pie Chart
        pie_chart_frame = QFrame()
        pie_chart_frame.setFrameShape(QFrame.StyledPanel)
        pie_chart_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        pie_chart_layout = QVBoxLayout(pie_chart_frame)
        
        pie_title = QLabel("🥧 Invoice Status")
        pie_title_font = QFont()
        pie_title_font.setPointSize(13)
        pie_title_font.setBold(True)
        pie_title.setFont(pie_title_font)
        pie_chart_layout.addWidget(pie_title)
        
        self.pie_chart_view = self.create_pie_chart()
        pie_chart_layout.addWidget(self.pie_chart_view)
        
        charts_layout.addWidget(pie_chart_frame, 1)
        
        content_layout.addLayout(charts_layout)
        
        # ═══════════════════════════════════════════════════════════
        # 3. TWO COLUMN LAYOUT (Recent Invoices + Top Clients)
        # ═══════════════════════════════════════════════════════════
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(15)
        
        # Recent Invoices Table
        recent_frame = QFrame()
        recent_frame.setFrameShape(QFrame.StyledPanel)
        recent_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        recent_layout = QVBoxLayout(recent_frame)
        
        recent_title = QLabel("📋 Recent Invoices (Last 10)")
        recent_title_font = QFont()
        recent_title_font.setPointSize(13)
        recent_title_font.setBold(True)
        recent_title.setFont(recent_title_font)
        recent_layout.addWidget(recent_title)
        
        self.recent_table = QTableWidget(0, 5)
        self.recent_table.setHorizontalHeaderLabels(["Invoice No", "Client", "Date", "Amount", "Status"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setMinimumHeight(350)
        self.recent_table.setMaximumHeight(400)
        self.recent_table.doubleClicked.connect(self.on_invoice_double_clicked)
        recent_layout.addWidget(self.recent_table)
        
        tables_layout.addWidget(recent_frame, 2)
        
        # Top Clients Table
        clients_frame = QFrame()
        clients_frame.setFrameShape(QFrame.StyledPanel)
        clients_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        clients_layout = QVBoxLayout(clients_frame)
        
        clients_title = QLabel("🏆 Top 5 Clients by Revenue")
        clients_title_font = QFont()
        clients_title_font.setPointSize(13)
        clients_title_font.setBold(True)
        clients_title.setFont(clients_title_font)
        clients_layout.addWidget(clients_title)
        
        self.clients_table = QTableWidget(0, 3)
        self.clients_table.setHorizontalHeaderLabels(["Rank", "Client", "Total Revenue"])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.clients_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.clients_table.setMinimumHeight(350)
        self.clients_table.setMaximumHeight(400)
        clients_layout.addWidget(self.clients_table)
        
        tables_layout.addWidget(clients_frame, 1)
        
        content_layout.addLayout(tables_layout)
        
        # ═══════════════════════════════════════════════════════════
        # 4. QUICK ACTIONS
        # ═══════════════════════════════════════════════════════════
        actions_frame = QFrame()
        actions_frame.setFrameShape(QFrame.StyledPanel)
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        actions_layout = QHBoxLayout(actions_frame)
        
        actions_title = QLabel("⚡ Quick Actions")
        actions_title_font = QFont()
        actions_title_font.setPointSize(13)
        actions_title_font.setBold(True)
        actions_title.setFont(actions_title_font)
        actions_layout.addWidget(actions_title)
        
        actions_layout.addStretch()
        
        # New Invoice Button
        new_invoice_btn = QPushButton("📄 New Invoice")
        new_invoice_btn.setFixedHeight(50)
        new_invoice_btn.setFixedWidth(180)
        new_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        new_invoice_btn.clicked.connect(self.new_invoice_clicked.emit)
        actions_layout.addWidget(new_invoice_btn)
        
        # New Client Button
        new_client_btn = QPushButton("👤 New Client")
        new_client_btn.setFixedHeight(50)
        new_client_btn.setFixedWidth(180)
        new_client_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        new_client_btn.clicked.connect(self.new_client_clicked.emit)
        actions_layout.addWidget(new_client_btn)
        
        # View All Invoices Button
        view_all_btn = QPushButton("📋 View All Invoices")
        view_all_btn.setFixedHeight(50)
        view_all_btn.setFixedWidth(180)
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        actions_layout.addWidget(view_all_btn)
        
        content_layout.addWidget(actions_frame)
        
        content_layout.addStretch()
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def create_bar_chart(self):
        """Create monthly revenue bar chart"""
        series = QBarSeries()
        
        bar_set = QBarSet("Revenue")
        bar_set.setColor(QColor("#3b82f6"))
        
        # Placeholder data (will be updated in load_dashboard_data)
        for i in range(12):
            bar_set.append(0)
        
        series.append(bar_set)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Categories (last 12 months)
        categories = []
        today = datetime.now()
        for i in range(11, -1, -1):
            month = (today.month - i - 1) % 12 + 1
            year = today.year - ((today.month - i - 1) < 0)
            categories.append(calendar.month_abbr[month])
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Revenue (MMK)")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def create_pie_chart(self):
        """Create paid vs pending pie chart"""
        series = QPieSeries()
        
        # Placeholder data
        series.append("Paid", 0)
        series.append("Pending", 0)
        
        # Colors
        paid_slice = series.slices()[0]
        paid_slice.setBrush(QColor("#10b981"))
        paid_slice.setLabelVisible(True)
        
        pending_slice = series.slices()[1]
        pending_slice.setBrush(QColor("#f59e0b"))
        pending_slice.setLabelVisible(True)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def load_dashboard_data(self):
        """Load all dashboard data from database"""
        try:
            conn = get_db()
            
            # ═══════════════════════════════════════════════════════════
            # 1. KPI DATA
            # ═══════════════════════════════════════════════════════════
            
            # Total invoices
            total_invoices = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
            
            # Total revenue
            total_revenue = conn.execute("SELECT SUM(grand_total) FROM invoices").fetchone()[0] or 0
            
            # Pending vs Paid
            pending_count = conn.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Pending'").fetchone()[0]
            paid_count = conn.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Paid'").fetchone()[0]
            
            # This month revenue
            today = datetime.now()
            month_start = f"{today.year}-{today.month:02d}-01"
            month_revenue = conn.execute(
                "SELECT SUM(grand_total) FROM invoices WHERE invoice_date >= ?",
                (month_start,)
            ).fetchone()[0] or 0
            
            # Update KPI cards
            self.update_kpi_card(self.total_invoices_card, str(total_invoices))
            self.update_kpi_card(self.total_revenue_card, f"{total_revenue:,.0f} MMK")
            self.update_kpi_card(self.pending_paid_card, f"{pending_count} / {paid_count}")
            self.update_kpi_card(self.month_revenue_card, f"{month_revenue:,.0f} MMK")
            
            # ═══════════════════════════════════════════════════════════
            # 2. MONTHLY REVENUE CHART
            # ═══════════════════════════════════════════════════════════
            
            monthly_data = []
            for i in range(11, -1, -1):
                month = (today.month - i - 1) % 12 + 1
                year = today.year - ((today.month - i - 1) < 0)
                
                month_str = f"{year}-{month:02d}"
                revenue = conn.execute(
                    "SELECT SUM(grand_total) FROM invoices WHERE strftime('%Y-%m', invoice_date) = ?",
                    (month_str,)
                ).fetchone()[0] or 0
                
                monthly_data.append(revenue)
            
            # Update bar chart
            chart = self.bar_chart_view.chart()
            series = chart.series()[0]
            bar_set = series.barSets()[0]
            bar_set.remove(0, 12)
            for value in monthly_data:
                bar_set.append(value)
            
            # Update Y axis range
            max_value = max(monthly_data) if monthly_data else 1000000
            axis_y = chart.axes(Qt.Vertical)[0]
            axis_y.setRange(0, max_value * 1.1)
            
            # ═══════════════════════════════════════════════════════════
            # 3. PIE CHART (Paid vs Pending)
            # ═══════════════════════════════════════════════════════════
            
            chart = self.pie_chart_view.chart()
            series = chart.series()[0]
            series.clear()
            
            if paid_count > 0:
                series.append(f"Paid ({paid_count})", paid_count)
            if pending_count > 0:
                series.append(f"Pending ({pending_count})", pending_count)
            
            # Reapply colors
            if len(series.slices()) > 0:
                series.slices()[0].setBrush(QColor("#10b981"))
                series.slices()[0].setLabelVisible(True)
            if len(series.slices()) > 1:
                series.slices()[1].setBrush(QColor("#f59e0b"))
                series.slices()[1].setLabelVisible(True)
            
            # ═══════════════════════════════════════════════════════════
            # 4. RECENT INVOICES TABLE
            # ═══════════════════════════════════════════════════════════
            
            recent_invoices = conn.execute('''
                SELECT id, invoice_no, company_name, invoice_date, grand_total, status
                FROM invoices
                ORDER BY id DESC
                LIMIT 10
            ''').fetchall()
            
            self.recent_table.setRowCount(0)
            for invoice in recent_invoices:
                row = self.recent_table.rowCount()
                self.recent_table.insertRow(row)
                
                # Invoice No
                self.recent_table.setItem(row, 0, QTableWidgetItem(invoice[1]))
                
                # Client
                self.recent_table.setItem(row, 1, QTableWidgetItem(invoice[2] or "N/A"))
                
                # Date
                self.recent_table.setItem(row, 2, QTableWidgetItem(invoice[3]))
                
                # Amount
                amount_item = QTableWidgetItem(f"{invoice[4]:,.0f} MMK")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.recent_table.setItem(row, 3, amount_item)
                
                # Status
                status = invoice[5]
                status_item = QTableWidgetItem(f"{'✅' if status == 'Paid' else '⏳'} {status}")
                self.recent_table.setItem(row, 4, status_item)
                
                # Store invoice ID for double-click
                self.recent_table.item(row, 0).setData(Qt.UserRole, invoice[0])
            
            # ═══════════════════════════════════════════════════════════
            # 5. TOP CLIENTS TABLE
            # ═══════════════════════════════════════════════════════════
            
            top_clients = conn.execute('''
                SELECT company_name, SUM(grand_total) as total_revenue
                FROM invoices
                WHERE company_name IS NOT NULL
                GROUP BY company_name
                ORDER BY total_revenue DESC
                LIMIT 5
            ''').fetchall()
            
            self.clients_table.setRowCount(0)
            for rank, client in enumerate(top_clients, 1):
                row = self.clients_table.rowCount()
                self.clients_table.insertRow(row)
                
                # Rank with medal
                medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                rank_item = QTableWidgetItem(f"{medals[rank-1]} #{rank}")
                rank_item.setTextAlignment(Qt.AlignCenter)
                self.clients_table.setItem(row, 0, rank_item)
                
                # Client name
                self.clients_table.setItem(row, 1, QTableWidgetItem(client[0]))
                
                # Total revenue
                revenue_item = QTableWidgetItem(f"{client[1]:,.0f} MMK")
                revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.clients_table.setItem(row, 2, revenue_item)
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            import traceback
            traceback.print_exc()
    
    def update_kpi_card(self, card, new_value):
        """Update KPI card value"""
        # Find the value label (3rd child, which is the large value label)
        layout = card.layout()
        if layout and layout.count() >= 2:
            value_label = layout.itemAt(1).widget()
            if isinstance(value_label, QLabel):
                value_label.setText(str(new_value))
    
    def on_invoice_double_clicked(self, index):
        """Handle invoice double-click"""
        row = index.row()
        invoice_id_item = self.recent_table.item(row, 0)
        if invoice_id_item:
            invoice_id = invoice_id_item.data(Qt.UserRole)
            if invoice_id:
                self.view_invoice_clicked.emit(invoice_id)
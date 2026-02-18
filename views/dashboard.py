from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class DashboardView(QWidget):
    def __init__(self, company_name):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel(f"Welcome to {company_name} Dashboard")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #BB86FC;")
        layout.addWidget(label)
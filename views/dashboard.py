from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class DashboardView(QWidget):
    def __init__(self, company_name=None):  # default value ထည့်
        super().__init__()
        # ... ကျန်တဲ့ code ...
        layout = QVBoxLayout(self)
        label = QLabel(f"Welcome to {company_name} Dashboard")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #BB86FC;")
        layout.addWidget(label)
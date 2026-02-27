"""
Theme - Light (White background, Black text)
"""

COLORS = {
    'bg_primary':        '#FFFFFF',
    'bg_sidebar':        '#F5F5F5',
    'bg_card':           '#FFFFFF',
    'bg_input':          '#FFFFFF',
    'bg_button':         '#F0F0F0',
    'bg_button_hover':   '#E0E0E0',
    'bg_button_pressed': '#D0D0D0',
    'bg_hover':          '#EEEEEE',
    'bg_header':         '#F5F5F5',
    'bg_alternate':      '#FAFAFA',
    'bg_disabled':       '#F5F5F5',
    'bg_tooltip':        '#333333',
    'text_primary':   '#1A1A1A',
    'text_secondary': '#555555',
    'text_disabled':  '#AAAAAA',
    'accent': '#2563EB',
    'border': '#DDDDDD',
}


def _build_stylesheet(c):
    return f"""
    QMainWindow, QDialog {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}
    QFrame#Sidebar {{
        background-color: {c['bg_sidebar']};
        border-right: 1px solid {c['border']};
    }}
    QPushButton#NavBtn {{
        text-align: left;
        background: transparent;
        color: {c['text_secondary']};
        border: none;
        font-size: 14px;
        padding: 10px 15px;
    }}
    QPushButton#NavBtn:hover {{
        background-color: {c['bg_hover']};
        color: {c['text_primary']};
        border-left: 4px solid {c['accent']};
    }}
    QGroupBox {{
        color: {c['accent']};
        font-weight: bold;
        border: 1px solid {c['border']};
        border-radius: 8px;
        margin-top: 10px;
        padding: 15px;
        background-color: {c['bg_card']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: {c['accent']};
    }}
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
        background-color: {c['bg_input']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px;
        color: {c['text_primary']};
        selection-background-color: {c['accent']};
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 2px solid {c['accent']};
    }}
    QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
        background-color: {c['bg_disabled']};
        color: {c['text_disabled']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border: 5px solid transparent;
        border-top: 5px solid {c['text_secondary']};
        width: 0;
        height: 0;
        margin-right: 10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['bg_input']};
        border: 1px solid {c['border']};
        selection-background-color: {c['accent']};
        selection-color: white;
        color: {c['text_primary']};
    }}
    QPushButton {{
        background-color: {c['bg_button']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {c['bg_button_hover']};
        border-color: {c['accent']};
    }}
    QPushButton:pressed {{
        background-color: {c['bg_button_pressed']};
    }}
    QPushButton:disabled {{
        background-color: {c['bg_disabled']};
        color: {c['text_disabled']};
        border-color: {c['border']};
    }}
    QTableWidget {{
        background-color: {c['bg_card']};
        alternate-background-color: {c['bg_alternate']};
        gridline-color: {c['border']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
    }}
    QTableWidget::item {{ padding: 5px; }}
    QTableWidget::item:selected {{
        background-color: {c['accent']};
        color: white;
    }}
    QHeaderView::section {{
        background-color: {c['bg_header']};
        color: {c['text_primary']};
        padding: 8px;
        border: none;
        border-bottom: 2px solid {c['accent']};
        font-weight: bold;
    }}
    QScrollBar:vertical {{
        background-color: {c['bg_card']};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {c['text_secondary']};
        border-radius: 6px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{ background-color: {c['accent']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QScrollBar:horizontal {{
        background-color: {c['bg_card']};
        height: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {c['text_secondary']};
        border-radius: 6px;
        min-width: 20px;
    }}
    QScrollBar::handle:horizontal:hover {{ background-color: {c['accent']}; }}
    QScrollArea {{ border: none; background-color: transparent; }}
    QTabWidget::pane {{
        border: 1px solid {c['border']};
        border-radius: 6px;
        background-color: {c['bg_card']};
    }}
    QTabBar::tab {{
        background-color: {c['bg_button']};
        color: {c['text_secondary']};
        padding: 10px 20px;
        margin-right: 2px;
        border: 1px solid {c['border']};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{
        background-color: {c['bg_card']};
        color: {c['accent']};
        font-weight: bold;
        border-bottom: 2px solid {c['accent']};
    }}
    QTabBar::tab:hover {{ background-color: {c['bg_hover']}; }}
    QCheckBox, QRadioButton {{
        color: {c['text_primary']};
        spacing: 8px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {c['border']};
        border-radius: 4px;
        background-color: {c['bg_input']};
    }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
    }}
    QLabel {{ color: {c['text_primary']}; }}
    QToolTip {{
        background-color: {c['bg_tooltip']};
        color: white;
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 5px;
    }}
    QMenuBar {{
        background-color: {c['bg_sidebar']};
        color: {c['text_primary']};
        border-bottom: 1px solid {c['border']};
    }}
    QMenuBar::item {{ padding: 8px 15px; background-color: transparent; }}
    QMenuBar::item:selected {{ background-color: {c['bg_hover']}; }}
    QMenu {{
        background-color: {c['bg_card']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
    }}
    QMenu::item {{ padding: 8px 25px; }}
    QMenu::item:selected {{ background-color: {c['accent']}; color: white; }}
    QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}
    QCalendarWidget QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}
    QCalendarWidget QAbstractItemView {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        selection-background-color: {c['accent']};
        selection-color: white;
    }}
    QCalendarWidget QToolButton {{
        background-color: {c['bg_button']};
        color: {c['text_primary']};
    }}
    QCalendarWidget QMenu {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}
    QSpinBox, QDoubleSpinBox {{
        background-color: {c['bg_input']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 4px;
    }}
    QDateEdit::drop-down {{ border: none; width: 24px; }}
    QDateEdit QAbstractItemView {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}
    """


STYLESHEET = _build_stylesheet(COLORS)


def get_theme(theme_name=None):
    """Always returns light theme (backward compatible)"""
    class _Theme:
        name = "light"
        colors = COLORS
        def get_stylesheet(self):
            return STYLESHEET
    return _Theme()
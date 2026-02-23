"""
Theme System for Billing App
=============================
Light/Dark theme support with user preference storage
"""

class Theme:
    """Base theme class"""
    def __init__(self):
        self.name = "base"
        self.colors = {}
    
    def get_stylesheet(self):
        """Generate QSS stylesheet from theme colors"""
        c = self.colors
        return f"""
        /* ============================================ */
        /* Main Window & Dialog Base                   */
        /* ============================================ */
        QMainWindow, QDialog {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
        }}
        
        /* ============================================ */
        /* Sidebar & Navigation                         */
        /* ============================================ */
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
        
        /* ============================================ */
        /* GroupBox                                     */
        /* ============================================ */
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
        
        /* ============================================ */
        /* Input Fields                                 */
        /* ============================================ */
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
        
        /* ============================================ */
        /* ComboBox Dropdown                            */
        /* ============================================ */
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
        
        /* ============================================ */
        /* Buttons                                      */
        /* ============================================ */
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
        
        /* ============================================ */
        /* Tables                                       */
        /* ============================================ */
        QTableWidget {{
            background-color: {c['bg_card']};
            alternate-background-color: {c['bg_alternate']};
            gridline-color: {c['border']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: 6px;
        }}
        
        QTableWidget::item {{
            padding: 5px;
        }}
        
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
        
        /* ============================================ */
        /* ScrollBar                                    */
        /* ============================================ */
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
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c['accent']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
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
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {c['accent']};
        }}
        
        /* ============================================ */
        /* ScrollArea                                   */
        /* ============================================ */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        /* ============================================ */
        /* TabWidget                                    */
        /* ============================================ */
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
        
        QTabBar::tab:hover {{
            background-color: {c['bg_hover']};
        }}
        
        /* ============================================ */
        /* CheckBox & RadioButton                       */
        /* ============================================ */
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
        
        /* ============================================ */
        /* Labels                                       */
        /* ============================================ */
        QLabel {{
            color: {c['text_primary']};
        }}
        
        /* ============================================ */
        /* Tooltips                                     */
        /* ============================================ */
        QToolTip {{
            background-color: {c['bg_tooltip']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 5px;
        }}
        
        /* ============================================ */
        /* MenuBar                                      */
        /* ============================================ */
        QMenuBar {{
            background-color: {c['bg_sidebar']};
            color: {c['text_primary']};
            border-bottom: 1px solid {c['border']};
        }}
        
        QMenuBar::item {{
            padding: 8px 15px;
            background-color: transparent;
        }}
        
        QMenuBar::item:selected {{
            background-color: {c['bg_hover']};
        }}
        
        QMenu {{
            background-color: {c['bg_card']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
        }}
        
        QMenu::item {{
            padding: 8px 25px;
        }}
        
        QMenu::item:selected {{
            background-color: {c['accent']};
            color: white;
        }}
        """


class DarkTheme(Theme):
    """Dark theme (current)"""
    def __init__(self):
        super().__init__()
        self.name = "dark"
        self.colors = {
            # Backgrounds
            'bg_primary': '#0f0f0f',
            'bg_sidebar': '#161616',
            'bg_card': '#1a1a1a',
            'bg_input': '#1a1a1a',
            'bg_button': '#333333',
            'bg_button_hover': '#444444',
            'bg_button_pressed': '#222222',
            'bg_hover': '#222222',
            'bg_header': '#1a1a1a',
            'bg_alternate': '#151515',
            'bg_disabled': '#0a0a0a',
            'bg_tooltip': '#2a2a2a',
            
            # Text colors
            'text_primary': '#E0E0E0',
            'text_secondary': '#888888',
            'text_disabled': '#555555',
            
            # Accent & borders
            'accent': '#BB86FC',
            'border': '#333333',
        }


class LightTheme(Theme):
    """Light theme (clean and professional)"""
    def __init__(self):
        super().__init__()
        self.name = "light"
        self.colors = {
            # Backgrounds
            'bg_primary': '#FFFFFF',
            'bg_sidebar': '#F9FAFB',
            'bg_card': '#F9FAFB',
            'bg_input': '#FFFFFF',
            'bg_button': '#F3F4F6',
            'bg_button_hover': '#E5E7EB',
            'bg_button_pressed': '#D1D5DB',
            'bg_hover': '#F3F4F6',
            'bg_header': '#F9FAFB',
            'bg_alternate': '#F3F4F6',
            'bg_disabled': '#F3F4F6',
            'bg_tooltip': '#1F2937',
            
            # Text colors
            'text_primary': '#1F2937',
            'text_secondary': '#6B7280',
            'text_disabled': '#9CA3AF',
            
            # Accent & borders
            'accent': '#3B82F6',
            'border': '#E5E7EB',
        }


# Theme registry
THEMES = {
    'dark': DarkTheme(),
    'light': LightTheme(),
}


def get_theme(theme_name='dark'):
    """Get theme by name"""
    return THEMES.get(theme_name, THEMES['dark'])


# Backward compatibility - default dark theme
STYLESHEET = THEMES['dark'].get_stylesheet()

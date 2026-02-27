"""
Views Package Initialization
=============================
All view components for the billing system
"""

# Dialog imports
from .clients import ClientDialog
from .invoice import InvoiceDialog
from .invoice_list import InvoiceListDialog
from .settings import SettingsDialog

# Page imports
from .dashboard import Dashboard

# Utility imports
from .styles import get_theme
from .pdf_generator import InvoicePDFGenerator

# Define what's available when using "from views import *"
__all__ = [
    # Dialogs
    'ClientDialog',
    'InvoiceDialog',
    'InvoiceListDialog',
    'SettingsDialog',
    
    # Pages
    'Dashboard',
    
    # Utilities
    'get_theme',
    'THEMES',
    'InvoicePDFGenerator',
]
"""
Base tab class
"""

import tkinter as tk
from tkinter import ttk
from gui.widgets.base_widget import BaseWidget

class BaseTab(BaseWidget):
    """Base class for all tabs"""
    
    TAB_NAME = "Base Tab"
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup tab UI - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup_ui()")

"""
Base widget class
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Any

class BaseWidget:
    """Base class for all widgets"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.config = app.config
        self.style = app.style_manager
        self.adb = app.adb
        
        self.frame = ttk.Frame(parent)
        self.widgets = {}
    
    def setup_ui(self):
        """Setup UI - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
    def create_label(self, parent, text: str, style: str = None, **kwargs) -> ttk.Label:
        """Create a label"""
        if style:
            label = ttk.Label(parent, text=text, style=style, **kwargs)
        else:
            label = ttk.Label(parent, text=text, **kwargs)
        
        return label
    
    def create_button(self, parent, text: str, command, style: str = 'Tool.TButton', **kwargs) -> ttk.Button:
        """Create a button"""
        button = ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        return button
    
    def create_entry(self, parent, textvariable: tk.Variable = None, **kwargs) -> ttk.Entry:
        """Create an entry widget"""
        entry = ttk.Entry(parent, textvariable=textvariable, **kwargs)
        return entry
    
    def create_scrolled_text(self, parent, height: int = 10, **kwargs) -> tk.Text:
        """Create a scrolled text widget"""
        from tkinter import scrolledtext
        
        default_kwargs = {
            'bg': self.style.colors['terminal_bg'],
            'fg': self.style.colors['fg'],
            'font': ('Consolas', 9),
        }
        default_kwargs.update(kwargs)
        
        text_widget = scrolledtext.ScrolledText(parent, **default_kwargs)
        return text_widget
    
    def create_progress_bar(self, parent, **kwargs) -> ttk.Progressbar:
        """Create a progress bar"""
        default_kwargs = {
            'mode': 'indeterminate',
            'length': 100,
        }
        default_kwargs.update(kwargs)
        
        progress = ttk.Progressbar(parent, **default_kwargs)
        return progress
    
    def update_status(self, message: str):
        """Update main status bar"""
        self.app.update_status(message)
    
    def show_info(self, title: str, message: str):
        """Show info dialog"""
        self.app.show_info(title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning dialog"""
        self.app.show_warning(title, message)
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        self.app.show_error(title, message)
    
    def run_threaded(self, func, *args, **kwargs):
        """Run function in thread"""
        self.app.run_threaded(func, *args, **kwargs)

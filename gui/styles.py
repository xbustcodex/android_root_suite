import tkinter as tk
from tkinter import ttk

class StyleManager:
    """Manages GUI styling"""
    
    def __init__(self):
        self.style = ttk.Style()
        self.setup_styles()
    
    def setup_styles(self):
        """Configure ttk styles"""
        self.style.theme_use('clam')
        
        # Color definitions
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#00ff00',
            'accent': '#007acc',
            'button_bg': '#2d2d30',
            'warning': '#ff6b6b',
            'info': '#ff9900',
            'text': '#cccccc',
            'terminal_bg': '#0c0c0c',
        }
        
        self.configure_styles()
    
    def configure_styles(self):
        """Configure all widget styles"""
        # Title label
        self.style.configure('Title.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['fg'],
                           font=('Arial', 16, 'bold'))
        
        # Subtitle label
        self.style.configure('Subtitle.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['text'],
                           font=('Arial', 10))
        
        # Status label
        self.style.configure('Status.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['info'],
                           font=('Arial', 9))
        
        # Tool button
        self.style.configure('Tool.TButton',
                           background=self.colors['button_bg'],
                           foreground='white',
                           borderwidth=1,
                           relief='raised',
                           padding=10)
        
        self.style.map('Tool.TButton',
                      background=[('active', '#3e3e42')])
        
        # Success button
        self.style.configure('Green.TButton',
                           background='#2e7d32',
                           foreground='white')
        
        # Danger button
        self.style.configure('Red.TButton',
                           background='#c62828',
                           foreground='white')
        
        # Warning label
        self.style.configure('Warning.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['warning'],
                           font=('Arial', 9, 'italic'))
        
        # Notebook/Tab style
        self.style.configure('Custom.TNotebook', background=self.colors['bg'])
        self.style.configure('Custom.TNotebook.Tab',
                           background=self.colors['button_bg'],
                           foreground='white',
                           padding=[10, 5])
        
        self.style.map('Custom.TNotebook.Tab',
                      background=[('selected', self.colors['accent'])])

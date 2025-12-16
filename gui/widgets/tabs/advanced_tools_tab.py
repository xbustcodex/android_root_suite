"""
Advanced Tools Tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class AdvancedToolsTab:
    """Advanced Tools Tab"""
    
    TAB_NAME = "Advanced Tools"
    
    def __init__(self, parent, app: 'ADBRootToolGUI'):
        self.parent = parent
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI for advanced tools tab"""
        # Tools grid
        self.create_tools_grid()
        
        # Terminal output area
        self.create_terminal_section()
    
    def create_tools_grid(self):
        """Create grid of advanced tools"""
        tools_grid = [
            ("Screen Recording", self.app.screen_record),
            ("Screenshot", self.app.take_screenshot),
            ("Install APK", self.app.install_apk),
            ("Pull Files", self.app.pull_files),
            ("Push Files", self.app.push_files),
            ("ADB Shell", self.app.open_adb_shell),
            ("Reboot Options", self.app.show_reboot_menu),
            ("Remove Bloatware", self.app.remove_bloatware),
            ("View Logcat", self.app.view_logcat),
            ("Check Root", self.app.check_root),
            ("List Apps", self.app.list_apps),
            ("File Explorer", self.app.open_file_explorer),
        ]
        
        # Create 3x4 grid
        row, col = 0, 0
        for text, command in tools_grid:
            btn = ttk.Button(
                self.frame,
                text=text,
                command=command,
                style='Tool.TButton'
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(3):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(4):
            self.frame.grid_rowconfigure(i, weight=1)
    
    def create_terminal_section(self):
        """Create terminal output section"""
        ttk.Separator(self.frame, orient='horizontal').grid(
            row=4, column=0, columnspan=3, sticky='ew', pady=20
        )
        
        ttk.Label(
            self.frame,
            text="Terminal Output",
            font=('Arial', 10, 'bold'),
            background=self.app.style_manager.colors['bg'],
            foreground=self.app.style_manager.colors['fg']
        ).grid(row=5, column=0, columnspan=3, pady=5)
        
        self.terminal_text = scrolledtext.ScrolledText(
            self.frame,
            height=10,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        self.terminal_text.grid(
            row=6, column=0, columnspan=3, padx=10, pady=10, sticky='nsew'
        )
        
        self.frame.grid_rowconfigure(6, weight=1)

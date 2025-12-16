import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Tuple

class MainToolsTab:
    """Main Tools Tab"""
    
    TAB_NAME = "Main Tools"
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.config = app.config
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI for main tools tab"""
        # Create scrollable canvas
        self.canvas = tk.Canvas(
            self.frame,
            bg=self.app.style_manager.colors['bg'],
            highlightthickness=0
        )
        
        self.scrollbar = ttk.Scrollbar(
            self.frame,
            orient="vertical",
            command=self.canvas.yview
        )
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Define tools
        tools = self.get_tool_list()
        
        # Create tool buttons
        for text, command in tools:
            btn = ttk.Button(
                self.scrollable_frame,
                text=text,
                command=command,
                style='Tool.TButton'
            )
            btn.pack(fill='x', padx=20, pady=5, ipady=10)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def get_tool_list(self) -> List[Tuple[str, callable]]:
        """Get list of tools for main tab"""
        return [
            ("ADB Setup & Device Check", self.app.show_adb_setup),
            ("Device Information Scan", self.app.show_device_info),
            ("COMPLETE BACKUP (ESSENTIAL)", self.app.start_complete_backup),
            ("Backup Boot Image Only", self.app.show_backup_boot),
            ("Patch Boot with Magisk/KernelSU", self.app.show_patch_boot),
            ("Flash Patched Boot/Recovery", self.app.show_flash_tools),
            ("Install Custom Recovery (TWRP)", self.app.show_install_recovery),
            ("Device-Specific Rooting Guide", self.app.show_root_guide),
            ("Advanced ADB Tools", self.app.show_advanced_tools),
            ("Install USB Drivers", self.app.show_driver_install),
        ]

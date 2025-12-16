"""
Brand Tools Tab
"""

import os
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple

from gui.widgets.tabs.base_tab import BaseTab
from config.constants import BRAND_TOOLS, DRIVER_PACKS

class BrandToolsTab(BaseTab):
    """Brand Tools Tab"""
    
    TAB_NAME = "Brand Tools"
    
    def setup_ui(self):
        """Setup brand tools UI"""
        # Create scrollable frame
        canvas = tk.Canvas(self.frame, bg=self.style.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = self.create_label(
            scrollable_frame,
            text="Brand-Specific Tools",
            font=('Arial', 12, 'bold'),
            background=self.style.colors['bg'],
            foreground=self.style.colors['fg']
        )
        title_label.pack(pady=10)
        
        # Brand tools section
        self.create_brand_tools_section(scrollable_frame)
        
        # Drivers section
        self.create_drivers_section(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_brand_tools_section(self, parent):
        """Create brand tools section"""
        for brand_name, brand_key, tool_name in BRAND_TOOLS:
            btn_frame = ttk.Frame(parent)
            btn_frame.pack(pady=10, padx=50, fill='x')
            
            # Create button
            btn = self.create_button(
                btn_frame,
                text=f"{brand_name} ({tool_name})",
                command=self.get_brand_command(brand_key),
                style='Tool.TButton'
            )
            btn.pack(fill='x')
            
            # Show tool count if available
            brand_dir = self.config.PATHS.get(brand_key, "")
            tool_count = self.get_tool_count(brand_dir)
            
            if tool_count > 0:
                count_label = self.create_label(
                    btn_frame,
                    text=f"Tools available: {tool_count}",
                    background=self.style.colors['bg'],
                    foreground='#888888',
                    font=('Arial', 8)
                )
                count_label.pack()
    
    def get_tool_count(self, directory: str) -> int:
        """Get count of tool files in directory"""
        if not os.path.exists(directory):
            return 0
        
        tool_extensions = ('.exe', '.zip', '.bin', '.img', '.tar', '.md5')
        tool_files = [
            f for f in os.listdir(directory)
            if f.lower().endswith(tool_extensions)
        ]
        
        return len(tool_files)
    
    def get_brand_command(self, brand_key: str):
        """Get command for brand tool"""
        commands = {
            'samsung': self.show_samsung_tools,
            'xiaomi': self.show_xiaomi_tools,
            'qualcomm': self.show_qualcomm_tools,
            'mediatek': self.show_mediatek_tools,
        }
        return commands.get(brand_key, lambda: None)
    
    def create_drivers_section(self, parent):
        """Create drivers section"""
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', padx=20, pady=20)
        
        # Title
        drivers_label = self.create_label(
            parent,
            text="USB Drivers",
            font=('Arial', 11, 'bold'),
            background=self.style.colors['bg'],
            foreground=self.style.colors['info']
        )
        drivers_label.pack(pady=5)
        
        # Driver install button
        driver_btn = self.create_button(
            parent,
            text="Install USB Drivers",
            command=self.show_driver_install,
            style='Green.TButton'
        )
        driver_btn.pack(pady=10, padx=50, fill='x')
    
    def show_samsung_tools(self):
        """Show Samsung tools"""
        self.app.show_samsung_tools()
    
    def show_xiaomi_tools(self):
        """Show Xiaomi tools"""
        self.app.show_xiaomi_tools()
    
    def show_qualcomm_tools(self):
        """Show Qualcomm tools"""
        self.app.show_qualcomm_tools()
    
    def show_mediatek_tools(self):
        """Show MediaTek tools"""
        self.app.show_mediatek_tools()
    
    def show_driver_install(self):
        """Show driver installation dialog"""
        self.app.show_driver_install()

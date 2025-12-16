"""
Root Tools Tab
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple

from gui.widgets.tabs.base_tab import BaseTab
from config.constants import ROOT_METHODS, BRAND_TOOLS

class RootToolsTab(BaseTab):
    """Root Tools Tab"""
    
    TAB_NAME = "Root Tools"
    
    def setup_ui(self):
        """Setup root tools UI"""
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
            text="Rooting Solutions",
            font=('Arial', 12, 'bold'),
            background=self.style.colors['bg'],
            foreground=self.style.colors['fg']
        )
        title_label.pack(pady=10)
        
        # Root method buttons
        self.create_root_methods_section(scrollable_frame)
        
        # Rooting guides section
        self.create_guides_section(scrollable_frame)
        
        # Warnings section
        self.create_warnings_section(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_root_methods_section(self, parent):
        """Create root methods section"""
        for text, method_id in ROOT_METHODS:
            btn = self.create_button(
                parent,
                text=text,
                command=self.get_root_method_command(method_id),
                style='Tool.TButton'
            )
            btn.pack(pady=5, padx=50, fill='x')
    
    def get_root_method_command(self, method_id: str):
        """Get command for root method"""
        commands = {
            'magisk': self.show_magisk_patch,
            'kernelsu': self.show_kernelsu_info,
            'apatch': self.show_apatch_info,
        }
        return commands.get(method_id, lambda: None)
    
    def create_guides_section(self, parent):
        """Create rooting guides section"""
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', padx=20, pady=20)
        
        # Title
        guides_label = self.create_label(
            parent,
            text="Rooting Guides",
            font=('Arial', 11, 'bold'),
            background=self.style.colors['bg'],
            foreground=self.style.colors['info']
        )
        guides_label.pack(pady=5)
        
        # Guide buttons
        guides = [
            ("Samsung Root Guide", lambda: self.show_brand_guide('samsung')),
            ("Xiaomi Root Guide", lambda: self.show_brand_guide('xiaomi')),
            ("Google Pixel Guide", lambda: self.show_brand_guide('google')),
            ("OnePlus Guide", lambda: self.show_brand_guide('oneplus')),
            ("Generic Root Guide", self.show_generic_guide),
        ]
        
        for text, command in guides:
            btn = self.create_button(parent, text, command, style='Tool.TButton')
            btn.pack(pady=2, padx=30, fill='x')
    
    def create_warnings_section(self, parent):
        """Create warnings section"""
        # Warning frame
        warning_frame = ttk.Frame(parent, relief='sunken', borderwidth=1)
        warning_frame.pack(pady=20, padx=20, fill='x')
        
        # Warning title
        warning_title = self.create_label(
            warning_frame,
            text="⚠️ WARNING ⚠️",
            font=('Arial', 10, 'bold'),
            background=self.style.colors['bg'],
            foreground=self.style.colors['warning'],
            justify='center'
        )
        warning_title.pack(pady=5)
        
        # Warning list
        warnings = [
            "• Voids warranty",
            "• Can brick device",
            "• Security risks",
            "• Breaks OTA updates",
            "• Banking apps may fail",
        ]
        
        for warning in warnings:
            warning_label = self.create_label(
                warning_frame,
                text=warning,
                background=self.style.colors['bg'],
                foreground=self.style.colors['warning'],
                font=('Arial', 9)
            )
            warning_label.pack(anchor='w', padx=10)
    
    def show_magisk_patch(self):
        """Show Magisk patch instructions"""
        self.app.show_patch_boot()
    
    def show_kernelsu_info(self):
        """Show KernelSU info"""
        self.show_info(
            "KernelSU",
            "KernelSU - Kernel-based root solution\n\n"
            "KernelSU requires:\n"
            "- Kernel with KernelSU support built-in\n"
            "- Or patching kernel source and recompiling\n"
            "- For GKI devices, use KernelSU kernel patches\n\n"
            "APK: KernelSU_v3.0.0_32179-release.apk\n\n"
            "Visit: https://kernelsu.org for more info"
        )
    
    def show_apatch_info(self):
        """Show APatch info"""
        self.show_info(
            "APatch",
            "APatch - Alternative to Magisk\n\n"
            "APatch works similar to Magisk:\n"
            "1. Install APatch app\n"
            "2. Patch boot image\n"
            "3. Flash patched image\n\n"
            "APK: APatch_11107_11107-release-signed.apk"
        )
    
    def show_brand_guide(self, brand: str):
        """Show brand-specific rooting guide"""
        self.app.show_brand_guide(brand)
    
    def show_generic_guide(self):
        """Show generic rooting guide"""
        self.app.show_generic_guide()

"""
Samsung-specific tools
"""

import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class SamsungTools:
    """Samsung device tools"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
    
    def show_tools(self):
        """Show Samsung tools window"""
        window = tk.Toplevel(self.app.root)
        window.title("Samsung Tools")
        window.geometry("700x500")
        window.configure(bg=self.app.style_manager.colors['bg'])
        
        self.create_ui(window)
    
    def create_ui(self, window):
        """Create Samsung tools UI"""
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Find Odin versions
        odin_dir = os.path.join(self.app.config.PATHS['tools'], 'odin')
        odin_versions = []
        
        if os.path.exists(odin_dir):
            for item in os.listdir(odin_dir):
                if 'odin' in item.lower():
                    odin_versions.append(item)
        
        text_widget.insert('end', "SAMSUNG TOOLS - Odin\n")
        text_widget.insert('end', "=" * 50 + "\n\n")
        
        if odin_versions:
            text_widget.insert('end', "Odin versions available:\n")
            for version in odin_versions:
                text_widget.insert('end', f"  - {version}\n")
            text_widget.insert('end', "\n")
        else:
            text_widget.insert('end', "No Odin versions found.\n\n")
        
        instructions = """INSTRUCTIONS:

1. Enter Download Mode:
   - Power off device
   - Hold Vol Down + Power + Home
   - Release when warning appears
   - Press Vol Up to continue

2. Connect USB cable

3. Open Odin3.exe as Administrator

4. Load firmware files:
   - AP: System, boot, recovery
   - BL: Bootloader
   - CP: Modem/Radio
   - CSC: Carrier/Region

5. Important settings:
   - Auto Reboot: ✓
   - F. Reset Time: ✓
   - Re-Partition: ✗ (unless instructed)

6. Click Start

WARNINGS:
- Trips Knox (voids warranty permanently)
- Breaks Secure Folder, Samsung Pay
- Can brick if wrong firmware used
- Backup EFS partition if possible

For rooting: Patch AP file with Magisk first!"""
        
        text_widget.insert('end', instructions)
        text_widget.config(state='disabled')
        
        # Buttons
        self.create_buttons(window, odin_dir)
    
    def create_buttons(self, window, odin_dir):
        """Create Samsung tools buttons"""
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        if odin_dir and os.path.exists(odin_dir):
            ttk.Button(
                btn_frame,
                text="Open Odin Folder",
                command=lambda: os.startfile(odin_dir)
            ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=window.destroy
        ).pack(side='right', padx=5)

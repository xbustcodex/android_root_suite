"""
ADB Setup Dialog
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class ADBSetupDialog:
    """ADB Setup Dialog"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
        self.window = None
        self.text_widget = None
    
    def show(self):
        """Show ADB setup window"""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("ADB Setup & Device Check")
        self.window.geometry("600x400")
        self.window.configure(bg=self.app.style_manager.colors['bg'])
        
        self.create_ui()
        self.refresh_info()
    
    def create_ui(self):
        """Create UI for ADB setup dialog"""
        # Create text widget for output
        self.text_widget = scrolledtext.ScrolledText(
            self.window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        self.text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons
        self.create_buttons()
    
    def create_buttons(self):
        """Create dialog buttons"""
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Check Again",
            command=self.refresh_info
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=self.window.destroy
        ).pack(side='right', padx=5)
    
    def refresh_info(self):
        """Refresh ADB and device information"""
        if not self.text_widget:
            return
        
        self.text_widget.config(state='normal')
        self.text_widget.delete(1.0, 'end')
        
        # Check ADB status
        adb_ok, msg = self.app.adb.check_adb()
        self.text_widget.insert('end', f"ADB Status: {msg}\n\n")
        
        # Get devices
        devices = self.app.adb.get_devices()
        self.text_widget.insert('end', f"Connected Devices ({len(devices)}):\n")
        self.text_widget.insert('end', "-" * 40 + "\n")
        
        for device in devices:
            self.text_widget.insert('end', f"{device['serial']}\t{device['status']}\n")
        
        if not devices:
            self.text_widget.insert('end', "\nTroubleshooting Steps:\n")
            self.text_widget.insert('end', "1. Enable Developer Options\n")
            self.text_widget.insert('end', "2. Enable USB Debugging\n")
            self.text_widget.insert('end', "3. Install USB Drivers\n")
            self.text_widget.insert('end', "4. Try different USB cable/port\n")
            self.text_widget.insert('end', "5. Check phone for 'Allow USB debugging?' prompt\n")
        
        self.text_widget.config(state='disabled')

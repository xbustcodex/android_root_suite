"""
Device Information Dialog
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class DeviceInfoDialog:
    """Device Information Dialog"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
        self.window = None
    
    def show(self):
        """Show device information window"""
        if not self.app.current_device:
            self.app.show_warning("No Device", "Connect a device first")
            return
        
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Device Information")
        self.window.geometry("700x600")
        self.window.configure(bg=self.app.style_manager.colors['bg'])
        
        self.create_ui()
    
    def create_ui(self):
        """Create UI for device info dialog"""
        # Create notebook for different info sections
        notebook = ttk.Notebook(self.window, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Basic Info Tab
        self.create_basic_info_tab(notebook)
        
        # Advanced Info Tab
        self.create_advanced_info_tab(notebook)
        
        # Root Check Tab
        self.create_root_info_tab(notebook)
        
        # Buttons
        self.create_buttons()
    
    def create_basic_info_tab(self, notebook):
        """Create basic device info tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Basic Info")
        
        # Get device properties
        from config.constants import DEVICE_PROPERTIES
        props = self.app.adb.get_device_props(DEVICE_PROPERTIES[:9])  # First 9 basic props
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        for prop, value in props.items():
            prop_name = prop.replace('ro.', '').replace('.', ' ')
            text_widget.insert('end', f"{prop_name.title()}: {value}\n")
        
        text_widget.config(state='disabled')
    
    def create_advanced_info_tab(self, notebook):
        """Create advanced device info tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Advanced")
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Get more props
        from config.constants import DEVICE_PROPERTIES
        props = self.app.adb.get_device_props(DEVICE_PROPERTIES[9:])  # Remaining props
        
        for prop, value in props.items():
            prop_name = prop.replace('ro.', '').replace('.', ' ')
            text_widget.insert('end', f"{prop_name}: {value}\n")
        
        text_widget.config(state='disabled')
    
    def create_root_info_tab(self, notebook):
        """Create root status tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Root Status")
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Check root status
        from core.device_manager import DeviceManager
        device_mgr = DeviceManager(self.app.adb)
        status = device_mgr.check_root_status()
        
        if status['rooted']:
            text_widget.insert('end', "[✓] ROOTED\n")
            text_widget.insert('end', f"Method: {status['method']}\n")
            if status['version'] != 'Unknown':
                text_widget.insert('end', f"Version: {status['version']}\n")
        else:
            text_widget.insert('end', "[✗] NOT ROOTED\n")
        
        text_widget.config(state='disabled')
    
    def create_buttons(self):
        """Create dialog buttons"""
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Save to File",
            command=self.save_device_info
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=self.window.destroy
        ).pack(side='right', padx=5)
    
    def save_device_info(self):
        """Save device info to file"""
        from config.constants import DEVICE_PROPERTIES
        props = self.app.adb.get_device_props(DEVICE_PROPERTIES)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"device_info_{self.app.config.TIMESTAMP}.txt"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Device Information\n")
                f.write("=" * 50 + "\n\n")
                for prop, value in props.items():
                    prop_name = prop.replace('ro.', '').replace('.', ' ')
                    f.write(f"{prop_name.title()}: {value}\n")
            
            self.app.show_info("Saved", f"Device information saved to:\n{filename}")

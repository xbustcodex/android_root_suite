"""
Boot Patching Dialog
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class PatchingDialog:
    """Boot Patching Dialog"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
        self.window = None
    
    def show(self):
        """Show boot patching window"""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Patch Boot Image")
        self.window.geometry("700x500")
        self.window.configure(bg=self.app.style_manager.colors['bg'])
        
        self.create_ui()
    
    def create_ui(self):
        """Create UI for patching dialog"""
        # Create notebook for different methods
        notebook = ttk.Notebook(self.window, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Magisk Tab
        self.create_magisk_tab(notebook)
        
        # KernelSU Tab
        self.create_kernelsu_tab(notebook)
        
        # APatch Tab
        self.create_apatch_tab(notebook)
    
    def create_magisk_tab(self, notebook):
        """Create Magisk patching tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Magisk")
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        instructions = """Magisk v29.0 - Recommended for most devices
==================================================

Steps to patch boot image:

1. Copy boot.img to device: /sdcard/boot.img
2. Install Magisk app
3. Open Magisk app
4. Tap Install > Select and Patch a File
5. Choose /sdcard/boot.img
6. Copy patched file from /sdcard/ to PC
7. Save as patchedboot.img in backup folder"""
        
        text_widget.insert('end', instructions)
        text_widget.config(state='disabled')
        
        # Browse button
        def browse_boot_img():
            filename = filedialog.askopenfilename(
                title="Select boot.img",
                filetypes=[("Boot images", "*.img"), ("All files", "*.*")]
            )
            if filename:
                self.app.adb.push_file(filename, '/sdcard/boot.img')
                self.app.show_info(
                    "Success",
                    "boot.img copied to device\n\nNow install Magisk app and patch the file."
                )
        
        ttk.Button(
            frame,
            text="Browse for boot.img",
            command=browse_boot_img
        ).pack(pady=10)
    
    def create_kernelsu_tab(self, notebook):
        """Create KernelSU tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="KernelSU")
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        info = """KernelSU - Kernel-based root solution
==================================================

KernelSU requires:

1. Kernel with KernelSU support built-in
2. Or patching kernel source and recompiling
3. For GKI devices, use KernelSU kernel patches

APK: KernelSU_v3.0.0_32179-release.apk

Visit: https://kernelsu.org for more info"""
        
        text_widget.insert('end', info)
        text_widget.config(state='disabled')
    
    def create_apatch_tab(self, notebook):
        """Create APatch tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="APatch")
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        info = """APatch - Alternative to Magisk
==================================================

APatch works similar to Magisk:

1. Install APatch app
2. Patch boot image
3. Flash patched image

APK: APatch_11107_11107-release-signed.apk"""
        
        text_widget.insert('end', info)
        text_widget.config(state='disabled')
        
        # Close button
        ttk.Button(
            self.window,
            text="Close",
            command=self.window.destroy
        ).pack(pady=10)

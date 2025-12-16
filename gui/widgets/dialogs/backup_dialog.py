"""
Backup Dialog
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class BackupDialog:
    """Backup Operation Dialog"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
        self.window = None
    
    def show_backup_boot(self):
        """Show backup boot image dialog"""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Backup Boot Image")
        self.window.geometry("500x400")
        self.window.configure(bg=self.app.style_manager.colors['bg'])
        
        self.create_backup_boot_ui()
    
    def create_backup_boot_ui(self):
        """Create UI for backup boot dialog"""
        # Title
        ttk.Label(
            self.window,
            text="Select backup method:",
            background=self.app.style_manager.colors['bg'],
            foreground=self.app.style_manager.colors['fg'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        # Method selection
        method_var = tk.StringVar(value="adb")
        
        methods = [
            ("Via ADB (requires root)", "adb"),
            ("Via Fastboot (unlocked bootloader)", "fastboot"),
            ("Extract from firmware file", "extract"),
        ]
        
        for text, value in methods:
            rb = ttk.Radiobutton(
                self.window,
                text=text,
                variable=method_var,
                value=value,
                style='Tool.TButton'
            )
            rb.pack(pady=5, padx=20, anchor='w')
        
        # Info text
        info_text = scrolledtext.ScrolledText(
            self.window,
            height=10,
            bg='#0c0c0c',
            fg='#cccccc',
            font=('Arial', 9)
        )
        info_text.pack(padx=20, pady=10, fill='x')
        info_text.insert('end', "ADB method:\n- Requires rooted device\n- Dumps boot partition directly\n- Saves as ogboot.img")
        info_text.config(state='disabled')
        
        # Update info based on selection
        def update_info(*args):
            info_text.config(state='normal')
            info_text.delete(1.0, 'end')
            
            if method_var.get() == "adb":
                info_text.insert('end', "ADB method:\n- Requires rooted device\n- Dumps boot partition directly\n- Saves as ogboot.img")
            elif method_var.get() == "fastboot":
                info_text.insert('end', "Fastboot method:\n- Requires unlocked bootloader\n- Need to extract from firmware\n- Manual process")
            else:
                info_text.insert('end', f"Extract from firmware:\n- Place firmware in: {self.app.config.PATHS['stock_firmware']}\n- Use extractor tool\n- Copy to: {self.app.config.PATHS['boot_images']}")
            
            info_text.config(state='disabled')
        
        method_var.trace('w', update_info)
        
        # Buttons
        self.create_backup_buttons(method_var)
    
    def create_backup_buttons(self, method_var):
        """Create backup action buttons"""
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        def start_backup():
            method = method_var.get()
            if method == "adb":
                self.start_adb_backup()
            elif method == "fastboot":
                self.app.show_info(
                    "Fastboot Backup",
                    "Reboot to bootloader and use:\n\nfastboot getvar all\nfastboot flash boot boot.img"
                )
            else:
                if os.path.exists(self.app.config.PATHS['stock_firmware']):
                    os.startfile(self.app.config.PATHS['stock_firmware'])
                self.app.show_info(
                    "Extract Firmware",
                    f"Place firmware files in:\n{self.app.config.PATHS['stock_firmware']}\n\nThen extract boot.img using appropriate tool."
                )
            
            self.window.destroy()
        
        ttk.Button(
            btn_frame,
            text="Start Backup",
            command=start_backup,
            style='Green.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.window.destroy
        ).pack(side='right', padx=5)
    
    def start_adb_backup(self):
        """Start ADB backup process"""
        from core.backup_manager import BackupManager
        backup_mgr = BackupManager(self.app.adb)
        
        self.app.update_status("Backing up boot image...")
        self.app.progress.start()
        
        def backup():
            backup_folder = self.app.config.get_backup_folder()
            success, file_path = backup_mgr.backup_boot_image(backup_folder)
            
            self.app.progress.stop()
            
            if success:
                self.app.root.after(0, lambda: self.app.show_info(
                    "Success",
                    f"Boot image backed up successfully!\n\nSaved to: {file_path}"
                ))
                self.app.update_status("Boot backup completed")
            else:
                self.app.root.after(0, lambda: self.app.show_warning(
                    "Failed",
                    "Could not backup boot image.\n\nPossible reasons:\n"
                    "- Device not rooted\n"
                    "- Different partition naming\n"
                    "- Insufficient permissions\n\n"
                    "Try extracting from firmware instead."
                ))
        
        self.app.run_threaded(backup)

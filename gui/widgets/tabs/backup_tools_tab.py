"""
Backup Tools Tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from typing import List, Tuple

from gui.widgets.tabs.base_tab import BaseTab
from utils.file_utils import format_file_size

class BackupToolsTab(BaseTab):
    """Backup Tools Tab"""
    
    TAB_NAME = "Backup Tools"
    
    def setup_ui(self):
        """Setup backup tools UI"""
        # Main container with padding
        main_frame = ttk.Frame(self.frame, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = self.create_label(
            main_frame,
            text="Backup Management",
            font=('Arial', 12, 'bold'),
            background=self.style.colors['bg'],
            foreground=self.style.colors['fg']
        )
        title_label.pack(pady=10)
        
        # Backup folder info
        backup_folder = self.config.get_backup_folder()
        folder_label = self.create_label(
            main_frame,
            text=f"Current backup folder:\n{backup_folder}",
            background=self.style.colors['bg'],
            foreground=self.style.colors['text'],
            justify='center'
        )
        folder_label.pack(pady=10)
        
        # Backup buttons
        self.create_backup_buttons(main_frame)
        
        # Backup stats
        self.backup_stats_label = self.create_label(
            main_frame,
            text="",
            background=self.style.colors['bg'],
            foreground='#888888'
        )
        self.backup_stats_label.pack(pady=10)
        
        # Update stats
        self.update_backup_stats()
    
    def create_backup_buttons(self, parent):
        """Create backup action buttons"""
        buttons = [
            ("Start Complete Backup", self.start_complete_backup, 'Green.TButton'),
            ("Backup Boot Image", self.show_backup_boot, 'Tool.TButton'),
            ("Backup Single App", self.backup_single_app, 'Tool.TButton'),
            ("Backup User Data (Photos, Docs)", self.backup_user_data, 'Tool.TButton'),
            ("View Backup Manager", self.show_backup_manager, 'Tool.TButton'),
        ]
        
        for text, command, style in buttons:
            btn = self.create_button(parent, text, command, style)
            btn.pack(pady=5, padx=50, fill='x')
    
    def start_complete_backup(self):
        """Start complete device backup"""
        if not self.app.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        from gui.utils import DialogHelper
        if DialogHelper.ask_yesno(self.frame, "Complete Backup", 
                                 self.get_backup_warning_text()):
            self.app.start_complete_backup()
    
    def get_backup_warning_text(self) -> str:
        """Get backup warning text"""
        return (
            "This will create a complete backup including:\n\n"
            "1. Boot partition image\n"
            "2. App data backup (.ab file)\n"
            "3. Critical user data\n"
            "4. System information\n\n"
            "Make sure you have enough storage space.\n\n"
            "Continue?"
        )
    
    def show_backup_boot(self):
        """Show backup boot image dialog"""
        from gui.widgets.dialogs import BackupDialog
        dialog = BackupDialog(self.frame, self.app)
        dialog.show()
    
    def backup_single_app(self):
        """Backup single app"""
        from gui.widgets.dialogs.backup_dialog import AppBackupDialog
        dialog = AppBackupDialog(self.frame, self.app)
        dialog.show()
    
    def backup_user_data(self):
        """Backup user data"""
        from gui.widgets.dialogs.backup_dialog import UserDataBackupDialog
        dialog = UserDataBackupDialog(self.frame, self.app)
        dialog.show()
    
    def show_backup_manager(self):
        """Show backup manager"""
        from gui.widgets.dialogs import BackupManagerDialog
        dialog = BackupManagerDialog(self.frame, self.app)
        dialog.show()
    
    def update_backup_stats(self):
        """Update backup statistics"""
        try:
            from core.backup_manager import BackupManager
            backup_manager = BackupManager(self.adb)
            backups = backup_manager.list_backups()
            
            if backups:
                total_backups = len(backups)
                latest_backup = backups[0]
                
                stats_text = (
                    f"Total backups: {total_backups}\n"
                    f"Latest: {latest_backup['name']} ({latest_backup['size']})\n"
                    f"Created: {latest_backup['created']}"
                )
            else:
                stats_text = "No backups found"
            
            self.backup_stats_label.config(text=stats_text)
        except Exception as e:
            self.backup_stats_label.config(text="Error loading backup stats")

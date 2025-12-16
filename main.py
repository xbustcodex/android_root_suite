#!/usr/bin/env python3
"""
Ultimate ADB Root Tool v4.0 - GUI Edition
Refactored modular version
"""

import sys
import traceback
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import os
import time
import threading
from datetime import datetime

# Import refactored modules
from config.settings import config
from core.adb_manager import ADBManager, CommandResult
from core.device_manager import DeviceManager
from core.backup_manager import BackupManager
from gui.styles import StyleManager
from gui.widgets.dialogs.device_info_dialog import DeviceInfoDialog
from gui.widgets.dialogs.backup_dialog import BackupDialog
from gui.widgets.dialogs.patching_dialog import PatchingDialog
from gui.widgets.dialogs.adb_setup_dialog import ADBSetupDialog
from tools.samsung_tools import SamsungTools
from tools.xiaomi_tools import XiaomiTools
from tools.qualcomm_tools import QualcommTools
from tools.mediatek_tools import MediaTekTools

class ADBRootToolGUI:
    """Main GUI Application with all integrated functionality"""
    
    def __init__(self):
        self.config = config
        self.adb = ADBManager(config)
        self.device_mgr = DeviceManager(self.adb)
        self.backup_mgr = BackupManager(self.adb)
        self.style_manager = StyleManager()
        
        # Initialize dialog managers
        self.device_info_dialog = DeviceInfoDialog(self)
        self.backup_dialog = BackupDialog(self)
        self.patching_dialog = PatchingDialog(self)
        self.adb_setup_dialog = ADBSetupDialog(self)
        
        # Initialize tool managers
        self.samsung_tools = SamsungTools(self)
        self.xiaomi_tools = XiaomiTools(self)
        self.qualcomm_tools = QualcommTools(self)
        self.mediatek_tools = MediaTekTools(self)
        
        self.current_device = None
        self.logcat_running = False
        self.logcat_process = None
        
        self.setup_gui()
        self.check_initial_status()
    
    # ==================== GUI Setup Methods ====================
    
    def setup_gui(self):
        """Setup main GUI window"""
        self.root = tk.Tk()
        self.root.title("Ultimate ADB Root Tool v4.0 - GUI Edition")
        self.root.geometry("1000x700")
        self.root.configure(bg=self.style_manager.colors['bg'])
        
        self.setup_icon()
        self.create_main_container()
    
    def setup_icon(self):
        """Set window icon if available"""
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
    
    def create_main_container(self):
        """Create main container with all widgets"""
        # Title Frame
        self.create_title_frame()
        
        # Device Status Frame
        self.create_status_frame()
        
        # Main Content Notebook
        self.create_tabbed_interface()
        
        # Status Bar
        self.create_status_bar()
    
    def create_title_frame(self):
        """Create title frame"""
        title_frame = tk.Frame(self.root, bg=self.style_manager.colors['bg'])
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(
            title_frame,
            text="ULTIMATE ADB ROOT TOOL v4.0",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 16, 'bold')
        ).pack()
        
        tk.Label(
            title_frame,
            text="AndroidRootSuite - Complete GUI Edition",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['text'],
            font=('Arial', 10)
        ).pack()
    
    def create_status_frame(self):
        """Create device status frame"""
        status_frame = tk.LabelFrame(
            self.root,
            text="Device Status",
            bg=self.style_manager.colors['bg'],
            fg='white',
            padx=10,
            pady=10
        )
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.device_status_label = tk.Label(
            status_frame,
            text="No device connected",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['info'],
            font=('Arial', 9)
        )
        self.device_status_label.pack(side='left', padx=10)
        
        tk.Button(
            status_frame,
            text="Check Connection",
            command=self.check_device_connection,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
        
        tk.Button(
            status_frame,
            text="Get Device Info",
            command=self.show_device_info,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
    
    def create_tabbed_interface(self):
        """Create tabbed interface"""
        self.notebook = tk.ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create tabs
        self.create_main_tools_tab()
        self.create_backup_tools_tab()
        self.create_root_tools_tab()
        self.create_brand_tools_tab()
        self.create_advanced_tools_tab()
    
    def create_main_tools_tab(self):
        """Create main tools tab"""
        frame = tk.Frame(self.notebook, bg=self.style_manager.colors['bg'])
        self.notebook.add(frame, text="Main Tools")
        
        # Create scrollable frame
        canvas = tk.Canvas(frame, bg=self.style_manager.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style_manager.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Define tools
        tools = [
            ("ADB Setup & Device Check", self.show_adb_setup),
            ("Device Information Scan", self.show_device_info),
            ("COMPLETE BACKUP (ESSENTIAL)", self.start_complete_backup),
            ("Backup Boot Image Only", self.show_backup_boot),
            ("Patch Boot with Magisk/KernelSU", self.show_patch_boot),
            ("Flash Patched Boot/Recovery", self.show_flash_tools),
            ("Install Custom Recovery (TWRP)", self.show_install_recovery),
            ("Device-Specific Rooting Guide", self.show_root_guide),
            ("Advanced ADB Tools", self.show_advanced_tools),
            ("Install USB Drivers", self.show_driver_install),
        ]
        
        # Create tool buttons
        for text, command in tools:
            btn = tk.Button(
                scrollable_frame,
                text=text,
                command=command,
                bg=self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=10,
                width=40
            )
            btn.pack(fill='x', padx=20, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_backup_tools_tab(self):
        """Create backup tools tab"""
        frame = tk.Frame(self.notebook, bg=self.style_manager.colors['bg'])
        self.notebook.add(frame, text="Backup Tools")
        
        tk.Label(
            frame,
            text="Backup Management",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        # Backup folder info
        backup_folder = self.config.get_backup_folder()
        folder_label = tk.Label(
            frame,
            text=f"Current backup folder:\n{backup_folder}",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['text'],
            justify='center'
        )
        folder_label.pack(pady=10)
        
        # Backup buttons
        self.create_backup_buttons(frame)
        
        # Backup stats
        self.backup_stats_label = tk.Label(
            frame,
            text="",
            bg=self.style_manager.colors['bg'],
            fg='#888888'
        )
        self.backup_stats_label.pack(pady=10)
    
    def create_backup_buttons(self, parent):
        """Create backup operation buttons"""
        buttons = [
            ("Start Complete Backup", self.start_complete_backup, '#2e7d32'),
            ("Backup Boot Image", self.show_backup_boot, self.style_manager.colors['button_bg']),
            ("Backup Single App", self.backup_single_app, self.style_manager.colors['button_bg']),
            ("Backup User Data (Photos, Docs)", self.backup_user_data, self.style_manager.colors['button_bg']),
            ("View Backup Manager", self.show_backup_manager, self.style_manager.colors['button_bg']),
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=color,
                fg='white',
                relief='raised',
                padx=10,
                pady=5,
                width=40
            )
            btn.pack(pady=5, padx=50)
    
    def create_root_tools_tab(self):
        """Create rooting tools tab"""
        frame = tk.Frame(self.notebook, bg=self.style_manager.colors['bg'])
        self.notebook.add(frame, text="Root Tools")
        
        tk.Label(
            frame,
            text="Rooting Solutions",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        # Root method buttons
        methods = [
            ("Magisk (Recommended)", self.show_magisk_patch),
            ("KernelSU", self.show_kernelsu_info),
            ("APatch", self.show_apatch_info),
        ]
        
        for text, command in methods:
            btn = tk.Button(
                frame,
                text=text,
                command=command,
                bg=self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=5,
                width=30
            )
            btn.pack(pady=5, padx=50)
        
        # Separator
        tk.Frame(frame, height=2, bg='#444444').pack(fill='x', padx=20, pady=20)
        
        # Rooting guides
        tk.Label(
            frame,
            text="Rooting Guides",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['info'],
            font=('Arial', 11, 'bold')
        ).pack(pady=5)
        
        guides = [
            ("Samsung Root Guide", lambda: self.show_brand_guide('samsung')),
            ("Xiaomi Root Guide", lambda: self.show_brand_guide('xiaomi')),
            ("Google Pixel Guide", lambda: self.show_brand_guide('google')),
            ("OnePlus Guide", lambda: self.show_brand_guide('oneplus')),
            ("Generic Root Guide", self.show_generic_guide),
        ]
        
        for text, command in guides:
            btn = tk.Button(
                frame,
                text=text,
                command=command,
                bg=self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=2,
                width=25
            )
            btn.pack(pady=2, padx=30)
        
        # Warnings
        self.create_warning_section(frame)
    
    def create_warning_section(self, parent):
        """Create warning section"""
        warning_frame = tk.Frame(parent, bg=self.style_manager.colors['bg'], relief='sunken', borderwidth=1)
        warning_frame.pack(pady=20, padx=20, fill='x')
        
        tk.Label(
            warning_frame,
            text="⚠️ WARNING ⚠️",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['warning'],
            font=('Arial', 10, 'bold'),
            justify='center'
        ).pack(pady=5)
        
        warnings = [
            "• Voids warranty",
            "• Can brick device",
            "• Security risks",
            "• Breaks OTA updates",
            "• Banking apps may fail",
        ]
        
        for warning in warnings:
            tk.Label(
                warning_frame,
                text=warning,
                bg=self.style_manager.colors['bg'],
                fg=self.style_manager.colors['warning'],
                font=('Arial', 9)
            ).pack(anchor='w', padx=10)
    
    def create_brand_tools_tab(self):
        """Create brand-specific tools tab"""
        frame = tk.Frame(self.notebook, bg=self.style_manager.colors['bg'])
        self.notebook.add(frame, text="Brand Tools")
        
        tk.Label(
            frame,
            text="Brand-Specific Tools",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        # Brand buttons
        brands = [
            ("Samsung", "Samsung (Odin)", self.show_samsung_tools),
            ("Xiaomi", "Xiaomi (Mi Flash)", self.show_xiaomi_tools),
            ("Qualcomm", "Qualcomm (QFIL/QPST)", self.show_qualcomm_tools),
            ("MediaTek", "MediaTek (SP Flash)", self.show_mediatek_tools),
        ]
        
        for i, (icon, text, command) in enumerate(brands):
            btn_frame = tk.Frame(frame, bg=self.style_manager.colors['bg'])
            btn_frame.pack(pady=10, padx=50, fill='x')
            
            btn = tk.Button(
                btn_frame,
                text=text,
                command=command,
                bg=self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=5,
                width=40
            )
            btn.pack(fill='x')
            
            # Show available tools
            brand_dir = self.config.PATHS.get(icon.lower(), "")
            if os.path.exists(brand_dir):
                tool_count = len([f for f in os.listdir(brand_dir) if f.endswith(('.exe', '.zip', '.bin'))])
                tk.Label(
                    btn_frame,
                    text=f"Tools available: {tool_count}",
                    bg=self.style_manager.colors['bg'],
                    fg='#888888',
                    font=('Arial', 8)
                ).pack()
        
        # Drivers section
        tk.Frame(frame, height=2, bg='#444444').pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            frame,
            text="USB Drivers",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['info'],
            font=('Arial', 11, 'bold')
        ).pack(pady=5)
        
        driver_btn = tk.Button(
            frame,
            text="Install USB Drivers",
            command=self.show_driver_install,
            bg='#2e7d32',
            fg='white',
            relief='raised',
            padx=10,
            pady=5,
            width=40
        )
        driver_btn.pack(pady=10, padx=50)
    
    def create_advanced_tools_tab(self):
        """Create advanced tools tab"""
        frame = tk.Frame(self.notebook, bg=self.style_manager.colors['bg'])
        self.notebook.add(frame, text="Advanced Tools")
        
        # Create a grid of advanced tools
        tools_grid = [
            ("Screen Recording", self.screen_record),
            ("Screenshot", self.take_screenshot),
            ("Install APK", self.install_apk),
            ("Pull Files", self.pull_files),
            ("Push Files", self.push_files),
            ("ADB Shell", self.open_adb_shell),
            ("Reboot Options", self.show_reboot_menu),
            ("Remove Bloatware", self.remove_bloatware),
            ("View Logcat", self.view_logcat),
            ("Check Root", self.check_root),
            ("List Apps", self.list_apps),
            ("File Explorer", self.open_file_explorer),
        ]
        
        # Create 3x4 grid
        row, col = 0, 0
        for text, command in tools_grid:
            btn = tk.Button(
                frame,
                text=text,
                command=command,
                bg=self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=5,
                width=20
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)
        for i in range(4):
            frame.grid_rowconfigure(i, weight=1)
        
        # Terminal output area
        tk.Frame(frame, height=2, bg='#444444').grid(row=4, column=0, columnspan=3, sticky='ew', pady=20)
        
        tk.Label(
            frame,
            text="Terminal Output",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 10, 'bold')
        ).grid(row=5, column=0, columnspan=3, pady=5)
        
        self.terminal_text = scrolledtext.ScrolledText(
            frame,
            height=10,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        self.terminal_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        
        frame.grid_rowconfigure(6, weight=1)
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar_frame = tk.Frame(self.root, bg=self.style_manager.colors['bg'])
        status_bar_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.status_bar = tk.Label(
            status_bar_frame,
            text="Ready",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['info'],
            font=('Arial', 9)
        )
        self.status_bar.pack(side='left')
        
        # Progress Bar
        self.progress = tk.ttk.Progressbar(
            status_bar_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side='right', padx=10)
        
        # Version info
        tk.Label(
            status_bar_frame,
            text="v4.0 - Python GUI Edition",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['text'],
            font=('Arial', 9)
        ).pack(side='right', padx=20)
    
    # ==================== Core Application Methods ====================
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def show_warning(self, title: str, message: str):
        """Show warning message"""
        messagebox.showwarning(title, message)
    
    def show_error(self, title: str, message: str):
        """Show error message"""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """Show info message"""
        messagebox.showinfo(title, message)
    
    def show_yesno_dialog(self, title: str, message: str) -> bool:
        """Show yes/no dialog"""
        return messagebox.askyesno(title, message)
    
    def run_threaded(self, func, *args, **kwargs):
        """Run function in thread to avoid GUI freeze"""
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    
    def check_initial_status(self):
        """Check initial device status"""
        self.update_status("Initializing...")
        adb_ok, msg = self.adb.check_adb()
        if not adb_ok:
            self.show_warning("ADB not found", "Please install ADB or check configuration")
        self.check_device_connection()
    
    def check_device_connection(self):
        """Check device connection"""
        self.update_status("Checking device connection...")
        self.progress.start()
        
        def check():
            self.adb.start_adb_server()
            time.sleep(1)
            devices = self.adb.get_devices()
            
            self.root.after(0, self.update_device_status, devices)
            self.progress.stop()
        
        self.run_threaded(check)
    
    def update_device_status(self, devices):
        """Update device status label"""
        if devices:
            device_text = "\n".join([f"{d['serial']} - {d['status']}" for d in devices])
            self.device_status_label.config(
                text=f"Connected devices:\n{device_text}",
                fg=self.style_manager.colors['fg']
            )
            self.current_device = devices[0]['serial']
            self.update_status(f"{len(devices)} device(s) connected")
        else:
            self.device_status_label.config(
                text="No device connected\nEnable USB Debugging and connect device",
                fg=self.style_manager.colors['info']
            )
            self.current_device = None
            self.update_status("No devices detected")
    
    # ==================== Tool Methods ====================
    
    def show_adb_setup(self):
        """Show ADB setup window"""
        self.adb_setup_dialog.show()
    
    def show_device_info(self):
        """Show device information window"""
        self.device_info_dialog.show()
    
    def show_backup_boot(self):
        """Show backup boot image window"""
        self.backup_dialog.show_backup_boot()
    
    def show_patch_boot(self):
        """Show boot patching window"""
        self.patching_dialog.show()
    
    def show_magisk_patch(self):
        """Show Magisk patch instructions"""
        self.show_patch_boot()
    
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
            "Visit: https://kernelsu.org for more information\n\n"
            "Not all devices support KernelSU. Check compatibility first."
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
            "APK: APatch_11107_11107-release-signed.apk\n\n"
            "Features:\n"
            "- Similar to Magisk\n"
            "- Active development\n"
            "- Some Magisk modules compatible\n\n"
            "Note: Less tested than Magisk, use with caution."
        )
    
    def start_complete_backup(self):
        """Start complete device backup"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
            
        result = self.show_yesno_dialog(
            "Complete Backup",
            "This will create a complete backup including:\n\n"
            "1. Boot partition image\n"
            "2. App data backup (.ab file)\n"
            "3. Critical user data\n"
            "4. System information\n\n"
            "Make sure you have enough storage space.\n\n"
            "Continue?"
        )
        
        if not result:
            return
            
        self.update_status("Starting complete backup...")
        self.progress.start()
        
        def backup():
            backup_folder = self.config.get_backup_folder()
            os.makedirs(backup_folder, exist_ok=True)
            
            # Save device props
            props_file = os.path.join(backup_folder, "device_properties.txt")
            props = self.adb.get_device_props([
                'ro.product.manufacturer',
                'ro.product.model',
                'ro.build.version.release',
                'ro.build.id',
            ])
            
            with open(props_file, 'w') as f:
                for prop, value in props.items():
                    f.write(f"{prop}={value}\n")
            
            self.root.after(0, self.backup_complete, backup_folder)
            self.progress.stop()
            self.update_status("Backup completed")
            
        self.run_threaded(backup)
    
    def backup_complete(self, backup_folder):
        """Show backup completion message"""
        self.show_info(
            "Backup Complete",
            f"Backup completed successfully!\n\n"
            f"Location: {backup_folder}\n\n"
            f"Contents:\n"
            f"- device_properties.txt\n"
            f"- backup_summary.txt\n"
            f"\nMore files will be added as backup progresses."
        )
    
    def show_flash_tools(self):
        """Show flashing tools window"""
        window = tk.Toplevel(self.root)
        window.title("Flashing Tools")
        window.geometry("500x400")
        window.configure(bg=self.style_manager.colors['bg'])
        
        tk.Label(
            window,
            text="Select device chipset/brand:",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        # Brand buttons
        brands = [
            ("Samsung (Odin)", self.show_samsung_tools),
            ("Xiaomi (Mi Flash/Fastboot)", self.show_xiaomi_tools),
            ("Qualcomm (QFIL/EDL Mode)", self.show_qualcomm_tools),
            ("MediaTek (SP Flash Tool)", self.show_mediatek_tools),
            ("Generic (Fastboot)", self.show_generic_flash),
        ]
        
        for text, command in brands:
            btn = tk.Button(
                window,
                text=text,
                command=lambda cmd=command: (cmd(), window.destroy()),
                bg=self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=5,
                width=40
            )
            btn.pack(pady=5, padx=50)
        
        tk.Button(
            window,
            text="Cancel",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=20)
    
    def show_generic_flash(self):
        """Show generic fastboot flashing"""
        backup_folder = self.config.get_backup_folder()
        patched_boot = os.path.join(backup_folder, 'patchedboot.img')
        
        if not os.path.exists(patched_boot):
            self.show_warning("No Patched Boot", "No patchedboot.img found!\n\nCreate one using Patch Boot option first.")
            return
        
        result = self.show_yesno_dialog(
            "Flash Warning",
            f"WARNING: Flashing wrong boot image will brick device!\n\n"
            f"Ensure this is the correct image for your exact model.\n\n"
            f"File: {patched_boot}\n\n"
            f"Continue?"
        )
        
        if not result:
            return
        
        self.update_status("Flashing boot image...")
        self.progress.start()
        
        def flash():
            # Reboot to bootloader
            self.adb.reboot_device('bootloader')
            time.sleep(5)
            
            # Flash boot image
            result = self.adb.run_command([self.adb.fastboot_path, 'flash', 'boot', patched_boot])
            
            self.progress.stop()
            
            if result.success:
                self.root.after(0, lambda: self.show_info(
                    "Success",
                    "Boot image flashed successfully!\n\nDevice will reboot."
                ))
                self.adb.run_command([self.adb.fastboot_path, 'reboot'])
                self.update_status("Flash completed")
            else:
                self.root.after(0, lambda: self.show_error(
                    "Flash Failed",
                    f"Flash failed!\n\nError: {result.stderr}\n\nPossible issues:\n- Bootloader locked\n- Wrong boot image\n- Fastboot connection"
                ))
                self.adb.run_command([self.adb.fastboot_path, 'reboot'])
        
        self.run_threaded(flash)
    
    def show_install_recovery(self):
        """Show install recovery window"""
        window = tk.Toplevel(self.root)
        window.title("Install Custom Recovery")
        window.geometry("600x400")
        window.configure(bg=self.style_manager.colors['bg'])
        
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert('end', "TWRP (Team Win Recovery Project)\n")
        text_widget.insert('end', "=" * 50 + "\n\n")
        text_widget.insert('end', "Steps:\n\n")
        text_widget.insert('end', "1. Download TWRP for your specific device\n")
        text_widget.insert('end', "   - Visit: https://twrp.me\n")
        text_widget.insert('end', "   - Search by device codename\n\n")
        text_widget.insert('end', "2. Copy .img file to tools/recovery/\n\n")
        text_widget.insert('end', "3. Flash using fastboot:\n")
        text_widget.insert('end', "   - fastboot flash recovery twrp.img\n")
        text_widget.insert('end', "   - fastboot boot twrp.img (to test)\n\n")
        
        # Check for existing recovery images
        recovery_dir = os.path.join(self.config.PATHS['tools'], 'recovery')
        if os.path.exists(recovery_dir):
            recovery_files = [f for f in os.listdir(recovery_dir) if f.endswith('.img')]
            text_widget.insert('end', f"Current recovery images ({len(recovery_files)}):\n")
            for file in recovery_files:
                text_widget.insert('end', f"  - {file}\n")
        else:
            text_widget.insert('end', "No recovery directory found.\n")
        
        text_widget.config(state='disabled')
        
        tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def show_root_guide(self):
        """Show rooting guide window"""
        window = tk.Toplevel(self.root)
        window.title("Rooting Guide")
        window.geometry("800x600")
        window.configure(bg=self.style_manager.colors['bg'])
        
        # Create notebook for different guides
        notebook = tk.ttk.Notebook(window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Universal Guide
        universal_frame = tk.Frame(notebook, bg=self.style_manager.colors['bg'])
        notebook.add(universal_frame, text="Universal Guide")
        
        universal_text = scrolledtext.ScrolledText(
            universal_frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        universal_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        guide = """
===== UNIVERSAL ROOTING STEPS =====

1. ✅ RESEARCH your specific device
   - XDA Forum: https://forum.xda-developers.com
   - Search: "your_device_model root"

2. ✅ BACKUP device (ESSENTIAL)
   - Use Complete Backup option
   - Save backup to multiple locations

3. 🔓 UNLOCK bootloader (if possible)
   - Developer Options > OEM Unlocking
   - Fastboot: fastboot flashing unlock
   - WARNING: Wipes all data!

4. 📱 INSTALL custom recovery (optional)
   - TWRP for your device
   - Flash via fastboot

5. ⚙ PATCH boot image with Magisk
   - Extract boot.img from firmware
   - Patch with Magisk app
   - Save as patchedboot.img

6. 🔄 FLASH patched image
   - Fastboot: fastboot flash boot patchedboot.img
   - Samsung: Use Odin with patched AP file

7. 📲 INSTALL Magisk app
   - Manage root permissions
   - Install modules

===== RISKS & WARNINGS =====
⚠ VOIDS WARRANTY
⚠ CAN BRICK DEVICE
⚠ SECURITY VULNERABILITIES
⚠ BREAKS OTA UPDATES
⚠ BANKING APPS MAY NOT WORK
⚠ SAMSUNG PAY/SECURE FOLDER BREAKS
        """
        
        universal_text.insert('end', guide)
        universal_text.config(state='disabled')
        
        # Samsung Guide
        samsung_frame = tk.Frame(notebook, bg=self.style_manager.colors['bg'])
        notebook.add(samsung_frame, text="Samsung")
        
        samsung_text = scrolledtext.ScrolledText(
            samsung_frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        samsung_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        samsung_guide = """
===== SAMSUNG ROOTING GUIDE =====

1. BACKUP (ESSENTIAL) - Critical!
2. Enable OEM Unlock in Developer Options
3. Download firmware for your model
4. Extract AP_*.tar.md5
5. Patch with Magisk
6. Flash patched AP with Odin

⚠ WARNING: Trips Knox (voids warranty)
          Breaks Secure Folder, Samsung Pay
          Samsung Health may stop working

Tools needed:
- Odin3 (included in tools/samsung/)
- Magisk app
- Firmware for your exact model

Steps:
1. Enable Developer Options
2. Enable OEM Unlocking
3. Download firmware (SamMobile, Frija)
4. Extract AP file
5. Patch with Magisk
6. Flash with Odin
7. Boot and install Magisk app
        """
        
        samsung_text.insert('end', samsung_guide)
        samsung_text.config(state='disabled')
        
        # Xiaomi Guide
        xiaomi_frame = tk.Frame(notebook, bg=self.style_manager.colors['bg'])
        notebook.add(xiaomi_frame, text="Xiaomi")
        
        xiaomi_text = scrolledtext.ScrolledText(
            xiaomi_frame,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        xiaomi_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        xiaomi_guide = """
===== XIAOMI ROOTING GUIDE =====

1. Apply for bootloader unlock (7-15 day wait)
2. Use Mi Unlock Tool
3. Flash TWRP recovery (if available)
4. Install Magisk zip via recovery
5. OR patch boot image with Magisk

⚠ Note: May trigger Anti-Rollback (ARB)

Steps:
1. Bind account in MIUI settings
2. Wait 7-15 days
3. Use Mi Unlock Tool
4. Flash TWRP (fastboot flash recovery)
5. Boot to recovery
6. Flash Magisk.zip
7. Reboot and install Magisk app

WARNING: Unlocking wipes all data!
        """
        
        xiaomi_text.insert('end', xiaomi_guide)
        xiaomi_text.config(state='disabled')
        
        tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def show_advanced_tools(self):
        """Switch to advanced tools tab"""
        self.notebook.select(4)  # Advanced tools tab
    
    def show_driver_install(self):
        """Show driver installation window"""
        window = tk.Toplevel(self.root)
        window.title("Install USB Drivers")
        window.geometry("600x500")
        window.configure(bg=self.style_manager.colors['bg'])
        
        tk.Label(
            window,
            text="Select driver pack to install:",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        # Driver list
        drivers = [
            ("Universal ADB Driver", os.path.join(self.config.PATHS['driver_pack'], 'universal_adb_driver')),
            ("Google USB Driver", os.path.join(self.config.PATHS['driver_pack'], 'google_usb')),
            ("Samsung USB Driver", os.path.join(self.config.PATHS['driver_pack'], 'samsung_usb')),
            ("MediaTek Driver", os.path.join(self.config.PATHS['driver_pack'], 'mtk_drivers')),
            ("Qualcomm QDLoader", os.path.join(self.config.PATHS['driver_pack'], 'qualcomm_qdloader')),
            ("Xiaomi Driver", os.path.join(self.config.PATHS['tools'], 'miflash')),
        ]
        
        for name, path in drivers:
            frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
            frame.pack(fill='x', padx=20, pady=5)
            
            # Check if path exists
            exists = os.path.exists(path)
            
            btn = tk.Button(
                frame,
                text=name,
                command=lambda p=path: self.install_driver(p),
                bg='#2e7d32' if exists else self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=5
            )
            btn.pack(side='left', padx=5)
            
            status = "✓ Available" if exists else "✗ Not found"
            color = '#00ff00' if exists else '#ff9900'
            
            tk.Label(
                frame,
                text=status,
                bg=self.style_manager.colors['bg'],
                fg=color
            ).pack(side='right', padx=5)
        
        # Manual guide
        tk.Frame(window, height=2, bg='#444444').pack(fill='x', padx=20, pady=20)
        
        guide_btn = tk.Button(
            window,
            text="Manual Installation Guide",
            command=self.show_driver_guide,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        )
        guide_btn.pack(pady=10)
        
        tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def install_driver(self, driver_path):
        """Install USB driver"""
        if not os.path.exists(driver_path):
            self.show_warning("Driver Not Found", f"Driver path not found:\n{driver_path}")
            return
        
        # Look for installer files
        installers = []
        for root, dirs, files in os.walk(driver_path):
            for file in files:
                if file.endswith('.exe') or file.endswith('.msi'):
                    installers.append(os.path.join(root, file))
        
        if installers:
            try:
                os.startfile(installers[0])
                self.show_info("Installer Started", f"Starting {os.path.basename(installers[0])}\n\nFollow the installer instructions.")
            except Exception as e:
                self.show_error("Error", f"Failed to start installer:\n{e}")
        else:
            # Open folder for manual installation
            os.startfile(driver_path)
            self.show_info("Manual Installation", f"Driver folder opened.\n\nInstall via Device Manager:\n1. Open Device Manager\n2. Find unknown device\n3. Update driver\n4. Browse to this folder")
    
    def show_driver_guide(self):
        """Show driver installation guide"""
        window = tk.Toplevel(self.root)
        window.title("Driver Installation Guide")
        window.geometry("600x400")
        window.configure(bg=self.style_manager.colors['bg'])
        
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        guide = f"""
===== MANUAL DRIVER INSTALLATION =====

1. Open Device Manager:
   - Windows Key + X, then M
   - Or: Right-click Start button > Device Manager

2. Find unknown device:
   - Look for "Android", "ADB Interface", or unknown device
   - May be under "Other devices" or "Portable devices"

3. Right-click > Update driver

4. Select "Browse my computer for drivers"

5. Navigate to driver folder:
   - {self.config.PATHS['driver_pack']}

6. Select appropriate driver folder

7. Complete installation

===== COMMON ISSUES =====

Yellow exclamation mark: Driver not installed
- Update driver as above

Device not showing:
- Try different USB port
- Try different USB cable
- Restart computer and phone

"Unauthorized" in ADB:
- Check phone screen for "Allow USB debugging?" prompt
- Enable "Always allow from this computer"

Device shows as "MTP" or "File Transfer":
- Change USB mode to "File transfer" or "PTP"
- Some devices need PTP mode for ADB

Samsung devices:
- May need Samsung USB drivers specifically

Qualcomm EDL mode (9008):
- Needs Qualcomm QDLoader drivers
- Device shows as "QHSUSB_BULK" or "9008"
        """
        
        text_widget.insert('end', guide)
        text_widget.config(state='disabled')
        
        tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def show_samsung_tools(self):
        """Show Samsung tools window"""
        self.samsung_tools.show_tools()
    
    def show_xiaomi_tools(self):
        """Show Xiaomi tools window"""
        self.xiaomi_tools.show_tools()
    
    def show_qualcomm_tools(self):
        """Show Qualcomm tools warning"""
        self.qualcomm_tools.show_tools()
    
    def show_mediatek_tools(self):
        """Show MediaTek tools info"""
        self.mediatek_tools.show_tools()
    
    def show_backup_manager(self):
        """Show backup manager window"""
        window = tk.Toplevel(self.root)
        window.title("Backup Management")
        window.geometry("800x600")
        window.configure(bg=self.style_manager.colors['bg'])
        
        # List of backups
        backups_frame = tk.LabelFrame(
            window,
            text="Available Backups",
            bg=self.style_manager.colors['bg'],
            fg='white',
            padx=10,
            pady=10
        )
        backups_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for backups
        columns = ("Name", "Size", "Date", "Files")
        tree = tk.ttk.Treeview(backups_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        tree.heading("Name", text="Backup Name")
        tree.heading("Size", text="Size")
        tree.heading("Date", text="Date")
        tree.heading("Files", text="Files")
        
        tree.column("Name", width=250)
        tree.column("Size", width=100)
        tree.column("Date", width=150)
        tree.column("Files", width=100)
        
        # Add scrollbar
        scrollbar = tk.ttk.Scrollbar(backups_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate with backups
        backups = self.backup_mgr.get_backup_list()
        for backup in backups:
            tree.insert("", "end", values=(backup['name'], backup['size'], backup['date'], backup['files']), tags=(backup['name'],))
        
        # Buttons
        btn_frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        def open_selected():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                backup_name = item['values'][0]
                backup_path = os.path.join(self.config.PATHS['backup_root'], backup_name)
                if os.path.exists(backup_path):
                    os.startfile(backup_path)
        
        def delete_selected():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                backup_name = item['values'][0]
                
                result = self.show_yesno_dialog(
                    "Delete Backup",
                    f"Are you sure you want to delete backup:\n{backup_name}?\n\n"
                    "This action cannot be undone."
                )
                
                if result:
                    backup_path = os.path.join(self.config.PATHS['backup_root'], backup_name)
                    import shutil
                    try:
                        shutil.rmtree(backup_path)
                        tree.delete(selection[0])
                        self.show_info("Deleted", f"Backup deleted: {backup_name}")
                    except Exception as e:
                        self.show_error("Error", f"Failed to delete backup:\n{e}")
        
        tk.Button(
            btn_frame,
            text="Open Selected",
            command=open_selected,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Delete Selected",
            command=delete_selected,
            bg='#c62828',
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        def clean_backups():
            items = tree.get_children()
            if len(items) <= 5:
                self.show_info("Cleanup", "No old backups to clean (keeping last 5)")
                return
            
            result = self.show_yesno_dialog(
                "Clean Backups",
                f"This will keep only the last 5 backups and delete {len(items)-5} older ones.\n\n"
                "Continue?"
            )
            
            if not result:
                return
            
            # Get all backups sorted by date
            backups_list = []
            for item in items:
                values = tree.item(item)['values']
                backups_list.append((item, values[0], values[2]))  # item_id, name, date
            
            # Sort by date (newest first)
            backups_list.sort(key=lambda x: x[2], reverse=True)
            
            # Delete old ones
            deleted = 0
            for i, (item_id, backup_name, date) in enumerate(backups_list):
                if i >= 5:  # Keep only first 5 (newest)
                    backup_path = os.path.join(self.config.PATHS['backup_root'], backup_name)
                    try:
                        shutil.rmtree(backup_path)
                        tree.delete(item_id)
                        deleted += 1
                    except Exception as e:
                        print(f"Failed to delete {backup_name}: {e}")
            
            self.show_info("Cleanup Complete", f"Deleted {deleted} old backups.\nKept 5 most recent backups.")
        
        tk.Button(
            btn_frame,
            text="Clean Old Backups",
            command=clean_backups,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
    
    # ==================== Advanced Tools Implementations ====================
    
    def screen_record(self):
        """Start screen recording"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
            
        self.show_info(
            "Screen Recording",
            "Starting screen recording...\n\n"
            "To stop recording, press Ctrl+C on the device or disconnect USB.\n"
            "Recording will be saved to /sdcard/screenrecord.mp4"
        )
        
        # Run in background
        def record():
            self.adb.run_command([self.adb.adb_path, 'shell', 'screenrecord', '/sdcard/screenrecord.mp4'])
        
        self.run_threaded(record)
    
    def take_screenshot(self):
        """Take screenshot"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        self.update_status("Taking screenshot...")
        self.progress.start()
        
        def screenshot():
            file_path = self.device_mgr.take_screenshot()
            
            self.progress.stop()
            if file_path and os.path.exists(file_path):
                self.root.after(0, lambda: self.show_info(
                    "Screenshot Saved",
                    f"Screenshot saved to:\n{file_path}"
                ))
                self.update_status("Screenshot saved")
        
        self.run_threaded(screenshot)
    
    def install_apk(self):
        """Install APK file"""
        filename = filedialog.askopenfilename(
            title="Select APK to install",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        
        if filename:
            self.update_status(f"Installing {os.path.basename(filename)}...")
            self.progress.start()
            
            def install():
                success = self.device_mgr.install_apk(filename)
                
                self.progress.stop()
                
                if success:
                    self.root.after(0, lambda: self.show_info(
                        "Install Successful",
                        f"APK installed successfully:\n{os.path.basename(filename)}"
                    ))
                    self.update_status("APK installed")
                else:
                    self.root.after(0, lambda: self.show_error(
                        "Install Failed",
                        "Failed to install APK"
                    ))
            
            self.run_threaded(install)
    
    def pull_files(self):
        """Pull files from device"""
        window = tk.Toplevel(self.root)
        window.title("Pull Files from Device")
        window.geometry("500x300")
        window.configure(bg=self.style_manager.colors['bg'])
        
        tk.Label(
            window,
            text="Pull files from device to computer",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        # Source path
        tk.Label(
            window,
            text="Device path:",
            bg=self.style_manager.colors['bg'],
            fg='white'
        ).pack(anchor='w', padx=20)
        
        source_var = tk.StringVar(value="/sdcard/DCIM")
        source_entry = tk.Entry(window, textvariable=source_var, width=50)
        source_entry.pack(padx=20, pady=5, fill='x')
        
        # Destination path
        tk.Label(
            window,
            text="Computer folder:",
            bg=self.style_manager.colors['bg'],
            fg='white'
        ).pack(anchor='w', padx=20)
        
        dest_var = tk.StringVar(value=self.config.get_backup_folder())
        dest_entry = tk.Entry(window, textvariable=dest_var, width=50)
        dest_entry.pack(padx=20, pady=5, fill='x')
        
        def browse_dest():
            folder = filedialog.askdirectory(
                title="Select destination folder",
                initialdir=self.config.get_backup_folder()
            )
            if folder:
                dest_var.set(folder)
        
        tk.Button(
            window,
            text="Browse...",
            command=browse_dest,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=5)
        
        def start_pull():
            source = source_var.get()
            dest = dest_var.get()
            
            if not source or not dest:
                self.show_warning("Missing Path", "Please enter both source and destination paths")
                return
            
            self.update_status(f"Pulling files from {source}...")
            self.progress.start()
            
            def pull():
                result = self.adb.pull_file(source, dest)
                
                self.progress.stop()
                
                if result.success:
                    self.root.after(0, lambda: self.show_info(
                        "Pull Successful",
                        f"Files pulled successfully to:\n{dest}"
                    ))
                    self.update_status("Files pulled")
                else:
                    self.root.after(0, lambda: self.show_error(
                        "Pull Failed",
                        f"Failed to pull files:\n{result.stderr}"
                    ))
                
                window.destroy()
            
            self.run_threaded(pull)
        
        # Buttons
        btn_frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            btn_frame,
            text="Start Pull",
            command=start_pull,
            bg='#2e7d32',
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
    
    def push_files(self):
        """Push files to device"""
        window = tk.Toplevel(self.root)
        window.title("Push Files to Device")
        window.geometry("500x300")
        window.configure(bg=self.style_manager.colors['bg'])
        
        tk.Label(
            window,
            text="Push files from computer to device",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        # Source file
        tk.Label(
            window,
            text="Computer file:",
            bg=self.style_manager.colors['bg'],
            fg='white'
        ).pack(anchor='w', padx=20)
        
        source_var = tk.StringVar()
        
        def browse_source():
            filename = filedialog.askopenfilename(
                title="Select file to push"
            )
            if filename:
                source_var.set(filename)
        
        source_frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
        source_frame.pack(fill='x', padx=20, pady=5)
        
        source_entry = tk.Entry(source_frame, textvariable=source_var, width=40)
        source_entry.pack(side='left', padx=(0, 5))
        
        tk.Button(
            source_frame,
            text="Browse...",
            command=browse_source,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Destination path
        tk.Label(
            window,
            text="Device path:",
            bg=self.style_manager.colors['bg'],
            fg='white'
        ).pack(anchor='w', padx=20)
        
        dest_var = tk.StringVar(value="/sdcard/")
        dest_entry = tk.Entry(window, textvariable=dest_var, width=50)
        dest_entry.pack(padx=20, pady=5, fill='x')
        
        def start_push():
            source = source_var.get()
            dest = dest_var.get()
            
            if not source or not dest:
                self.show_warning("Missing Path", "Please select a file and destination")
                return
            
            if not os.path.exists(source):
                self.show_warning("File Not Found", f"File not found:\n{source}")
                return
            
            self.update_status(f"Pushing {os.path.basename(source)}...")
            self.progress.start()
            
            def push():
                result = self.adb.push_file(source, dest)
                
                self.progress.stop()
                
                if result.success:
                    self.root.after(0, lambda: self.show_info(
                        "Push Successful",
                        f"File pushed successfully to:\n{dest}"
                    ))
                    self.update_status("File pushed")
                else:
                    self.root.after(0, lambda: self.show_error(
                        "Push Failed",
                        f"Failed to push file:\n{result.stderr}"
                    ))
                
                window.destroy()
            
            self.run_threaded(push)
        
        # Buttons
        btn_frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            btn_frame,
            text="Start Push",
            command=start_push,
            bg='#2e7d32',
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
    
    def open_adb_shell(self):
        """Open ADB shell in new window"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        # For Windows, open command prompt with ADB
        import subprocess
        subprocess.Popen(['start', 'cmd', '/k', f'"{self.adb.adb_path}" shell'], shell=True)
    
    def show_reboot_menu(self):
        """Show reboot options menu"""
        window = tk.Toplevel(self.root)
        window.title("Reboot Options")
        window.geometry("300x250")
        window.configure(bg=self.style_manager.colors['bg'])
        
        tk.Label(
            window,
            text="Select reboot option:",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        options = [
            ("Reboot", "reboot"),
            ("Bootloader", "bootloader"),
            ("Recovery", "recovery"),
            ("Fastboot", "fastboot"),
            ("Soft Reboot", "soft"),
        ]
        
        for text, command in options:
            btn = tk.Button(
                window,
                text=text,
                command=lambda cmd=command: (self.adb.reboot_device(cmd), window.destroy()),
                bg=self.style_manager.colors['button_bg'],
                fg='white',
                relief='raised',
                padx=10,
                pady=5,
                width=20
            )
            btn.pack(pady=5, padx=50)
        
        tk.Button(
            window,
            text="Cancel",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def remove_bloatware(self):
        """Show bloatware removal window"""
        window = tk.Toplevel(self.root)
        window.title("Remove Bloatware")
        window.geometry("700x500")
        window.configure(bg=self.style_manager.colors['bg'])
        
        tk.Label(
            window,
            text="Warning: Can break system functionality!",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['warning'],
            font=('Arial', 10, 'bold')
        ).pack(pady=10)
        
        # Get package list
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.update_status("Getting package list...")
        self.progress.start()
        
        def get_packages():
            apps = self.device_mgr.get_installed_apps()
            
            self.progress.stop()
            
            if apps:
                # Filter for common bloatware
                bloat_keywords = ['facebook', 'test', 'demo', 'sample', 'carrier', 'bloat']
                bloat_packages = []
                
                for pkg in apps:
                    if any(keyword in pkg.lower() for keyword in bloat_keywords):
                        bloat_packages.append(pkg)
                
                self.root.after(0, lambda: self.display_bloatware(text_widget, bloat_packages))
            else:
                self.root.after(0, lambda: text_widget.insert('end', "Error getting package list"))
                text_widget.config(state='disabled')
        
        self.run_threaded(get_packages)
        
        # Package entry
        tk.Label(
            window,
            text="Package to disable:",
            bg=self.style_manager.colors['bg'],
            fg='white'
        ).pack(anchor='w', padx=20)
        
        pkg_var = tk.StringVar()
        pkg_entry = tk.Entry(window, textvariable=pkg_var, width=50)
        pkg_entry.pack(padx=20, pady=5, fill='x')
        
        def disable_package():
            pkg = pkg_var.get().strip()
            if pkg:
                self.adb.run_command([self.adb.adb_path, 'shell', 'pm', 'disable-user', '--user', '0', pkg])
                self.show_info("Disabled", f"Package disabled: {pkg}")
        
        tk.Button(
            window,
            text="Disable Package",
            command=disable_package,
            bg='#c62828',
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
        
        tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def display_bloatware(self, text_widget, packages):
        """Display bloatware packages in text widget"""
        text_widget.config(state='normal')
        text_widget.delete(1.0, 'end')
        
        if packages:
            text_widget.insert('end', f"Found {len(packages)} possible bloatware packages:\n\n")
            for pkg in packages:
                text_widget.insert('end', f"{pkg}\n")
        else:
            text_widget.insert('end', "No obvious bloatware packages found.\n")
            text_widget.insert('end', "Common bloatware keywords: facebook, test, demo, sample, carrier\n")
        
        text_widget.config(state='disabled')
        self.update_status("Package list loaded")
    
    def view_logcat(self):
        """View logcat output"""
        window = tk.Toplevel(self.root)
        window.title("Logcat Viewer")
        window.geometry("800x600")
        window.configure(bg=self.style_manager.colors['bg'])
        
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert('end', "Starting logcat...\n")
        text_widget.insert('end', "Press Stop to stop logging.\n\n")
        
        # Control variables
        self.logcat_running = True
        self.logcat_process = None
        
        def start_logcat():
            import subprocess
            self.logcat_process = subprocess.Popen(
                [self.adb.adb_path, 'logcat'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in background thread
            def read_output():
                while self.logcat_running and self.logcat_process:
                    line = self.logcat_process.stdout.readline()
                    if line:
                        window.after(0, text_widget.insert, 'end', line)
                        text_widget.see('end')
                    else:
                        break
            
            threading.Thread(target=read_output, daemon=True).start()
        
        def stop_logcat():
            self.logcat_running = False
            if self.logcat_process:
                self.logcat_process.terminate()
                self.logcat_process = None
            text_widget.insert('end', "\n\nLogcat stopped.\n")
        
        # Start logcat
        start_logcat()
        
        # Buttons
        btn_frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="Stop Logcat",
            command=stop_logcat,
            bg='#c62828',
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        def save_logcat():
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"logcat_{self.config.TIMESTAMP}.log"
            )
            
            if filename:
                content = text_widget.get(1.0, 'end')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.show_info("Saved", f"Logcat saved to:\n{filename}")
        
        tk.Button(
            btn_frame,
            text="Save Log",
            command=save_logcat,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Clear",
            command=lambda: text_widget.delete(1.0, 'end'),
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Close",
            command=lambda: (stop_logcat(), window.destroy()),
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
    
    def check_root(self):
        """Check root status"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        self.update_status("Checking root status...")
        self.progress.start()
        
        def check():
            status = self.device_mgr.check_root_status()
            
            self.progress.stop()
            
            if status['rooted']:
                message = f"[✓] ROOTED - {status['method']}\n"
                if status['version'] != 'Unknown':
                    message += f"Version: {status['version']}\n"
                self.root.after(0, lambda: self.show_info("Root Status", message))
            else:
                self.root.after(0, lambda: self.show_info("Root Status", "[✗] NOT ROOTED\n\nNo su binary found."))
            
            self.update_status("Root check completed")
        
        self.run_threaded(check)
    
    def list_apps(self):
        """List installed apps"""
        window = tk.Toplevel(self.root)
        window.title("Installed Apps")
        window.geometry("800x600")
        window.configure(bg=self.style_manager.colors['bg'])
        
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.update_status("Getting app list...")
        self.progress.start()
        
        def get_apps():
            apps = self.device_mgr.get_installed_apps()
            
            self.progress.stop()
            
            if apps:
                self.root.after(0, lambda: self.display_apps(text_widget, apps))
            else:
                self.root.after(0, lambda: text_widget.insert('end', "Error getting app list"))
                text_widget.config(state='disabled')
                self.update_status("Failed to get apps")
        
        self.run_threaded(get_apps)
        
        # Buttons
        btn_frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        def save_apps():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"apps_list_{self.config.TIMESTAMP}.txt"
            )
            
            if filename:
                content = text_widget.get(1.0, 'end')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.show_info("Saved", f"App list saved to:\n{filename}")
        
        tk.Button(
            btn_frame,
            text="Save List",
            command=save_apps,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
    
    def display_apps(self, text_widget, apps):
        """Display apps in text widget"""
        text_widget.config(state='normal')
        text_widget.delete(1.0, 'end')
        
        text_widget.insert('end', f"Found {len(apps)} installed apps:\n\n")
        
        for i, app in enumerate(apps[:100], 1):  # Show first 100
            text_widget.insert('end', f"{i:3}. {app}\n")
        
        if len(apps) > 100:
            text_widget.insert('end', f"\n... and {len(apps)-100} more apps.\n")
        
        text_widget.config(state='disabled')
        self.update_status(f"Found {len(apps)} apps")
    
    def backup_single_app(self):
        """Backup single app"""
        window = tk.Toplevel(self.root)
        window.title("Backup Single App")
        window.geometry("500x300")
        window.configure(bg=self.style_manager.colors['bg'])
        
        tk.Label(
            window,
            text="Backup single app with data",
            bg=self.style_manager.colors['bg'],
            fg=self.style_manager.colors['fg'],
            font=('Arial', 11, 'bold')
        ).pack(pady=10)
        
        # Package name
        tk.Label(
            window,
            text="Package name:",
            bg=self.style_manager.colors['bg'],
            fg='white'
        ).pack(anchor='w', padx=20)
        
        pkg_var = tk.StringVar()
        pkg_entry = tk.Entry(window, textvariable=pkg_var, width=50)
        pkg_entry.pack(padx=20, pady=5, fill='x')
        
        # Output file
        tk.Label(
            window,
            text="Output file:",
            bg=self.style_manager.colors['bg'],
            fg='white'
        ).pack(anchor='w', padx=20)
        
        output_var = tk.StringVar(value=os.path.join(self.config.get_backup_folder(), "app_backup.ab"))
        output_entry = tk.Entry(window, textvariable=output_var, width=50)
        output_entry.pack(padx=20, pady=5, fill='x')
        
        def browse_output():
            filename = filedialog.asksaveasfilename(
                defaultextension=".ab",
                filetypes=[("Android Backup", "*.ab"), ("All files", "*.*")],
                initialfile="app_backup.ab",
                initialdir=self.config.get_backup_folder()
            )
            if filename:
                output_var.set(filename)
        
        tk.Button(
            window,
            text="Browse...",
            command=browse_output,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=5)
        
        def start_backup():
            pkg = pkg_var.get().strip()
            output = output_var.get()
            
            if not pkg:
                self.show_warning("Missing Info", "Please enter package name")
                return
            
            self.show_info(
                "Backup Started",
                f"Starting backup for package: {pkg}\n\n"
                "Confirm backup on device screen when prompted.\n"
                "Leave password blank for no encryption."
            )
            
            self.update_status(f"Backing up {pkg}...")
            self.progress.start()
            
            def backup():
                success = self.backup_mgr.backup_single_app(pkg, output)
                
                self.progress.stop()
                
                if success:
                    file_size = os.path.getsize(output)
                    self.root.after(0, lambda: self.show_info(
                        "Backup Complete",
                        f"App backup created successfully!\n\n"
                        f"Package: {pkg}\n"
                        f"File: {output}\n"
                        f"Size: {file_size:,} bytes"
                    ))
                    self.update_status("App backup completed")
                else:
                    self.root.after(0, lambda: self.show_error(
                        "Backup Failed",
                        f"Failed to backup app.\n\n"
                        "Possible reasons:\n"
                        "- User cancelled on device\n"
                        "- App doesn't allow backup\n"
                        "- Insufficient storage"
                    ))
                    self.update_status("App backup failed")
                
                window.destroy()
            
            self.run_threaded(backup)
        
        # Buttons
        btn_frame = tk.Frame(window, bg=self.style_manager.colors['bg'])
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            btn_frame,
            text="Start Backup",
            command=start_backup,
            bg='#2e7d32',
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
    
    def backup_user_data(self):
        """Backup user data (photos, documents, etc.)"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        result = self.show_yesno_dialog(
            "Backup User Data",
            "This will backup user data including:\n\n"
            "- Photos/Videos (DCIM)\n"
            "- Downloads\n"
            "- Documents\n"
            "- WhatsApp (if exists)\n\n"
            "Continue?"
        )
        
        if not result:
            return
        
        self.update_status("Backing up user data...")
        self.progress.start()
        
        def backup():
            stats = self.backup_mgr.backup_user_data(self.config.get_backup_folder())
            
            self.progress.stop()
            
            summary = "\n".join([f"{name}: {count} files" for name, count in stats.items()])
            self.root.after(0, lambda: self.show_info(
                "Backup Complete",
                f"User data backed up successfully!\n\n"
                f"Summary:\n{summary}"
            ))
            self.update_status("User data backup completed")
        
        self.run_threaded(backup)
    
    def open_file_explorer(self):
        """Open file explorer on device"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        # Try to open file manager via ADB
        self.adb.run_command([self.adb.adb_path, 'shell', 'am', 'start', '-n', 'com.android.documentsui/.DocumentsActivity'])
        self.show_info("File Explorer", "Opening file explorer on device...")
    
    def show_brand_guide(self, brand):
        """Show brand-specific rooting guide"""
        if brand == 'samsung':
            self.show_samsung_guide()
        elif brand == 'xiaomi':
            self.show_xiaomi_guide()
        elif brand == 'google':
            self.show_google_guide()
        elif brand == 'oneplus':
            self.show_oneplus_guide()
        else:
            self.show_generic_guide()
    
    def show_samsung_guide(self):
        """Show Samsung rooting guide"""
        self.show_info(
            "Samsung Rooting Guide",
            """===== SAMSUNG ROOTING GUIDE =====

1. BACKUP (ESSENTIAL) - Critical!
   - Use Complete Backup option
   - Save backup to external storage

2. Enable OEM Unlock:
   - Settings > About Phone > Software Information
   - Tap "Build Number" 7 times
   - Back to Settings > Developer Options
   - Enable "OEM Unlocking"

3. Download firmware:
   - Use Frija tool or SamMobile
   - Download firmware for exact model (SM-XXXX)
   - Check region (CSC) matches your device

4. Extract AP_*.tar.md5 from firmware

5. Patch with Magisk:
   - Copy AP file to device
   - Install Magisk app
   - Select "Select and Patch a File"
   - Choose AP file
   - Copy patched file back to PC

6. Flash with Odin:
   - Enter Download Mode (Vol Down + Power + Home)
   - Open Odin as Administrator
   - Load patched AP in AP slot
   - Keep other slots empty or use original files
   - Click Start

7. First boot:
   - May take 10-15 minutes
   - Install Magisk app
   - Configure root permissions

⚠ WARNINGS:
- Trips Knox (voids warranty permanently)
- Breaks Secure Folder, Samsung Pay
- Samsung Health may stop working
- Some banking apps won't work
- Future OTA updates may fail"""
        )
    
    def show_xiaomi_guide(self):
        """Show Xiaomi rooting guide"""
        self.show_info(
            "Xiaomi Rooting Guide",
            """===== XIAOMI ROOTING GUIDE =====

1. Apply for bootloader unlock:
   - Settings > About Phone > tap MIUI version 7 times
   - Settings > Additional Settings > Developer Options
   - Enable "OEM unlocking" and "USB debugging"
   - Mi Unlock Status > Add account and device
   - Wait 7-15 days (168 hours minimum)

2. Unlock bootloader:
   - Download Mi Unlock Tool
   - Boot to fastboot (Vol Down + Power)
   - Connect to PC
   - Use Mi Unlock Tool to unlock
   - WARNING: Unlocking wipes all data!

3. Download firmware:
   - Get correct firmware for your device
   - Extract boot.img from payload.bin

4. Patch boot image with Magisk:
   - Copy boot.img to device
   - Install Magisk app
   - Patch boot image
   - Copy patched image back to PC

5. Flash patched boot:
   - Fastboot: fastboot flash boot magisk_patched.img
   - Or flash via custom recovery

⚠ WARNINGS:
- Anti-Rollback (ARB) protection
- Unlocking voids warranty in some regions
- Some features may break (Google Pay, banking)
- Weekly MIUI updates may break root"""
        )
    
    def show_google_guide(self):
        """Show Google Pixel rooting guide"""
        self.show_info(
            "Google Pixel Rooting Guide",
            """===== GOOGLE PIXEL ROOTING GUIDE =====

1. Enable OEM Unlocking:
   - Settings > About Phone > Build Number (tap 7 times)
   - Settings > Developer Options > OEM unlocking

2. Unlock bootloader:
   - adb reboot bootloader
   - fastboot flashing unlock
   - WARNING: Wipes all data!

3. Download factory image:
   - https://developers.google.com/android/images
   - Extract boot.img from archive

4. Patch with Magisk:
   - Copy boot.img to device
   - Install Magisk app
   - Patch boot image
   - Copy patched image to PC

5. Flash patched boot:
   - fastboot flash boot magisk_patched.img
   - fastboot reboot

6. Install Magisk app:
   - Manage root permissions
   - Install modules

✓ Easiest devices to root
✓ Regular security updates
✓ Good developer support"""
        )
    
    def show_oneplus_guide(self):
        """Show OnePlus rooting guide"""
        self.show_info(
            "OnePlus Rooting Guide",
            """===== ONEPLUS ROOTING GUIDE =====

1. Enable OEM Unlocking:
   - Settings > About Phone > Build Number (tap 7 times)
   - Settings > Developer Options > OEM unlocking

2. Unlock bootloader:
   - adb reboot bootloader
   - fastboot oem unlock
   - WARNING: Wipes all data!

3. Extract boot from payload.bin:
   - Download full OTA zip
   - Use payload_dumper tool
   - Extract boot.img

4. Patch with Magisk:
   - Copy boot.img to device
   - Install Magisk app
   - Patch boot image
   - Copy patched image to PC

5. Flash patched boot:
   - fastboot flash boot magisk_patched.img
   - fastboot reboot

WARNINGS:
- Voids warranty
- May break Widevine L1
- Banking apps may not work

OnePlus devices generally have good developer support."""
        )
    
    def show_generic_guide(self):
        """Show generic rooting guide"""
        window = tk.Toplevel(self.root)
        window.title("Generic Rooting Guide")
        window.geometry("700x500")
        window.configure(bg=self.style_manager.colors['bg'])
        
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Get device info if available
        device_info = ""
        if self.current_device:
            props = self.adb.get_device_props(['ro.product.manufacturer', 'ro.product.model'])
            if props:
                manufacturer = props.get('ro.product.manufacturer', 'Unknown')
                model = props.get('ro.product.model', 'Unknown')
                device_info = f"\nCurrent device: {manufacturer} {model}\n"
        
        guide = f"""===== GENERIC ROOTING GUIDE ====={device_info}

1. RESEARCH your specific device:
   - XDA Forum: https://forum.xda-developers.com
   - Search: "[Your Device Model] root"
   - Check device-specific forum
   - Read existing guides carefully

2. IDENTIFY your chipset:
   - Qualcomm (Snapdragon)
   - MediaTek (MTXXXX)
   - Exynos (Samsung)
   - Kirin (Huawei)
   - Unisoc/Spreadtrum

3. Common rooting methods:

   A. MAGISK (Most common):
      - Unlock bootloader
      - Extract boot.img from firmware
      - Patch with Magisk app
      - Flash patched boot

   B. TWRP + MAGISK:
      - Install custom recovery
      - Flash Magisk.zip
      - Works if TWRP available

   C. KERNEL-BASED:
      - KernelSU (if kernel supports)
      - APatch (Magisk alternative)
      - Requires compatible kernel

   D. MANUFACTURER-SPECIFIC:
      - Samsung: Odin + patched AP
      - Xiaomi: Mi Unlock + fastboot
      - Sony: Flashtool
      - LG: LGUP

4. IMPORTANT STEPS:
   - Backup everything first!
   - Unlock bootloader (if possible)
   - Use correct firmware for your model
   - Don't skip any steps in guides
   - Test with temporary boot first

⚠ WARNINGS:
- Always backup before modifying
- Use correct files for your exact model
- Read warnings in device-specific guides
- Rooting voids warranty
- Security risks exist"""
        
        text_widget.insert('end', guide)
        text_widget.config(state='disabled')
        
        tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg=self.style_manager.colors['button_bg'],
            fg='white',
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

# ============================================
# MAIN ENTRY POINT
# ============================================

def main():
    """Main entry point"""
    try:
        app = ADBRootToolGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

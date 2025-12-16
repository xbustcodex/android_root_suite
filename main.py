 #!/usr/bin/env python3
"""
Ultimate ADB Root Tool v4.0 - GUI Edition
Python + Tkinter Interface
Repository-ready structure
"""

import os
import sys
import subprocess
import threading
import time
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, font
import webbrowser

# ============================================
# CONFIGURATION
# ============================================

class Config:
    BASE_DIR = r"C:\AndroidRootSuite_skeleton"
    
    # Subdirectories
    SUBDIRS = {
        'backup_root': r"customer_backups",
        'boot_images': r"boot_images",
        'patched_boot': r"patched_boot",
        'magisk': r"magisk",
        'platform_tools': r"platform-tools",
        'scripts': r"scripts",
        'tools': r"tools",
        'driver_pack': r"driver_pack",
        'stock_firmware': r"stock_firmware",
        'samsung': r"samsung",
        'xiaomi': r"xiaomi",
        'qualcomm': r"qualcomm",
        'mtk': r"mtk",
        'scrcpy': r"scrcpy",
    }
    
    # Initialize full paths
    PATHS = {key: os.path.join(BASE_DIR, value) for key, value in SUBDIRS.items()}
    
    # Create timestamp
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @classmethod
    def get_backup_folder(cls):
        return os.path.join(cls.PATHS['backup_root'], f"newbackup_{cls.TIMESTAMP}")
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist"""
        for path in cls.PATHS.values():
            os.makedirs(path, exist_ok=True)
        os.makedirs(cls.get_backup_folder(), exist_ok=True)

# Setup directories
Config.setup_directories()

# ============================================
# ADB MANAGER
# ============================================

class ADBManager:
    def __init__(self):
        self.adb_path = os.path.join(Config.PATHS['platform_tools'], 'adb.exe')
        self.fastboot_path = os.path.join(Config.PATHS['platform_tools'], 'fastboot.exe')
        
    def run_command(self, cmd, wait=True, shell=False):
        """Run a command and return output"""
        try:
            if wait:
                result = subprocess.run(
                    cmd, 
                    shell=shell, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8',
                    errors='ignore'
                )
                return result.returncode, result.stdout, result.stderr
            else:
                subprocess.Popen(cmd, shell=shell)
                return 0, "", ""
        except Exception as e:
            return -1, "", str(e)
    
    def check_adb(self):
        """Check if ADB is available"""
        if os.path.exists(self.adb_path):
            return True, "ADB found"
        else:
            # Check universal drivers
            universal_adb = os.path.join(Config.PATHS['driver_pack'], 'universal_adb_driver', 'adb.exe')
            if os.path.exists(universal_adb):
                self.adb_path = universal_adb
                return True, "ADB found in universal drivers"
            return False, "ADB not found"
    
    def start_adb_server(self):
        """Start ADB server"""
        self.run_command([self.adb_path, 'kill-server'])
        time.sleep(1)
        return self.run_command([self.adb_path, 'start-server'])
    
    def get_devices(self):
        """Get list of connected devices"""
        code, out, err = self.run_command([self.adb_path, 'devices'])
        devices = []
        for line in out.strip().split('\n')[1:]:
            if line.strip():
                parts = line.split('\t')
                if len(parts) == 2:
                    devices.append({'serial': parts[0], 'status': parts[1]})
        return devices
    
    def get_device_props(self, prop_names):
        """Get device properties"""
        props = {}
        for prop in prop_names:
            code, out, err = self.run_command([self.adb_path, 'shell', 'getprop', prop])
            if code == 0 and out.strip():
                props[prop] = out.strip()
        return props

# ============================================
# GUI APPLICATION
# ============================================

class ADBRootToolGUI:
    def __init__(self):
        self.adb = ADBManager()
        self.current_device = None
        self.setup_gui()
        
    def setup_gui(self):
        """Setup main GUI window"""
        self.root = tk.Tk()
        self.root.title("Ultimate ADB Root Tool v4.0 - GUI Edition")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')
        
        # Set icon if available
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.setup_main_container()
        
        # Initialize
        self.check_initial_status()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        bg_color = '#1e1e1e'
        fg_color = '#00ff00'
        accent_color = '#007acc'
        button_bg = '#2d2d30'
        
        style.configure('Title.TLabel', 
                       background=bg_color, 
                       foreground=fg_color,
                       font=('Arial', 16, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=bg_color,
                       foreground='#cccccc',
                       font=('Arial', 10))
        
        style.configure('Status.TLabel',
                       background=bg_color,
                       foreground='#ff9900',
                       font=('Arial', 9))
        
        style.configure('Tool.TButton',
                       background=button_bg,
                       foreground='white',
                       borderwidth=1,
                       relief='raised',
                       padding=10)
        
        style.map('Tool.TButton',
                 background=[('active', '#3e3e42')])
        
        style.configure('Green.TButton',
                       background='#2e7d32',
                       foreground='white')
        
        style.configure('Red.TButton',
                       background='#c62828',
                       foreground='white')
        
        style.configure('Warning.TLabel',
                       background=bg_color,
                       foreground='#ff6b6b',
                       font=('Arial', 9, 'italic'))
        
        # Configure Notebook (Tab) style
        style.configure('Custom.TNotebook', background=bg_color)
        style.configure('Custom.TNotebook.Tab', 
                       background=button_bg,
                       foreground='white',
                       padding=[10, 5])
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', accent_color)])
        
    def setup_main_container(self):
        """Setup the main container with all widgets"""
        
        # Title Frame
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = ttk.Label(title_frame, 
                               text="ULTIMATE ADB ROOT TOOL v4.0",
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                  text="AndroidRootSuite - Complete GUI Edition",
                                  style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Device Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Device Status", padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.device_status_label = ttk.Label(status_frame, 
                                            text="No device connected",
                                            style='Status.TLabel')
        self.device_status_label.pack(side='left', padx=10)
        
        ttk.Button(status_frame, 
                  text="Check Connection", 
                  command=self.check_device_connection,
                  style='Tool.TButton').pack(side='right', padx=5)
        
        ttk.Button(status_frame,
                  text="Get Device Info",
                  command=self.show_device_info,
                  style='Tool.TButton').pack(side='right', padx=5)
        
        # Main Content Notebook
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create tabs
        self.create_main_tools_tab()
        self.create_backup_tools_tab()
        self.create_root_tools_tab()
        self.create_brand_tools_tab()
        self.create_advanced_tools_tab()
        
        # Status Bar
        status_bar_frame = ttk.Frame(self.root)
        status_bar_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.status_bar = ttk.Label(status_bar_frame, 
                                   text="Ready",
                                   style='Status.TLabel')
        self.status_bar.pack(side='left')
        
        # Progress Bar
        self.progress = ttk.Progressbar(status_bar_frame, 
                                       mode='indeterminate',
                                       length=200)
        self.progress.pack(side='right', padx=10)
        
        # Version info
        version_label = ttk.Label(status_bar_frame,
                                 text="v4.0 - Python GUI Edition",
                                 style='Subtitle.TLabel')
        version_label.pack(side='right', padx=20)
        
    def create_main_tools_tab(self):
        """Create main tools tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Main Tools")
        
        # Create a canvas with scrollbar for main tools
        canvas = tk.Canvas(frame, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
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
        for i, (text, command) in enumerate(tools):
            btn = ttk.Button(scrollable_frame,
                           text=text,
                           command=command,
                           style='Tool.TButton')
            btn.pack(fill='x', padx=20, pady=5, ipady=10)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_backup_tools_tab(self):
        """Create backup tools tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Backup Tools")
        
        ttk.Label(frame, 
                 text="Backup Management",
                 font=('Arial', 12, 'bold'),
                 background='#1e1e1e',
                 foreground='#00ff00').pack(pady=10)
        
        # Backup folder info
        backup_folder = Config.get_backup_folder()
        folder_label = ttk.Label(frame,
                                text=f"Current backup folder:\n{backup_folder}",
                                background='#1e1e1e',
                                foreground='#cccccc',
                                justify='center')
        folder_label.pack(pady=10)
        
        # Backup buttons
        ttk.Button(frame,
                  text="Start Complete Backup",
                  command=self.start_complete_backup,
                  style='Green.TButton').pack(pady=5, padx=50, fill='x')
        
        ttk.Button(frame,
                  text="Backup Boot Image",
                  command=self.show_backup_boot,
                  style='Tool.TButton').pack(pady=5, padx=50, fill='x')
        
        ttk.Button(frame,
                  text="Backup Single App",
                  command=self.backup_single_app,
                  style='Tool.TButton').pack(pady=5, padx=50, fill='x')
        
        ttk.Button(frame,
                  text="Backup User Data (Photos, Docs)",
                  command=self.backup_user_data,
                  style='Tool.TButton').pack(pady=5, padx=50, fill='x')
        
        ttk.Button(frame,
                  text="View Backup Manager",
                  command=self.show_backup_manager,
                  style='Tool.TButton').pack(pady=20, padx=50, fill='x')
        
        # Backup stats
        self.backup_stats_label = ttk.Label(frame,
                                           text="",
                                           background='#1e1e1e',
                                           foreground='#888888')
        self.backup_stats_label.pack(pady=10)
        
    def create_root_tools_tab(self):
        """Create rooting tools tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Root Tools")
        
        ttk.Label(frame,
                 text="Rooting Solutions",
                 font=('Arial', 12, 'bold'),
                 background='#1e1e1e',
                 foreground='#00ff00').pack(pady=10)
        
        # Root method buttons
        methods = [
            ("Magisk (Recommended)", self.show_magisk_patch),
            ("KernelSU", self.show_kernelsu_info),
            ("APatch", self.show_apatch_info),
        ]
        
        for text, command in methods:
            btn = ttk.Button(frame,
                           text=text,
                           command=command,
                           style='Tool.TButton')
            btn.pack(pady=5, padx=50, fill='x')
        
        # Separator
        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=20, pady=20)
        
        # Rooting guides
        ttk.Label(frame,
                 text="Rooting Guides",
                 font=('Arial', 11, 'bold'),
                 background='#1e1e1e',
                 foreground='#ff9900').pack(pady=5)
        
        guides = [
            ("Samsung Root Guide", lambda: self.show_brand_guide('samsung')),
            ("Xiaomi Root Guide", lambda: self.show_brand_guide('xiaomi')),
            ("Google Pixel Guide", lambda: self.show_brand_guide('google')),
            ("OnePlus Guide", lambda: self.show_brand_guide('oneplus')),
            ("Generic Root Guide", self.show_generic_guide),
        ]
        
        for text, command in guides:
            btn = ttk.Button(frame,
                           text=text,
                           command=command,
                           style='Tool.TButton')
            btn.pack(pady=2, padx=30, fill='x')
        
        # Warnings
        warning_frame = ttk.Frame(frame, relief='sunken', borderwidth=1)
        warning_frame.pack(pady=20, padx=20, fill='x')
        
        ttk.Label(warning_frame,
                 text="⚠️ WARNING ⚠️",
                 font=('Arial', 10, 'bold'),
                 background='#1e1e1e',
                 foreground='#ff6b6b',
                 justify='center').pack(pady=5)
        
        warnings = [
            "• Voids warranty",
            "• Can brick device",
            "• Security risks",
            "• Breaks OTA updates",
            "• Banking apps may fail",
        ]
        
        for warning in warnings:
            ttk.Label(warning_frame,
                     text=warning,
                     background='#1e1e1e',
                     foreground='#ff6b6b',
                     font=('Arial', 9)).pack(anchor='w', padx=10)
        
    def create_brand_tools_tab(self):
        """Create brand-specific tools tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Brand Tools")
        
        ttk.Label(frame,
                 text="Brand-Specific Tools",
                 font=('Arial', 12, 'bold'),
                 background='#1e1e1e',
                 foreground='#00ff00').pack(pady=10)
        
        # Brand buttons in a grid
        brands = [
            ("Samsung", "Samsung (Odin)", self.show_samsung_tools),
            ("Xiaomi", "Xiaomi (Mi Flash)", self.show_xiaomi_tools),
            ("Qualcomm", "Qualcomm (QFIL/QPST)", self.show_qualcomm_tools),
            ("MediaTek", "MediaTek (SP Flash)", self.show_mediatek_tools),
        ]
        
        for i, (icon, text, command) in enumerate(brands):
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(pady=10, padx=50, fill='x')
            
            btn = ttk.Button(btn_frame,
                           text=text,
                           command=command,
                           style='Tool.TButton')
            btn.pack(fill='x')
            
            # Show available tools
            brand_dir = Config.PATHS.get(icon.lower(), "")
            if os.path.exists(brand_dir):
                tool_count = len([f for f in os.listdir(brand_dir) if f.endswith(('.exe', '.zip', '.bin'))])
                ttk.Label(btn_frame,
                         text=f"Tools available: {tool_count}",
                         background='#1e1e1e',
                         foreground='#888888',
                         font=('Arial', 8)).pack()
        
        # Drivers section
        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=20, pady=20)
        
        ttk.Label(frame,
                 text="USB Drivers",
                 font=('Arial', 11, 'bold'),
                 background='#1e1e1e',
                 foreground='#ff9900').pack(pady=5)
        
        driver_btn = ttk.Button(frame,
                              text="Install USB Drivers",
                              command=self.show_driver_install,
                              style='Green.TButton')
        driver_btn.pack(pady=10, padx=50, fill='x')
        
    def create_advanced_tools_tab(self):
        """Create advanced tools tab"""
        frame = ttk.Frame(self.notebook)
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
            btn = ttk.Button(frame,
                           text=text,
                           command=command,
                           style='Tool.TButton')
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
        ttk.Separator(frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky='ew', pady=20)
        
        ttk.Label(frame,
                 text="Terminal Output",
                 font=('Arial', 10, 'bold'),
                 background='#1e1e1e',
                 foreground='#00ff00').grid(row=5, column=0, columnspan=3, pady=5)
        
        self.terminal_text = scrolledtext.ScrolledText(frame,
                                                      height=10,
                                                      bg='#0c0c0c',
                                                      fg='#00ff00',
                                                      font=('Consolas', 9))
        self.terminal_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        
        frame.grid_rowconfigure(6, weight=1)
        
    def check_initial_status(self):
        """Check initial device status"""
        self.update_status("Initializing...")
        adb_ok, msg = self.adb.check_adb()
        if not adb_ok:
            self.show_warning("ADB not found", "Please install ADB or check configuration")
        self.check_device_connection()
        
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
        
    def show_warning(self, title, message):
        """Show warning message"""
        messagebox.showwarning(title, message)
        
    def show_error(self, title, message):
        """Show error message"""
        messagebox.showerror(title, message)
        
    def show_info(self, title, message):
        """Show info message"""
        messagebox.showinfo(title, message)
        
    def run_threaded(self, func, *args):
        """Run function in thread to avoid GUI freeze"""
        thread = threading.Thread(target=func, args=args, daemon=True)
        thread.start()
        
    def check_device_connection(self):
        """Check device connection"""
        self.update_status("Checking device connection...")
        self.progress.start()
        
        def check():
            # Start ADB server
            self.adb.start_adb_server()
            time.sleep(1)
            
            # Get devices
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
                foreground='#00ff00'
            )
            self.current_device = devices[0]['serial']
            self.update_status(f"{len(devices)} device(s) connected")
        else:
            self.device_status_label.config(
                text="No device connected\nEnable USB Debugging and connect device",
                foreground='#ff9900'
            )
            self.current_device = None
            self.update_status("No devices detected")
    
    # ============================================
    # TOOL FUNCTIONS
    # ============================================
    
    def show_adb_setup(self):
        """Show ADB setup window"""
        window = tk.Toplevel(self.root)
        window.title("ADB Setup & Device Check")
        window.geometry("600x400")
        window.configure(bg='#1e1e1e')
        
        # Check ADB
        adb_ok, msg = self.adb.check_adb()
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert('end', f"ADB Status: {msg}\n\n")
        
        # Get devices
        devices = self.adb.get_devices()
        text_widget.insert('end', f"Connected Devices ({len(devices)}):\n")
        text_widget.insert('end', "-" * 40 + "\n")
        
        for device in devices:
            text_widget.insert('end', f"{device['serial']}\t{device['status']}\n")
        
        if not devices:
            text_widget.insert('end', "\nTroubleshooting Steps:\n")
            text_widget.insert('end', "1. Enable Developer Options\n")
            text_widget.insert('end', "2. Enable USB Debugging\n")
            text_widget.insert('end', "3. Install USB Drivers\n")
            text_widget.insert('end', "4. Try different USB cable/port\n")
            text_widget.insert('end', "5. Check phone for 'Allow USB debugging?' prompt\n")
        
        text_widget.config(state='disabled')
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame,
                  text="Check Again",
                  command=lambda: self.refresh_adb_info(text_widget)).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Close",
                  command=window.destroy).pack(side='right', padx=5)
        
    def refresh_adb_info(self, text_widget):
        """Refresh ADB info in the setup window"""
        text_widget.config(state='normal')
        text_widget.delete(1.0, 'end')
        
        adb_ok, msg = self.adb.check_adb()
        text_widget.insert('end', f"ADB Status: {msg}\n\n")
        
        devices = self.adb.get_devices()
        text_widget.insert('end', f"Connected Devices ({len(devices)}):\n")
        text_widget.insert('end', "-" * 40 + "\n")
        
        for device in devices:
            text_widget.insert('end', f"{device['serial']}\t{device['status']}\n")
        
        text_widget.config(state='disabled')
        
    def show_device_info(self):
        """Show device information window"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
            
        window = tk.Toplevel(self.root)
        window.title("Device Information")
        window.geometry("700x600")
        window.configure(bg='#1e1e1e')
        
        # Create notebook for different info sections
        notebook = ttk.Notebook(window, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Basic Info Tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        
        # Get device properties
        props_to_get = [
            'ro.product.manufacturer',
            'ro.product.model',
            'ro.product.brand',
            'ro.product.device',
            'ro.build.version.release',
            'ro.build.version.sdk',
            'ro.bootloader',
            'ro.build.version.security_patch',
            'ro.hardware',
        ]
        
        props = self.adb.get_device_props(props_to_get)
        
        text_widget = scrolledtext.ScrolledText(basic_frame,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        for prop, value in props.items():
            prop_name = prop.replace('ro.', '').replace('.', ' ')
            text_widget.insert('end', f"{prop_name.title()}: {value}\n")
        
        text_widget.config(state='disabled')
        
        # Advanced Info Tab
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Advanced")
        
        adv_text = scrolledtext.ScrolledText(advanced_frame,
                                            bg='#0c0c0c',
                                            fg='#00ff00',
                                            font=('Consolas', 9))
        adv_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Get more props
        more_props = [
            'ro.build.fingerprint',
            'ro.build.type',
            'ro.build.tags',
            'ro.build.user',
            'ro.build.id',
            'ro.product.name',
        ]
        
        more_props_data = self.adb.get_device_props(more_props)
        
        for prop, value in more_props_data.items():
            prop_name = prop.replace('ro.', '').replace('.', ' ')
            adv_text.insert('end', f"{prop_name}: {value}\n")
        
        adv_text.config(state='disabled')
        
        # Root Check Tab
        root_frame = ttk.Frame(notebook)
        notebook.add(root_frame, text="Root Status")
        
        root_text = scrolledtext.ScrolledText(root_frame,
                                             bg='#0c0c0c',
                                             fg='#00ff00',
                                             font=('Consolas', 10))
        root_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Check root
        code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', 'which', 'su'])
        if code == 0 and out.strip():
            root_text.insert('end', "[✓] ROOTED - su binary found\n")
            
            # Check for Magisk
            code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', 'su -c "magisk -v"'])
            if code == 0:
                root_text.insert('end', f"Root Method: Magisk {out.strip()}\n")
            
            # Check for KernelSU
            code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', 'su -c "ksud"'])
            if code == 0:
                root_text.insert('end', "Root Method: KernelSU\n")
        else:
            root_text.insert('end', "[✗] NOT ROOTED\n")
        
        root_text.config(state='disabled')
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame,
                  text="Save to File",
                  command=lambda: self.save_device_info(props)).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Close",
                  command=window.destroy).pack(side='right', padx=5)
        
    def save_device_info(self, props):
        """Save device info to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"device_info_{Config.TIMESTAMP}.txt"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Device Information\n")
                f.write("=" * 50 + "\n\n")
                for prop, value in props.items():
                    prop_name = prop.replace('ro.', '').replace('.', ' ')
                    f.write(f"{prop_name.title()}: {value}\n")
            
            self.show_info("Saved", f"Device information saved to:\n{filename}")
    
    def start_complete_backup(self):
        """Start complete device backup"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
            
        result = messagebox.askyesno(
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
            backup_folder = Config.get_backup_folder()
            os.makedirs(backup_folder, exist_ok=True)
            
            # Create backup summary
            summary_file = os.path.join(backup_folder, "backup_summary.txt")
            with open(summary_file, 'w') as f:
                f.write(f"Complete Backup - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
            
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
        messagebox.showinfo(
            "Backup Complete",
            f"Backup completed successfully!\n\n"
            f"Location: {backup_folder}\n\n"
            f"Contents:\n"
            f"- device_properties.txt\n"
            f"- backup_summary.txt\n"
            f"\nMore files will be added as backup progresses."
        )
        
    def show_backup_boot(self):
        """Show backup boot image window"""
        window = tk.Toplevel(self.root)
        window.title("Backup Boot Image")
        window.geometry("500x400")
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Select backup method:",
                 background='#1e1e1e',
                 foreground='#00ff00',
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Method selection
        method_var = tk.StringVar(value="adb")
        
        methods = [
            ("Via ADB (requires root)", "adb"),
            ("Via Fastboot (unlocked bootloader)", "fastboot"),
            ("Extract from firmware file", "extract"),
        ]
        
        for text, value in methods:
            rb = ttk.Radiobutton(window,
                                text=text,
                                variable=method_var,
                                value=value,
                                style='Tool.TButton')
            rb.pack(pady=5, padx=20, anchor='w')
        
        # Info text
        info_text = scrolledtext.ScrolledText(window,
                                             height=10,
                                             bg='#0c0c0c',
                                             fg='#cccccc',
                                             font=('Arial', 9))
        info_text.pack(padx=20, pady=10, fill='x')
        info_text.insert('end', "ADB method:\n- Requires rooted device\n- Dumps boot partition directly\n- Saves as ogboot.img")
        info_text.config(state='disabled')
        
        def update_info(*args):
            info_text.config(state='normal')
            info_text.delete(1.0, 'end')
            
            if method_var.get() == "adb":
                info_text.insert('end', "ADB method:\n- Requires rooted device\n- Dumps boot partition directly\n- Saves as ogboot.img")
            elif method_var.get() == "fastboot":
                info_text.insert('end', "Fastboot method:\n- Requires unlocked bootloader\n- Need to extract from firmware\n- Manual process")
            else:
                info_text.insert('end', f"Extract from firmware:\n- Place firmware in: {Config.PATHS['stock_firmware']}\n- Use extractor tool\n- Copy to: {Config.PATHS['boot_images']}")
            
            info_text.config(state='disabled')
        
        method_var.trace('w', update_info)
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        def start_backup():
            method = method_var.get()
            if method == "adb":
                self.backup_boot_adb()
            elif method == "fastboot":
                self.show_info("Fastboot Backup", "Reboot to bootloader and use:\n\nfastboot getvar all\nfastboot flash boot boot.img")
            else:
                if os.path.exists(Config.PATHS['stock_firmware']):
                    os.startfile(Config.PATHS['stock_firmware'])
                self.show_info("Extract Firmware", f"Place firmware files in:\n{Config.PATHS['stock_firmware']}\n\nThen extract boot.img using appropriate tool.")
            
            window.destroy()
        
        ttk.Button(btn_frame,
                  text="Start Backup",
                  command=start_backup,
                  style='Green.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Cancel",
                  command=window.destroy).pack(side='right', padx=5)
        
    def backup_boot_adb(self):
        """Backup boot image via ADB"""
        self.update_status("Backing up boot image...")
        self.progress.start()
        
        def backup():
            backup_folder = Config.get_backup_folder()
            
            # Try common boot partition locations
            partitions = [
                "/dev/block/bootdevice/by-name/boot",
                "/dev/block/bootdevice/by-name/boot_a",
                "/dev/block/bootdevice/by-name/boot_b",
                "/dev/block/bootdevice/by-name/kernel",
                "/dev/block/bootdevice/by-name/bootimg",
            ]
            
            success = False
            
            for part in partitions:
                cmd = f'su -c "dd if={part} of=/sdcard/boot_backup.img bs=4096 count=32768"'
                code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', cmd])
                
                if code == 0:
                    # Pull the file
                    self.adb.run_command([self.adb.adb_path, 'pull', '/sdcard/boot_backup.img', 
                                         os.path.join(backup_folder, 'ogboot.img')])
                    
                    # Clean up
                    self.adb.run_command([self.adb.adb_path, 'shell', 'rm', '/sdcard/boot_backup.img'])
                    success = True
                    break
            
            self.progress.stop()
            
            if success:
                self.root.after(0, lambda: self.show_info(
                    "Success", 
                    f"Boot image backed up successfully!\n\nSaved to: {os.path.join(backup_folder, 'ogboot.img')}"
                ))
                self.update_status("Boot backup completed")
            else:
                self.root.after(0, lambda: self.show_warning(
                    "Failed",
                    "Could not backup boot image.\n\nPossible reasons:\n"
                    "- Device not rooted\n"
                    "- Different partition naming\n"
                    "- Insufficient permissions\n\n"
                    "Try extracting from firmware instead."
                ))
        
        self.run_threaded(backup)
        
    def show_patch_boot(self):
        """Show boot patching window"""
        window = tk.Toplevel(self.root)
        window.title("Patch Boot Image")
        window.geometry("700x500")
        window.configure(bg='#1e1e1e')
        
        # Create notebook for different methods
        notebook = ttk.Notebook(window, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Magisk Tab
        magisk_frame = ttk.Frame(notebook)
        notebook.add(magisk_frame, text="Magisk")
        
        magisk_text = scrolledtext.ScrolledText(magisk_frame,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        magisk_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        magisk_text.insert('end', "Magisk v29.0 - Recommended for most devices\n")
        magisk_text.insert('end', "=" * 50 + "\n\n")
        magisk_text.insert('end', "Steps to patch boot image:\n\n")
        magisk_text.insert('end', "1. Copy boot.img to device: /sdcard/boot.img\n")
        magisk_text.insert('end', "2. Install Magisk app\n")
        magisk_text.insert('end', "3. Open Magisk app\n")
        magisk_text.insert('end', "4. Tap Install > Select and Patch a File\n")
        magisk_text.insert('end', "5. Choose /sdcard/boot.img\n")
        magisk_text.insert('end', "6. Copy patched file from /sdcard/ to PC\n")
        magisk_text.insert('end', "7. Save as patchedboot.img in backup folder\n")
        magisk_text.config(state='disabled')
        
        # Browse button
        def browse_boot_img():
            filename = filedialog.askopenfilename(
                title="Select boot.img",
                filetypes=[("Boot images", "*.img"), ("All files", "*.*")]
            )
            if filename:
                self.adb.run_command([self.adb.adb_path, 'push', filename, '/sdcard/boot.img'])
                self.show_info("Success", "boot.img copied to device\n\nNow install Magisk app and patch the file.")
        
        ttk.Button(magisk_frame,
                  text="Browse for boot.img",
                  command=browse_boot_img).pack(pady=10)
        
        # KernelSU Tab
        kernelsu_frame = ttk.Frame(notebook)
        notebook.add(kernelsu_frame, text="KernelSU")
        
        kernelsu_text = scrolledtext.ScrolledText(kernelsu_frame,
                                                 bg='#0c0c0c',
                                                 fg='#00ff00',
                                                 font=('Consolas', 10))
        kernelsu_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        kernelsu_text.insert('end', "KernelSU - Kernel-based root solution\n")
        kernelsu_text.insert('end', "=" * 50 + "\n\n")
        kernelsu_text.insert('end', "KernelSU requires:\n\n")
        kernelsu_text.insert('end', "1. Kernel with KernelSU support built-in\n")
        kernelsu_text.insert('end', "2. Or patching kernel source and recompiling\n")
        kernelsu_text.insert('end', "3. For GKI devices, use KernelSU kernel patches\n\n")
        kernelsu_text.insert('end', "APK: KernelSU_v3.0.0_32179-release.apk\n\n")
        kernelsu_text.insert('end', "Visit: https://kernelsu.org for more info\n")
        kernelsu_text.config(state='disabled')
        
        # APatch Tab
        apatch_frame = ttk.Frame(notebook)
        notebook.add(apatch_frame, text="APatch")
        
        apatch_text = scrolledtext.ScrolledText(apatch_frame,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        apatch_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        apatch_text.insert('end', "APatch - Alternative to Magisk\n")
        apatch_text.insert('end', "=" * 50 + "\n\n")
        apatch_text.insert('end', "APatch works similar to Magisk:\n\n")
        apatch_text.insert('end', "1. Install APatch app\n")
        apatch_text.insert('end', "2. Patch boot image\n")
        apatch_text.insert('end', "3. Flash patched image\n\n")
        apatch_text.insert('end', "APK: APatch_11107_11107-release-signed.apk\n")
        apatch_text.config(state='disabled')
        
        # Close button
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def show_flash_tools(self):
        """Show flashing tools window"""
        window = tk.Toplevel(self.root)
        window.title("Flashing Tools")
        window.geometry("500x400")
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Select device chipset/brand:",
                 background='#1e1e1e',
                 foreground='#00ff00',
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Brand buttons
        brands = [
            ("Samsung (Odin)", self.show_samsung_tools),
            ("Xiaomi (Mi Flash/Fastboot)", self.show_xiaomi_tools),
            ("Qualcomm (QFIL/EDL Mode)", self.show_qualcomm_tools),
            ("MediaTek (SP Flash Tool)", self.show_mediatek_tools),
            ("Generic (Fastboot)", self.show_generic_flash),
        ]
        
        for text, command in brands:
            btn = ttk.Button(window,
                           text=text,
                           command=lambda cmd=command: (cmd(), window.destroy()),
                           style='Tool.TButton')
            btn.pack(pady=5, padx=50, fill='x')
        
        ttk.Button(window,
                  text="Cancel",
                  command=window.destroy).pack(pady=20)
        
    def show_generic_flash(self):
        """Show generic fastboot flashing"""
        backup_folder = Config.get_backup_folder()
        patched_boot = os.path.join(backup_folder, 'patchedboot.img')
        
        if not os.path.exists(patched_boot):
            self.show_warning("No Patched Boot", "No patchedboot.img found!\n\nCreate one using Patch Boot option first.")
            return
        
        result = messagebox.askyesno(
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
            self.adb.run_command([self.adb.adb_path, 'reboot', 'bootloader'])
            time.sleep(5)
            
            # Flash boot image
            code, out, err = self.adb.run_command([self.adb.fastboot_path, 'flash', 'boot', patched_boot])
            
            self.progress.stop()
            
            if code == 0:
                self.root.after(0, lambda: self.show_info(
                    "Success",
                    "Boot image flashed successfully!\n\nDevice will reboot."
                ))
                self.adb.run_command([self.adb.fastboot_path, 'reboot'])
                self.update_status("Flash completed")
            else:
                self.root.after(0, lambda: self.show_error(
                    "Flash Failed",
                    f"Flash failed!\n\nError: {err}\n\nPossible issues:\n- Bootloader locked\n- Wrong boot image\n- Fastboot connection"
                ))
                self.adb.run_command([self.adb.fastboot_path, 'reboot'])
        
        self.run_threaded(flash)
        
    def show_install_recovery(self):
        """Show install recovery window"""
        window = tk.Toplevel(self.root)
        window.title("Install Custom Recovery")
        window.geometry("600x400")
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
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
        recovery_dir = os.path.join(Config.PATHS['tools'], 'recovery')
        if os.path.exists(recovery_dir):
            recovery_files = [f for f in os.listdir(recovery_dir) if f.endswith('.img')]
            text_widget.insert('end', f"Current recovery images ({len(recovery_files)}):\n")
            for file in recovery_files:
                text_widget.insert('end', f"  - {file}\n")
        else:
            text_widget.insert('end', "No recovery directory found.\n")
        
        text_widget.config(state='disabled')
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def show_root_guide(self):
        """Show rooting guide window"""
        window = tk.Toplevel(self.root)
        window.title("Rooting Guide")
        window.geometry("800x600")
        window.configure(bg='#1e1e1e')
        
        # Create notebook for different guides
        notebook = ttk.Notebook(window, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Universal Guide
        universal_frame = ttk.Frame(notebook)
        notebook.add(universal_frame, text="Universal Guide")
        
        universal_text = scrolledtext.ScrolledText(universal_frame,
                                                  bg='#0c0c0c',
                                                  fg='#00ff00',
                                                  font=('Consolas', 10))
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
        samsung_frame = ttk.Frame(notebook)
        notebook.add(samsung_frame, text="Samsung")
        
        samsung_text = scrolledtext.ScrolledText(samsung_frame,
                                                bg='#0c0c0c',
                                                fg='#00ff00',
                                                font=('Consolas', 10))
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
        xiaomi_frame = ttk.Frame(notebook)
        notebook.add(xiaomi_frame, text="Xiaomi")
        
        xiaomi_text = scrolledtext.ScrolledText(xiaomi_frame,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
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
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def show_advanced_tools(self):
        """Switch to advanced tools tab"""
        self.notebook.select(4)  # Advanced tools tab
        
    def show_driver_install(self):
        """Show driver installation window"""
        window = tk.Toplevel(self.root)
        window.title("Install USB Drivers")
        window.geometry("600x500")
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Select driver pack to install:",
                 background='#1e1e1e',
                 foreground='#00ff00',
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Driver list
        drivers = [
            ("Universal ADB Driver", os.path.join(Config.PATHS['driver_pack'], 'universal_adb_driver')),
            ("Google USB Driver", os.path.join(Config.PATHS['driver_pack'], 'google_usb')),
            ("Samsung USB Driver", os.path.join(Config.PATHS['driver_pack'], 'samsung_usb')),
            ("MediaTek Driver", os.path.join(Config.PATHS['driver_pack'], 'mtk_drivers')),
            ("Qualcomm QDLoader", os.path.join(Config.PATHS['driver_pack'], 'qualcomm_qdloader')),
            ("Xiaomi Driver", os.path.join(Config.PATHS['tools'], 'miflash')),
        ]
        
        for name, path in drivers:
            frame = ttk.Frame(window)
            frame.pack(fill='x', padx=20, pady=5)
            
            # Check if path exists
            exists = os.path.exists(path)
            
            btn = ttk.Button(frame,
                           text=name,
                           command=lambda p=path: self.install_driver(p),
                           style='Green.TButton' if exists else 'Tool.TButton')
            btn.pack(side='left', padx=5)
            
            status = "✓ Available" if exists else "✗ Not found"
            color = '#00ff00' if exists else '#ff9900'
            
            ttk.Label(frame,
                     text=status,
                     background='#1e1e1e',
                     foreground=color).pack(side='right', padx=5)
        
        # Manual guide
        ttk.Separator(window, orient='horizontal').pack(fill='x', padx=20, pady=20)
        
        guide_btn = ttk.Button(window,
                              text="Manual Installation Guide",
                              command=self.show_driver_guide,
                              style='Tool.TButton')
        guide_btn.pack(pady=10)
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
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
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        guide = """
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
   - {driver_path}

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
        """.format(driver_path=Config.PATHS['driver_pack'])
        
        text_widget.insert('end', guide)
        text_widget.config(state='disabled')
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def show_samsung_tools(self):
        """Show Samsung tools window"""
        window = tk.Toplevel(self.root)
        window.title("Samsung Tools")
        window.geometry("700x500")
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Find Odin versions
        odin_dir = os.path.join(Config.PATHS['tools'], 'odin')
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
        
        text_widget.insert('end', "INSTRUCTIONS:\n\n")
        text_widget.insert('end', "1. Enter Download Mode:\n")
        text_widget.insert('end', "   - Power off device\n")
        text_widget.insert('end', "   - Hold Vol Down + Power + Home\n")
        text_widget.insert('end', "   - Release when warning appears\n")
        text_widget.insert('end', "   - Press Vol Up to continue\n\n")
        
        text_widget.insert('end', "2. Connect USB cable\n\n")
        
        text_widget.insert('end', "3. Open Odin3.exe as Administrator\n\n")
        
        text_widget.insert('end', "4. Load firmware files:\n")
        text_widget.insert('end', "   - AP: System, boot, recovery\n")
        text_widget.insert('end', "   - BL: Bootloader\n")
        text_widget.insert('end', "   - CP: Modem/Radio\n")
        text_widget.insert('end', "   - CSC: Carrier/Region\n\n")
        
        text_widget.insert('end', "5. Important settings:\n")
        text_widget.insert('end', "   - Auto Reboot: ✓\n")
        text_widget.insert('end', "   - F. Reset Time: ✓\n")
        text_widget.insert('end', "   - Re-Partition: ✗ (unless instructed)\n\n")
        
        text_widget.insert('end', "6. Click Start\n\n")
        
        text_widget.insert('end', "WARNINGS:\n")
        text_widget.insert('end', "- Trips Knox (voids warranty permanently)\n")
        text_widget.insert('end', "- Breaks Secure Folder, Samsung Pay\n")
        text_widget.insert('end', "- Can brick if wrong firmware used\n")
        text_widget.insert('end', "- Backup EFS partition if possible\n\n")
        
        text_widget.insert('end', "For rooting: Patch AP file with Magisk first!\n")
        
        text_widget.config(state='disabled')
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        if odin_versions:
            ttk.Button(btn_frame,
                      text="Open Odin Folder",
                      command=lambda: os.startfile(odin_dir)).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Close",
                  command=window.destroy).pack(side='right', padx=5)
        
    def show_xiaomi_tools(self):
        """Show Xiaomi tools window"""
        window = tk.Toplevel(self.root)
        window.title("Xiaomi Tools")
        window.geometry("700x500")
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert('end', "XIAOMI/POCO/REDMI TOOLS\n")
        text_widget.insert('end', "=" * 50 + "\n\n")
        
        text_widget.insert('end', "1. MI UNLOCK TOOL (Bootloader Unlock):\n")
        text_widget.insert('end', "   - Apply at: https://account.xiaomi.com\n")
        text_widget.insert('end', "   - Wait 7-15 days for approval\n")
        text_widget.insert('end', "   - Use Mi Unlock Tool to unlock\n")
        text_widget.insert('end', "   - WARNING: Unlocking wipes all data!\n\n")
        
        text_widget.insert('end', "2. MI FLASH TOOL (Firmware Flash):\n")
        text_widget.insert('end', f"   - Location: {Config.PATHS['tools']}\\miflash\\\n")
        text_widget.insert('end', "   - Extract MiFlash20220507.zip\n")
        text_widget.insert('end', "   - Run XiaoMiFlash.exe as Admin\n")
        text_widget.insert('end', "   - Select firmware folder\n")
        text_widget.insert('end', "   - Click Flash\n\n")
        
        text_widget.insert('end', "3. FASTBOOT COMMANDS:\n")
        text_widget.insert('end', "   - Check unlock: fastboot oem device-info\n")
        text_widget.insert('end', "   - Unlock: fastboot flashing unlock\n")
        text_widget.insert('end', "   - Flash recovery: fastboot flash recovery twrp.img\n\n")
        
        text_widget.insert('end', "4. ROOTING METHODS:\n")
        text_widget.insert('end', "   - Patch boot.img with Magisk\n")
        text_widget.insert('end', "   - Flash Magisk zip via TWRP\n")
        text_widget.insert('end', "   - Use KernelSU if supported\n\n")
        
        text_widget.insert('end', "WARNINGS:\n")
        text_widget.insert('end', "- Anti-Rollback (ARB) protection\n")
        text_widget.insert('end', "- Some regions have unlock restrictions\n")
        text_widget.insert('end', "- May need to bind account for 7 days\n")
        text_widget.insert('end', "- EDL mode available for bricked devices\n")
        
        text_widget.config(state='disabled')
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def show_qualcomm_tools(self):
        """Show Qualcomm tools warning"""
        result = messagebox.askyesno(
            "Qualcomm Tools Warning",
            "WARNING: Qualcomm EDL/9008 tools can HARD-BRICK your device if used incorrectly!\n\n"
            "These are advanced tools for:\n"
            "- Bricked device recovery\n"
            "- Firmware flashing without bootloader\n"
            "- Partition manipulation\n\n"
            "Only proceed if you know what you're doing.\n\n"
            "Continue to view tools?"
        )
        
        if result:
            self.show_info(
                "Qualcomm Tools",
                f"QFIL/QPST tools located at:\n{Config.PATHS['tools']}\\qpstqfill\\\n\n"
                f"Drivers: {Config.PATHS['driver_pack']}\\qualcomm_qdloader\\\n\n"
                "Enter EDL/9008 mode with:\n"
                "- Device off, hold Vol Up+Down, connect USB\n"
                "- Or: adb reboot edl\n"
                "- Shows as 'Qualcomm HS-USB QDLoader 9008'"
            )
        
    def show_mediatek_tools(self):
        """Show MediaTek tools info"""
        self.show_info(
            "MediaTek Tools",
            f"SP Flash Tool for MediaTek devices\n\n"
            f"Requirements:\n"
            f"1. MediaTek USB Drivers (install first)\n"
            f"2. Scatter file from firmware\n"
            f"3. Firmware files (.bin, .img)\n\n"
            f"Drivers: {Config.PATHS['driver_pack']}\\mtk_drivers\\\n\n"
            f"WARNING: Authentication required for newer devices!\n"
            f"Need auth file and proper setup.\n\n"
            f"Scatter file format: MTXXXX_Android_scatter.txt"
        )
        
    def show_backup_manager(self):
        """Show backup manager window"""
        window = tk.Toplevel(self.root)
        window.title("Backup Management")
        window.geometry("800x600")
        window.configure(bg='#1e1e1e')
        
        # List of backups
        backups_frame = ttk.LabelFrame(window, text="Available Backups", padding=10)
        backups_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for backups
        columns = ("Name", "Size", "Date", "Files")
        tree = ttk.Treeview(backups_frame, columns=columns, show="headings", height=15)
        
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
        scrollbar = ttk.Scrollbar(backups_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate with backups
        backup_root = Config.PATHS['backup_root']
        if os.path.exists(backup_root):
            backups = []
            for item in os.listdir(backup_root):
                item_path = os.path.join(backup_root, item)
                if os.path.isdir(item_path) and item.startswith('newbackup_'):
                    # Get size
                    total_size = 0
                    file_count = 0
                    for root, dirs, files in os.walk(item_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.exists(file_path):
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                    
                    # Format size
                    if total_size > 1024**3:
                        size_str = f"{total_size/1024**3:.2f} GB"
                    elif total_size > 1024**2:
                        size_str = f"{total_size/1024**2:.2f} MB"
                    elif total_size > 1024:
                        size_str = f"{total_size/1024:.2f} KB"
                    else:
                        size_str = f"{total_size} B"
                    
                    # Get date
                    date_str = datetime.fromtimestamp(os.path.getctime(item_path)).strftime("%Y-%m-%d %H:%M")
                    
                    backups.append((item, size_str, date_str, str(file_count)))
            
            # Sort by date (newest first)
            backups.sort(key=lambda x: x[2], reverse=True)
            
            for backup in backups:
                tree.insert("", "end", values=backup, tags=(backup[0],))
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        def open_selected():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                backup_name = item['values'][0]
                backup_path = os.path.join(backup_root, backup_name)
                if os.path.exists(backup_path):
                    os.startfile(backup_path)
        
        def delete_selected():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                backup_name = item['values'][0]
                
                result = messagebox.askyesno(
                    "Delete Backup",
                    f"Are you sure you want to delete backup:\n{backup_name}?\n\n"
                    "This action cannot be undone."
                )
                
                if result:
                    backup_path = os.path.join(backup_root, backup_name)
                    import shutil
                    try:
                        shutil.rmtree(backup_path)
                        tree.delete(selection[0])
                        self.show_info("Deleted", f"Backup deleted: {backup_name}")
                    except Exception as e:
                        self.show_error("Error", f"Failed to delete backup:\n{e}")
        
        ttk.Button(btn_frame,
                  text="Open Selected",
                  command=open_selected).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Delete Selected",
                  command=delete_selected,
                  style='Red.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Clean Old Backups",
                  command=lambda: self.clean_backups(tree)).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Close",
                  command=window.destroy).pack(side='right', padx=5)
        
    def clean_backups(self, tree):
        """Clean old backups (keep last 5)"""
        items = tree.get_children()
        if len(items) <= 5:
            self.show_info("Cleanup", "No old backups to clean (keeping last 5)")
            return
        
        result = messagebox.askyesno(
            "Clean Backups",
            f"This will keep only the last 5 backups and delete {len(items)-5} older ones.\n\n"
            "Continue?"
        )
        
        if not result:
            return
        
        # Get all backups sorted by date
        backups = []
        for item in items:
            values = tree.item(item)['values']
            backups.append((item, values[0], values[2]))  # item_id, name, date
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x[2], reverse=True)
        
        # Delete old ones
        import shutil
        deleted = 0
        for i, (item_id, backup_name, date) in enumerate(backups):
            if i >= 5:  # Keep only first 5 (newest)
                backup_path = os.path.join(Config.PATHS['backup_root'], backup_name)
                try:
                    shutil.rmtree(backup_path)
                    tree.delete(item_id)
                    deleted += 1
                except Exception as e:
                    print(f"Failed to delete {backup_name}: {e}")
        
        self.show_info("Cleanup Complete", f"Deleted {deleted} old backups.\nKept 5 most recent backups.")
        
    # ============================================
    # ADVANCED TOOLS IMPLEMENTATIONS
    # ============================================
    
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
            
        filename = f"screenshot_{Config.TIMESTAMP}.png"
        backup_folder = Config.get_backup_folder()
        
        self.update_status("Taking screenshot...")
        self.progress.start()
        
        def screenshot():
            # Take screenshot
            self.adb.run_command([self.adb.adb_path, 'shell', 'screencap', '-p', f'/sdcard/{filename}'])
            
            # Pull to computer
            self.adb.run_command([self.adb.adb_path, 'pull', f'/sdcard/{filename}', os.path.join(backup_folder, filename)])
            
            # Clean up
            self.adb.run_command([self.adb.adb_path, 'shell', 'rm', f'/sdcard/{filename}'])
            
            self.progress.stop()
            self.root.after(0, lambda: self.show_info(
                "Screenshot Saved",
                f"Screenshot saved to:\n{os.path.join(backup_folder, filename)}"
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
                code, out, err = self.adb.run_command([self.adb.adb_path, 'install', filename])
                
                self.progress.stop()
                
                if code == 0:
                    self.root.after(0, lambda: self.show_info(
                        "Install Successful",
                        f"APK installed successfully:\n{os.path.basename(filename)}"
                    ))
                    self.update_status("APK installed")
                else:
                    self.root.after(0, lambda: self.show_error(
                        "Install Failed",
                        f"Failed to install APK:\n{err}"
                    ))
            
            self.run_threaded(install)
        
    def pull_files(self):
        """Pull files from device"""
        window = tk.Toplevel(self.root)
        window.title("Pull Files from Device")
        window.geometry("500x300")
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Pull files from device to computer",
                 background='#1e1e1e',
                 foreground='#00ff00',
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Source path
        ttk.Label(window,
                 text="Device path:",
                 background='#1e1e1e',
                 foreground='white').pack(anchor='w', padx=20)
        
        source_var = tk.StringVar(value="/sdcard/DCIM")
        source_entry = ttk.Entry(window, textvariable=source_var, width=50)
        source_entry.pack(padx=20, pady=5, fill='x')
        
        # Destination path
        ttk.Label(window,
                 text="Computer folder:",
                 background='#1e1e1e',
                 foreground='white').pack(anchor='w', padx=20)
        
        dest_var = tk.StringVar(value=Config.get_backup_folder())
        dest_entry = ttk.Entry(window, textvariable=dest_var, width=50)
        dest_entry.pack(padx=20, pady=5, fill='x')
        
        def browse_dest():
            folder = filedialog.askdirectory(
                title="Select destination folder",
                initialdir=Config.get_backup_folder()
            )
            if folder:
                dest_var.set(folder)
        
        ttk.Button(window,
                  text="Browse...",
                  command=browse_dest).pack(pady=5)
        
        def start_pull():
            source = source_var.get()
            dest = dest_var.get()
            
            if not source or not dest:
                self.show_warning("Missing Path", "Please enter both source and destination paths")
                return
            
            self.update_status(f"Pulling files from {source}...")
            self.progress.start()
            
            def pull():
                code, out, err = self.adb.run_command([self.adb.adb_path, 'pull', source, dest])
                
                self.progress.stop()
                
                if code == 0:
                    self.root.after(0, lambda: self.show_info(
                        "Pull Successful",
                        f"Files pulled successfully to:\n{dest}"
                    ))
                    self.update_status("Files pulled")
                else:
                    self.root.after(0, lambda: self.show_error(
                        "Pull Failed",
                        f"Failed to pull files:\n{err}"
                    ))
                
                window.destroy()
            
            self.run_threaded(pull)
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame,
                  text="Start Pull",
                  command=start_pull,
                  style='Green.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Cancel",
                  command=window.destroy).pack(side='right', padx=5)
        
    def push_files(self):
        """Push files to device"""
        window = tk.Toplevel(self.root)
        window.title("Push Files to Device")
        window.geometry("500x300")
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Push files from computer to device",
                 background='#1e1e1e',
                 foreground='#00ff00',
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Source file
        ttk.Label(window,
                 text="Computer file:",
                 background='#1e1e1e',
                 foreground='white').pack(anchor='w', padx=20)
        
        source_var = tk.StringVar()
        
        def browse_source():
            filename = filedialog.askopenfilename(
                title="Select file to push"
            )
            if filename:
                source_var.set(filename)
        
        source_frame = ttk.Frame(window)
        source_frame.pack(fill='x', padx=20, pady=5)
        
        source_entry = ttk.Entry(source_frame, textvariable=source_var, width=40)
        source_entry.pack(side='left', padx=(0, 5))
        
        ttk.Button(source_frame,
                  text="Browse...",
                  command=browse_source).pack(side='right')
        
        # Destination path
        ttk.Label(window,
                 text="Device path:",
                 background='#1e1e1e',
                 foreground='white').pack(anchor='w', padx=20)
        
        dest_var = tk.StringVar(value="/sdcard/")
        dest_entry = ttk.Entry(window, textvariable=dest_var, width=50)
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
                code, out, err = self.adb.run_command([self.adb.adb_path, 'push', source, dest])
                
                self.progress.stop()
                
                if code == 0:
                    self.root.after(0, lambda: self.show_info(
                        "Push Successful",
                        f"File pushed successfully to:\n{dest}"
                    ))
                    self.update_status("File pushed")
                else:
                    self.root.after(0, lambda: self.show_error(
                        "Push Failed",
                        f"Failed to push file:\n{err}"
                    ))
                
                window.destroy()
            
            self.run_threaded(push)
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame,
                  text="Start Push",
                  command=start_push,
                  style='Green.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Cancel",
                  command=window.destroy).pack(side='right', padx=5)
        
    def open_adb_shell(self):
        """Open ADB shell in new window"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        # For Windows, open command prompt with ADB
        subprocess.Popen(['start', 'cmd', '/k', f'"{self.adb.adb_path}" shell'], 
                        shell=True)
        
    def show_reboot_menu(self):
        """Show reboot options menu"""
        window = tk.Toplevel(self.root)
        window.title("Reboot Options")
        window.geometry("300x250")
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Select reboot option:",
                 background='#1e1e1e',
                 foreground='#00ff00',
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        options = [
            ("Reboot", "reboot"),
            ("Bootloader", "bootloader"),
            ("Recovery", "recovery"),
            ("Fastboot", "fastboot"),
            ("Soft Reboot", "soft"),
        ]
        
        for text, command in options:
            btn = ttk.Button(window,
                           text=text,
                           command=lambda cmd=command: (self.adb.run_command([self.adb.adb_path, 'reboot', cmd]), window.destroy()),
                           style='Tool.TButton')
            btn.pack(pady=5, padx=50, fill='x')
        
        ttk.Button(window,
                  text="Cancel",
                  command=window.destroy).pack(pady=10)
        
    def remove_bloatware(self):
        """Show bloatware removal window"""
        window = tk.Toplevel(self.root)
        window.title("Remove Bloatware")
        window.geometry("700x500")
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Warning: Can break system functionality!",
                 background='#1e1e1e',
                 foreground='#ff6b6b',
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Get package list
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 9))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.update_status("Getting package list...")
        self.progress.start()
        
        def get_packages():
            code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', 'pm list packages'])
            
            self.progress.stop()
            
            if code == 0:
                packages = out.strip().split('\n')
                packages = [pkg.replace('package:', '') for pkg in packages if pkg]
                
                # Filter for common bloatware
                bloat_keywords = ['facebook', 'test', 'demo', 'sample', 'carrier', 'bloat']
                bloat_packages = []
                
                for pkg in packages:
                    if any(keyword in pkg.lower() for keyword in bloat_keywords):
                        bloat_packages.append(pkg)
                
                self.root.after(0, lambda: self.display_bloatware(text_widget, bloat_packages))
            else:
                self.root.after(0, lambda: text_widget.insert('end', f"Error: {err}"))
                text_widget.config(state='disabled')
        
        self.run_threaded(get_packages)
        
        # Package entry
        ttk.Label(window,
                 text="Package to disable:",
                 background='#1e1e1e',
                 foreground='white').pack(anchor='w', padx=20)
        
        pkg_var = tk.StringVar()
        pkg_entry = ttk.Entry(window, textvariable=pkg_var, width=50)
        pkg_entry.pack(padx=20, pady=5, fill='x')
        
        def disable_package():
            pkg = pkg_var.get().strip()
            if pkg:
                self.adb.run_command([self.adb.adb_path, 'shell', 'pm', 'disable-user', '--user', '0', pkg])
                self.show_info("Disabled", f"Package disabled: {pkg}")
        
        ttk.Button(window,
                  text="Disable Package",
                  command=disable_package,
                  style='Red.TButton').pack(pady=10)
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
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
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 9))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert('end', "Starting logcat...\n")
        text_widget.insert('end', "Press Stop to stop logging.\n\n")
        
        # Control variables
        self.logcat_running = True
        self.logcat_process = None
        
        def start_logcat():
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
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame,
                  text="Stop Logcat",
                  command=stop_logcat,
                  style='Red.TButton').pack(side='left', padx=5)
        
        def save_logcat():
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"logcat_{Config.TIMESTAMP}.log"
            )
            
            if filename:
                content = text_widget.get(1.0, 'end')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.show_info("Saved", f"Logcat saved to:\n{filename}")
        
        ttk.Button(btn_frame,
                  text="Save Log",
                  command=save_logcat).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Clear",
                  command=lambda: text_widget.delete(1.0, 'end')).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Close",
                  command=lambda: (stop_logcat(), window.destroy())).pack(side='right', padx=5)
        
    def check_root(self):
        """Check root status"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        self.update_status("Checking root status...")
        self.progress.start()
        
        def check():
            code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', 'which', 'su'])
            
            self.progress.stop()
            
            if code == 0 and out.strip():
                # Check for Magisk
                magisk_code, magisk_out, magisk_err = self.adb.run_command([self.adb.adb_path, 'shell', 'su -c "magisk -v"'])
                
                # Check for KernelSU
                kernelsu_code, kernelsu_out, kernelsu_err = self.adb.run_command([self.adb.adb_path, 'shell', 'su -c "ksud"'])
                
                message = "[✓] ROOTED - su binary found\n\n"
                
                if magisk_code == 0:
                    message += f"Root Method: Magisk {magisk_out.strip()}\n"
                elif kernelsu_code == 0:
                    message += "Root Method: KernelSU\n"
                else:
                    message += "Root Method: Unknown (generic su)\n"
                
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
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 9))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.update_status("Getting app list...")
        self.progress.start()
        
        def get_apps():
            code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', 'pm list packages -f'])
            
            self.progress.stop()
            
            if code == 0:
                apps = out.strip().split('\n')
                apps = [app.replace('package:', '') for app in apps if app]
                
                self.root.after(0, lambda: self.display_apps(text_widget, apps))
            else:
                self.root.after(0, lambda: text_widget.insert('end', f"Error: {err}"))
                text_widget.config(state='disabled')
                self.update_status("Failed to get apps")
        
        self.run_threaded(get_apps)
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        def save_apps():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"apps_list_{Config.TIMESTAMP}.txt"
            )
            
            if filename:
                content = text_widget.get(1.0, 'end')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.show_info("Saved", f"App list saved to:\n{filename}")
        
        ttk.Button(btn_frame,
                  text="Save List",
                  command=save_apps).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Close",
                  command=window.destroy).pack(side='right', padx=5)
        
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
        window.configure(bg='#1e1e1e')
        
        ttk.Label(window,
                 text="Backup single app with data",
                 background='#1e1e1e',
                 foreground='#00ff00',
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Package name
        ttk.Label(window,
                 text="Package name:",
                 background='#1e1e1e',
                 foreground='white').pack(anchor='w', padx=20)
        
        pkg_var = tk.StringVar()
        pkg_entry = ttk.Entry(window, textvariable=pkg_var, width=50)
        pkg_entry.pack(padx=20, pady=5, fill='x')
        
        # Output file
        ttk.Label(window,
                 text="Output file:",
                 background='#1e1e1e',
                 foreground='white').pack(anchor='w', padx=20)
        
        output_var = tk.StringVar(value=os.path.join(Config.get_backup_folder(), "app_backup.ab"))
        output_entry = ttk.Entry(window, textvariable=output_var, width=50)
        output_entry.pack(padx=20, pady=5, fill='x')
        
        def browse_output():
            filename = filedialog.asksaveasfilename(
                defaultextension=".ab",
                filetypes=[("Android Backup", "*.ab"), ("All files", "*.*")],
                initialfile="app_backup.ab",
                initialdir=Config.get_backup_folder()
            )
            if filename:
                output_var.set(filename)
        
        ttk.Button(window,
                  text="Browse...",
                  command=browse_output).pack(pady=5)
        
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
                code, out, err = self.adb.run_command(
                    [self.adb.adb_path, 'backup', '-f', output, '-apk', pkg]
                )
                
                self.progress.stop()
                
                if code == 0 and os.path.exists(output):
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
                        f"Failed to backup app:\n{err}\n\n"
                        "Possible reasons:\n"
                        "- User cancelled on device\n"
                        "- App doesn't allow backup\n"
                        "- Insufficient storage"
                    ))
                    self.update_status("App backup failed")
                
                window.destroy()
            
            self.run_threaded(backup)
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame,
                  text="Start Backup",
                  command=start_backup,
                  style='Green.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="Cancel",
                  command=window.destroy).pack(side='right', padx=5)
        
    def backup_user_data(self):
        """Backup user data (photos, documents, etc.)"""
        if not self.current_device:
            self.show_warning("No Device", "Connect a device first")
            return
        
        result = messagebox.askyesno(
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
        
        backup_folder = Config.get_backup_folder()
        user_data_folder = os.path.join(backup_folder, "User_Data")
        os.makedirs(user_data_folder, exist_ok=True)
        
        self.update_status("Backing up user data...")
        self.progress.start()
        
        def backup():
            folders = [
                ("DCIM", "/sdcard/DCIM"),
                ("Downloads", "/sdcard/Download"),
                ("Documents", "/sdcard/Documents"),
                ("WhatsApp", "/sdcard/WhatsApp"),
            ]
            
            for name, path in folders:
                self.update_status(f"Backing up {name}...")
                dest_folder = os.path.join(user_data_folder, name)
                os.makedirs(dest_folder, exist_ok=True)
                
                # Check if folder exists on device
                code, out, err = self.adb.run_command([self.adb.adb_path, 'shell', f'ls {path}'])
                if code == 0:
                    self.adb.run_command([self.adb.adb_path, 'pull', path, dest_folder])
            
            self.progress.stop()
            
            # Create summary
            summary_file = os.path.join(user_data_folder, "backup_summary.txt")
            with open(summary_file, 'w') as f:
                f.write(f"User Data Backup - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                
                for name, path in folders:
                    dest_folder = os.path.join(user_data_folder, name)
                    if os.path.exists(dest_folder):
                        file_count = len([f for f in os.listdir(dest_folder) if os.path.isfile(os.path.join(dest_folder, f))])
                        f.write(f"{name}: {file_count} files\n")
                    else:
                        f.write(f"{name}: Not backed up (not found on device)\n")
            
            self.root.after(0, lambda: self.show_info(
                "Backup Complete",
                f"User data backed up successfully!\n\n"
                f"Location: {user_data_folder}\n\n"
                "Check backup_summary.txt for details."
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
        
    def show_brand_guide(self, brand):
        """Show brand-specific rooting guide"""
        guides = {
            'samsung': self.show_samsung_guide,
            'xiaomi': self.show_xiaomi_guide,
            'google': self.show_google_guide,
            'oneplus': self.show_oneplus_guide,
        }
        
        if brand in guides:
            guides[brand]()
        else:
            self.show_generic_guide()
        
    def show_samsung_guide(self):
        """Show Samsung rooting guide"""
        window = tk.Toplevel(self.root)
        window.title("Samsung Rooting Guide")
        window.geometry("700x500")
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        guide = """
===== SAMSUNG ROOTING GUIDE =====

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
- Future OTA updates may fail

RECOMMENDED:
- Backup EFS partition if possible
- Use home_csc to keep data (but risky)
- Research device-specific issues on XDA
        """
        
        text_widget.insert('end', guide)
        text_widget.config(state='disabled')
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def show_xiaomi_guide(self):
        """Show Xiaomi rooting guide"""
        window = tk.Toplevel(self.root)
        window.title("Xiaomi Rooting Guide")
        window.geometry("700x500")
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        guide = """
===== XIAOMI ROOTING GUIDE =====

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

6. Alternative: Flash TWRP and Magisk:
   - Download TWRP for your device
   - Fastboot: fastboot flash recovery twrp.img
   - Boot to recovery
   - Flash Magisk.zip
   - Reboot

⚠ WARNINGS:
- Anti-Rollback (ARB) protection
- Unlocking voids warranty in some regions
- Some features may break (Google Pay, banking)
- Weekly MIUI updates may break root

TIPS:
- Use "fastboot getvar anti" to check ARB status
- Never downgrade firmware with higher ARB version
- Backup persist partition if possible
- Use Xiaomi.eu ROMs for better experience
        """
        
        text_widget.insert('end', guide)
        text_widget.config(state='disabled')
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def show_google_guide(self):
        """Show Google Pixel rooting guide"""
        self.show_info(
            "Google Pixel Rooting Guide",
            "===== GOOGLE PIXEL ROOTING GUIDE =====\n\n"
            "1. Enable OEM Unlocking:\n"
            "   - Settings > About Phone > Build Number (tap 7 times)\n"
            "   - Settings > Developer Options > OEM unlocking\n\n"
            "2. Unlock bootloader:\n"
            "   - adb reboot bootloader\n"
            "   - fastboot flashing unlock\n"
            "   - WARNING: Wipes all data!\n\n"
            "3. Download factory image:\n"
            "   - https://developers.google.com/android/images\n"
            "   - Extract boot.img from archive\n\n"
            "4. Patch with Magisk:\n"
            "   - Copy boot.img to device\n"
            "   - Install Magisk app\n"
            "   - Patch boot image\n"
            "   - Copy patched image to PC\n\n"
            "5. Flash patched boot:\n"
            "   - fastboot flash boot magisk_patched.img\n"
            "   - fastboot reboot\n\n"
            "6. Install Magisk app:\n"
            "   - Manage root permissions\n"
            "   - Install modules\n\n"
            "✓ Easiest devices to root\n"
            "✓ Regular security updates\n"
            "✓ Good developer support\n\n"
            "Note: May need to disable verity on newer devices:\n"
            "fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img"
        )
        
    def show_oneplus_guide(self):
        """Show OnePlus rooting guide"""
        self.show_info(
            "OnePlus Rooting Guide",
            "===== ONEPLUS ROOTING GUIDE =====\n\n"
            "1. Enable OEM Unlocking:\n"
            "   - Settings > About Phone > Build Number (tap 7 times)\n"
            "   - Settings > Developer Options > OEM unlocking\n\n"
            "2. Unlock bootloader:\n"
            "   - adb reboot bootloader\n"
            "   - fastboot oem unlock\n"
            "   - WARNING: Wipes all data!\n\n"
            "3. Extract boot from payload.bin:\n"
            "   - Download full OTA zip\n"
            "   - Use payload_dumper tool\n"
            "   - Extract boot.img\n\n"
            "4. Patch with Magisk:\n"
            "   - Copy boot.img to device\n"
            "   - Install Magisk app\n"
            "   - Patch boot image\n"
            "   - Copy patched image to PC\n\n"
            "5. Flash patched boot:\n"
            "   - fastboot flash boot magisk_patched.img\n"
            "   - fastboot reboot\n\n"
            "Alternative method (MSM Tool):\n"
            "- For bricked devices\n"
            "- Qualcomm EDL mode\n"
            "- Use MSM Download Tool\n\n"
            "WARNINGS:\n"
            "- Voids warranty\n"
            -"May break Widevine L1\n"
            "- Banking apps may not work\n\n"
            "OnePlus devices generally have good developer support."
        )
        
    def show_generic_guide(self):
        """Show generic rooting guide"""
        window = tk.Toplevel(self.root)
        window.title("Generic Rooting Guide")
        window.geometry("700x500")
        window.configure(bg='#1e1e1e')
        
        text_widget = scrolledtext.ScrolledText(window,
                                               bg='#0c0c0c',
                                               fg='#00ff00',
                                               font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Get device info if available
        device_info = ""
        if self.current_device:
            props = self.adb.get_device_props(['ro.product.manufacturer', 'ro.product.model'])
            if props:
                manufacturer = props.get('ro.product.manufacturer', 'Unknown')
                model = props.get('ro.product.model', 'Unknown')
                device_info = f"\nCurrent device: {manufacturer} {model}\n"
        
        guide = f"""
===== GENERIC ROOTING GUIDE ====={device_info}

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

4. Chipset-specific tools:
   - Qualcomm: QFIL, QPST, EDL mode
   - MediaTek: SP Flash Tool
   - Exynos: Similar to Qualcomm
   - Kirin: HiSuite, DC Phoenix

5. IMPORTANT STEPS:
   - Backup everything first!
   - Unlock bootloader (if possible)
   - Use correct firmware for your model
   - Don't skip any steps in guides
   - Test with temporary boot first

6. TROUBLESHOOTING:
   - Bootloop: Flash stock firmware
   - Bricked device: Use EDL/Download mode
   - No root: Check if patching succeeded
   - SafetyNet: Use Magisk modules

⚠ WARNINGS:
- Always backup before modifying
- Use correct files for your exact model
- Read warnings in device-specific guides
- Rooting voids warranty
- Security risks exist
        """
        
        text_widget.insert('end', guide)
        text_widget.config(state='disabled')
        
        ttk.Button(window,
                  text="Close",
                  command=window.destroy).pack(pady=10)
        
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    try:
        app = ADBRootToolGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
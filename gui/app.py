import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from config.settings import config
from core.adb_manager import ADBManager
from gui.styles import StyleManager
from gui.widgets.tabs.main_tools_tab import MainToolsTab
from gui.widgets.tabs.backup_tools_tab import BackupToolsTab
# ... import other tab classes

class ADBRootToolGUI:
    """Main GUI Application"""
    
    def __init__(self):
        self.config = config
        self.adb = ADBManager(config)
        self.style_manager = StyleManager()
        self.current_device: Optional[str] = None
        
        self.setup_gui()
        self.check_initial_status()
    
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
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(title_frame,
                 text="ULTIMATE ADB ROOT TOOL v4.0",
                 style='Title.TLabel').pack()
        
        ttk.Label(title_frame,
                 text="AndroidRootSuite - Complete GUI Edition",
                 style='Subtitle.TLabel').pack()
    
    def create_status_frame(self):
        """Create device status frame"""
        status_frame = ttk.LabelFrame(self.root, text="Device Status", padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.device_status_label = ttk.Label(
            status_frame,
            text="No device connected",
            style='Status.TLabel'
        )
        self.device_status_label.pack(side='left', padx=10)
        
        ttk.Button(status_frame,
                  text="Check Connection",
                  command=self.check_device_connection,
                  style='Tool.TButton').pack(side='right', padx=5)
        
        ttk.Button(status_frame,
                  text="Get Device Info",
                  command=self.show_device_info,
                  style='Tool.TButton').pack(side='right', padx=5)
    
    def create_tabbed_interface(self):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Initialize tabs
        self.tabs = {
            'main': MainToolsTab(self.notebook, self),
            'backup': BackupToolsTab(self.notebook, self),
            # ... other tabs
        }
        
        for name, tab in self.tabs.items():
            self.notebook.add(tab.frame, text=tab.TAB_NAME)
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar_frame = ttk.Frame(self.root)
        status_bar_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.status_bar = ttk.Label(
            status_bar_frame,
            text="Ready",
            style='Status.TLabel'
        )
        self.status_bar.pack(side='left')
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            status_bar_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side='right', padx=10)
        
        # Version info
        ttk.Label(status_bar_frame,
                 text="v4.0 - Python GUI Edition",
                 style='Subtitle.TLabel').pack(side='right', padx=20)
    
    # ==================== Core Methods ====================
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def run_threaded(self, func, *args, **kwargs):
        """Run function in thread to avoid GUI freeze"""
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
    
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
                foreground=self.style_manager.colors['fg']
            )
            self.current_device = devices[0]['serial']
            self.update_status(f"{len(devices)} device(s) connected")
        else:
            self.device_status_label.config(
                text="No device connected\nEnable USB Debugging and connect device",
                foreground=self.style_manager.colors['info']
            )
            self.current_device = None
            self.update_status("No devices detected")
    
    # ==================== Dialog Methods ====================
    
    def show_warning(self, title: str, message: str):
        """Show warning message"""
        messagebox.showwarning(title, message)
    
    def show_error(self, title: str, message: str):
        """Show error message"""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """Show info message"""
        messagebox.showinfo(title, message)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

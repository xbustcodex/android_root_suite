"""
Xiaomi-specific tools
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class XiaomiTools:
    """Xiaomi device tools"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
    
    def show_tools(self):
        """Show Xiaomi tools window"""
        window = tk.Toplevel(self.app.root)
        window.title("Xiaomi Tools")
        window.geometry("700x500")
        window.configure(bg=self.app.style_manager.colors['bg'])
        
        text_widget = scrolledtext.ScrolledText(
            window,
            bg='#0c0c0c',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        info = """XIAOMI/POCO/REDMI TOOLS
==================================================

1. MI UNLOCK TOOL (Bootloader Unlock):
   - Apply at: https://account.xiaomi.com
   - Wait 7-15 days for approval
   - Use Mi Unlock Tool to unlock
   - WARNING: Unlocking wipes all data!

2. MI FLASH TOOL (Firmware Flash):
   - Location: {tools_path}\\miflash\\
   - Extract MiFlash20220507.zip
   - Run XiaoMiFlash.exe as Admin
   - Select firmware folder
   - Click Flash

3. FASTBOOT COMMANDS:
   - Check unlock: fastboot oem device-info
   - Unlock: fastboot flashing unlock
   - Flash recovery: fastboot flash recovery twrp.img

4. ROOTING METHODS:
   - Patch boot.img with Magisk
   - Flash Magisk zip via TWRP
   - Use KernelSU if supported

WARNINGS:
- Anti-Rollback (ARB) protection
- Some regions have unlock restrictions
- May need to bind account for 7 days
- EDL mode available for bricked devices""".format(
    tools_path=self.app.config.PATHS['tools']
)
        
        text_widget.insert('end', info)
        text_widget.config(state='disabled')
        
        ttk.Button(
            window,
            text="Close",
            command=window.destroy
        ).pack(pady=10)

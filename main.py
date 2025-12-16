#!/usr/bin/env python3
"""
Ultimate ADB Root Tool v4.0 - GUI Edition
Refactored modular version
"""

import sys
import traceback

def main():
    """Main entry point"""
    try:
        from gui.app import ADBRootToolGUI
        app = ADBRootToolGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        
        # Try fallback to simple error window
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror(
                "Fatal Error",
                f"Failed to start application:\n\n{e}\n\n"
                "Please check the console for details."
            )
        except:
            pass
        
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()

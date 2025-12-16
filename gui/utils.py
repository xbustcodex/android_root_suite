"""
GUI utility functions
"""

import threading
import time
from typing import Callable, Any
from tkinter import messagebox, filedialog
import tkinter as tk

class DialogHelper:
    """Helper for dialog operations"""
    
    @staticmethod
    def show_info(parent, title: str, message: str):
        """Show info dialog"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(parent, title: str, message: str):
        """Show warning dialog"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_error(parent, title: str, message: str):
        """Show error dialog"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def ask_yesno(parent, title: str, message: str) -> bool:
        """Show yes/no dialog"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def ask_okcancel(parent, title: str, message: str) -> bool:
        """Show ok/cancel dialog"""
        return messagebox.askokcancel(title, message)
    
    @staticmethod
    def select_file(parent, title: str = "Select File", 
                   filetypes: list = None, initialdir: str = None) -> str:
        """Open file selection dialog"""
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        
        return filedialog.askopenfilename(
            parent=parent,
            title=title,
            filetypes=filetypes,
            initialdir=initialdir
        )
    
    @staticmethod
    def select_folder(parent, title: str = "Select Folder", initialdir: str = None) -> str:
        """Open folder selection dialog"""
        return filedialog.askdirectory(
            parent=parent,
            title=title,
            initialdir=initialdir
        )
    
    @staticmethod
    def save_file(parent, title: str = "Save File", 
                 defaultextension: str = "", filetypes: list = None,
                 initialfile: str = "", initialdir: str = None) -> str:
        """Open save file dialog"""
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        
        return filedialog.asksaveasfilename(
            parent=parent,
            title=title,
            defaultextension=defaultextension,
            filetypes=filetypes,
            initialfile=initialfile,
            initialdir=initialdir
        )

class ThreadHelper:
    """Helper for threaded operations"""
    
    @staticmethod
    def run_in_thread(target: Callable, *args, **kwargs) -> threading.Thread:
        """Run function in background thread"""
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    
    @staticmethod
    def run_with_progress(parent, progress_widget, status_widget, 
                         target: Callable, *args, **kwargs):
        """Run function with progress indication"""
        def wrapper():
            # Start progress
            parent.after(0, progress_widget.start)
            
            try:
                # Run target function
                result = target(*args, **kwargs)
                
                # Stop progress
                parent.after(0, progress_widget.stop)
                
                return result
            except Exception as e:
                # Stop progress on error
                parent.after(0, progress_widget.stop)
                raise e
        
        return ThreadHelper.run_in_thread(wrapper)
    
    @staticmethod
    def update_gui(parent, func: Callable, *args, **kwargs):
        """Schedule GUI update from thread"""
        parent.after(0, lambda: func(*args, **kwargs))

class TextWidgetHelper:
    """Helper for text widget operations"""
    
    @staticmethod
    def clear_text_widget(widget):
        """Clear text widget"""
        widget.delete(1.0, tk.END)
    
    @staticmethod
    def append_text(widget, text: str, tag: str = None):
        """Append text to widget"""
        widget.insert(tk.END, text)
        if tag:
            widget.tag_add(tag, "end-1c", tk.END)
    
    @staticmethod
    def set_readonly(widget, readonly: bool = True):
        """Set text widget to read-only"""
        state = tk.DISABLED if readonly else tk.NORMAL
        widget.config(state=state)

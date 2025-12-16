"""
Qualcomm-specific tools
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class QualcommTools:
    """Qualcomm device tools"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
    
    def show_tools(self):
        """Show Qualcomm tools warning and info"""
        result = self.app.show_yesno_dialog(
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
            self.app.show_info(
                "Qualcomm Tools",
                f"QFIL/QPST tools located at:\n{self.app.config.PATHS['tools']}\\qpstqfill\\\n\n"
                f"Drivers: {self.app.config.PATHS['driver_pack']}\\qualcomm_qdloader\\\n\n"
                "Enter EDL/9008 mode with:\n"
                "- Device off, hold Vol Up+Down, connect USB\n"
                "- Or: adb reboot edl\n"
                "- Shows as 'Qualcomm HS-USB QDLoader 9008'"
            )

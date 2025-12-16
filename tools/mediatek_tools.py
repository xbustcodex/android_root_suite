"""
MediaTek-specific tools
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app import ADBRootToolGUI

class MediaTekTools:
    """MediaTek device tools"""
    
    def __init__(self, app: 'ADBRootToolGUI'):
        self.app = app
    
    def show_tools(self):
        """Show MediaTek tools info"""
        self.app.show_info(
            "MediaTek Tools",
            f"SP Flash Tool for MediaTek devices\n\n"
            f"Requirements:\n"
            f"1. MediaTek USB Drivers (install first)\n"
            f"2. Scatter file from firmware\n"
            f"3. Firmware files (.bin, .img)\n\n"
            f"Drivers: {self.app.config.PATHS['driver_pack']}\\mtk_drivers\\\n\n"
            f"WARNING: Authentication required for newer devices!\n"
            f"Need auth file and proper setup.\n\n"
            f"Scatter file format: MTXXXX_Android_scatter.txt"
        )

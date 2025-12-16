"""
Tab widgets module
"""

from .base_tab import BaseTab
from .main_tools_tab import MainToolsTab
from .backup_tools_tab import BackupToolsTab
from .root_tools_tab import RootToolsTab
from .brand_tools_tab import BrandToolsTab
from .advanced_tools_tab import AdvancedToolsTab

__all__ = [
    'BaseTab',
    'MainToolsTab', 'BackupToolsTab', 'RootToolsTab',
    'BrandToolsTab', 'AdvancedToolsTab'
]

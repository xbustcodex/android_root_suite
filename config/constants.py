"""
Application constants
"""

# Device property names
DEVICE_PROPERTIES_BASIC = [
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

DEVICE_PROPERTIES_ADVANCED = [
    'ro.build.fingerprint',
    'ro.build.type',
    'ro.build.tags',
    'ro.build.user',
    'ro.build.id',
    'ro.product.name',
]

# Boot partition paths
BOOT_PARTITION_PATHS = [
    "/dev/block/bootdevice/by-name/boot",
    "/dev/block/bootdevice/by-name/boot_a",
    "/dev/block/bootdevice/by-name/boot_b",
    "/dev/block/bootdevice/by-name/kernel",
    "/dev/block/bootdevice/by-name/bootimg",
]

# Backup folder names
BACKUP_FOLDERS = [
    ("DCIM", "/sdcard/DCIM"),
    ("Downloads", "/sdcard/Download"),
    ("Documents", "/sdcard/Documents"),
    ("WhatsApp", "/sdcard/WhatsApp"),
]

# Root methods
ROOT_METHODS = [
    ("Magisk", "magisk"),
    ("KernelSU", "kernelsu"),
    ("APatch", "apatch"),
]

# Brand-specific tools
BRAND_TOOLS = [
    ("Samsung", "samsung", "Odin"),
    ("Xiaomi", "xiaomi", "Mi Flash"),
    ("Qualcomm", "qualcomm", "QFIL/QPST"),
    ("MediaTek", "mediatek", "SP Flash"),
]

# Driver packs
DRIVER_PACKS = [
    ("Universal ADB Driver", "universal_adb_driver"),
    ("Google USB Driver", "google_usb"),
    ("Samsung USB Driver", "samsung_usb"),
    ("MediaTek Driver", "mtk_drivers"),
    ("Qualcomm QDLoader", "qualcomm_qdloader"),
    ("Xiaomi Driver", "miflash"),
]

"""FileVault, SIP, Gatekeeper and automatic update settings."""

from ..util import IS_MACOS, run, unsupported

SOFTWARE_UPDATE = "/Library/Preferences/com.apple.SoftwareUpdate"


def collect(cfg):
    if not IS_MACOS:
        return unsupported()
    return {
        "filevault": run(["fdesetup", "status"]),
        "sip": run(["csrutil", "status"]),
        "gatekeeper": run(["spctl", "--status"]),
        "auto_download": run(["defaults", "read", SOFTWARE_UPDATE, "AutomaticDownload"]),
        "auto_install_macos": run(["defaults", "read", SOFTWARE_UPDATE, "AutomaticallyInstallMacOSUpdates"]),
        "critical_updates": run(["defaults", "read", SOFTWARE_UPDATE, "CriticalUpdateInstall"]),
        "app_store_auto_update": run(["defaults", "read", "/Library/Preferences/com.apple.commerce", "AutoUpdate"]),
    }

"""
Platform detection and cross-platform utilities.
Works on both Windows and Linux.
"""
import platform
import sys
from pathlib import Path
from typing import Dict, Any
import os

class PlatformInfo:
    """Detect and handle platform-specific operations"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == 'Windows'
        self.is_linux = self.system == 'Linux'
        self.is_mac = self.system == 'Darwin'
        
    def get_info(self) -> Dict[str, Any]:
        """Get complete platform information"""
        return {
            'system': self.system,
            'is_windows': self.is_windows,
            'is_linux': self.is_linux,
            'is_mac': self.is_mac,
            'python_version': sys.version,
            'architecture': platform.machine(),
            'platform': platform.platform()
        }
    
    def get_chrome_path(self) -> str:
        """Get Chrome executable path for current platform"""
        if self.is_windows:
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        elif self.is_linux:
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        return None
    
    @staticmethod
    def get_project_root() -> Path:
        """Get project root directory (cross-platform)"""
        return Path(__file__).parent.parent.resolve()
    
    @staticmethod
    def get_database_path() -> Path:
        """Get database path (cross-platform)"""
        root = PlatformInfo.get_project_root()
        return root / "database" / "campervan_prices.db"
    
    @staticmethod
    def setup_async_windows():
        """Configure async for Windows if needed"""
        if platform.system() == 'Windows':
            import asyncio
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Global instance
platform_info = PlatformInfo()

# Print platform info when imported (for debugging)
if __name__ == "__main__":
    info = platform_info.get_info()
    print("Platform Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print(f"\nProject Root: {PlatformInfo.get_project_root()}")
    print(f"Database Path: {PlatformInfo.get_database_path()}")

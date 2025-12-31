import os
import asyncio
import aiofiles
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class CookieConfig:
    cookies_file: str = "Alya/assets/cookies.txt"
    backup_dir: str = "Alya/assets/cookies_backup"
    validation_url: str = "https://www.youtube.com"

class YouTubeCookiesAPI:
    __slots__ = ("config", "_cookies_exist_cache")

    def __init__(self, config: Optional[CookieConfig] = None):
        self.config = config or CookieConfig()
        self._cookies_exist_cache: Optional[bool] = None
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure all necessary directories exist"""
        os.makedirs(os.path.dirname(self.config.cookies_file), exist_ok=True)
        os.makedirs(self.config.backup_dir, exist_ok=True)

    async def cookies_exist(self) -> bool:
        """Check if cookies file exists and has valid size (cached)"""
        if self._cookies_exist_cache is not None:
            return self._cookies_exist_cache

        try:
            if os.path.isfile(self.config.cookies_file):
                size = os.path.getsize(self.config.cookies_file)
                self._cookies_exist_cache = size > 100
                return self._cookies_exist_cache
            return False
        except OSError:
            return False

    async def validate_cookies(self, timeout: int = 5) -> bool:
        """Validate cookies quickly using yt-dlp subprocess (non-blocking, timeout)"""
        if not await self.cookies_exist():
            return False

        cmd = [
            "yt-dlp", "--cookies", self.config.cookies_file,
            "--skip-download", "--print", "title", self.config.validation_url
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )

            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                return False

            return proc.returncode == 0 and len(stdout) > 0
        except Exception:
            return False

    async def backup_cookies(self, backup_name: Optional[str] = None) -> str:
        """Backup current cookies (parallel async read/write)"""
        if not await self.cookies_exist():
            raise FileNotFoundError("No cookies file to backup")

        backup_name = backup_name or f"cookies_backup_{datetime.now():%Y%m%d_%H%M%S}.txt"
        backup_path = os.path.join(self.config.backup_dir, backup_name)

        async with aiofiles.open(self.config.cookies_file, "rb") as src, \
                   aiofiles.open(backup_path, "wb") as dst:
            await dst.write(await src.read())

        return backup_path

    async def restore_cookies(self, backup_name: str) -> bool:
        """Restore cookies from backup"""
        backup_path = os.path.join(self.config.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            return False

        async with aiofiles.open(backup_path, "rb") as src, \
                   aiofiles.open(self.config.cookies_file, "wb") as dst:
            await dst.write(await src.read())

        self._cookies_exist_cache = True
        return True

    async def list_backups(self) -> List[str]:
        """List all available cookie backups"""
        try:
            files = os.listdir(self.config.backup_dir)
            return sorted(
                (f for f in files if f.startswith("cookies_backup_") and f.endswith(".txt")),
                reverse=True
            )
        except FileNotFoundError:
            return []

    async def update_cookies(self, new_cookies: str) -> bool:
        """Update cookies safely and validate"""
        if not new_cookies.strip():
            return False

        try:
            await self.backup_cookies()
            async with aiofiles.open(self.config.cookies_file, "w") as f:
                await f.write(new_cookies.strip())

            self._cookies_exist_cache = True
            return await self.validate_cookies()
        except Exception:
            backups = await self.list_backups()
            if backups:
                await self.restore_cookies(backups[0])
            return False

    async def get_cookies_for_ydl(self) -> Dict[str, str]:
        """Return yt-dlp cookiefile argument"""
        return {"cookiefile": self.config.cookies_file} if await self.cookies_exist() else {}

    async def get_ydl_options(self, base: Optional[Dict] = None) -> Dict:
        """Combine yt-dlp options with cookies config"""
        opts = dict(base or {})
        opts.update(await self.get_cookies_for_ydl())
        return opts

    async def get_cli_args(self) -> List[str]:
        """Return yt-dlp CLI args if cookies exist"""
        return ["--cookies", self.config.cookies_file] if await self.cookies_exist() else []

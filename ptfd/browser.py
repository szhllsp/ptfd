import os
from playwright.sync_api import sync_playwright, Browser, BrowserContext

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class BrowserManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._playwright = None
            cls._instance._browser = None
        return cls._instance

    def get_context(self, platform: str) -> BrowserContext:
        if self._playwright is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=False)
        cookie_dir = os.path.join(DATA_DIR, "cookies")
        os.makedirs(cookie_dir, exist_ok=True)
        context = self._browser.new_context(
            storage_state=os.path.join(cookie_dir, f"{platform}.json")
            if os.path.exists(os.path.join(cookie_dir, f"{platform}.json"))
            else None
        )
        return context

    def save_context(self, context: BrowserContext, platform: str, close: bool = True):
        cookie_dir = os.path.join(DATA_DIR, "cookies")
        os.makedirs(cookie_dir, exist_ok=True)
        context.storage_state(path=os.path.join(cookie_dir, f"{platform}.json"))
        if close:
            context.close()

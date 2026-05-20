import time
from typing import Optional
from ptfd.adapters.base import BaseAdapter
from ptfd.browser import BrowserManager
from ptfd.cookie import get_cookie_path, has_cookie
from ptfd.models.schemas import Message, Comment, Stats


class ToutiaoAdapter(BaseAdapter):
    LOGIN_URL = "https://mp.toutiao.com"
    PUBLISH_URL = "https://mp.toutiao.com/profile_v4/graphic/publish"

    def __init__(self):
        self.browser = BrowserManager()

    def login(self):
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(self.LOGIN_URL)
        print("请在打开的浏览器中扫码登录头条号...")
        page.wait_for_url("https://mp.toutiao.com/profile_v4/**", timeout=120000)
        page.wait_for_selector('a[href*="toutiao.com/c/user"]', timeout=10000)
        print("登录成功！保存登录状态...")
        self.browser.save_context(context, "toutiao")

    def check_login(self) -> bool:
        if not has_cookie("toutiao"):
            return False
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(self.LOGIN_URL)
        try:
            page.wait_for_selector('a[href*="toutiao.com/c/user"]', timeout=5000)
            page.close()
            return True
        except:
            page.close()
            return False

    def publish(self, title: str, content: str, images: Optional[list] = None) -> str:
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(self.PUBLISH_URL)
        time.sleep(5)

        page.wait_for_selector('[placeholder*="标题"]', timeout=10000)
        page.fill('[placeholder*="标题"]', title)

        editor = page.wait_for_selector(".ProseMirror", timeout=10000)
        editor.evaluate("(el, html) => { el.innerHTML = html; el.dispatchEvent(new Event('input', { bubbles: true })); }", content)

        time.sleep(2)

        publish_btn = page.locator("button:has-text('预览并发布')")
        if publish_btn.is_visible():
            publish_btn.click()
            time.sleep(3)
            confirm_btn = page.locator("button:has-text('确认发布')")
            if confirm_btn.is_visible():
                confirm_btn.click()
                time.sleep(5)

        post_url = page.url
        page.close()
        return post_url

    def delete(self, post_id: str) -> bool:
        raise NotImplementedError

    def get_messages(self) -> list[Message]:
        raise NotImplementedError

    def get_comments(self, post_id: str) -> list[Comment]:
        raise NotImplementedError

    def reply_comment(self, comment_id: str, text: str) -> bool:
        raise NotImplementedError

    def get_stats(self, post_id: str) -> Stats:
        raise NotImplementedError

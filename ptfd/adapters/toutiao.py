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

    def list_articles(self) -> list[Stats]:
        """从管理页面获取所有文章及统计数据"""
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto("https://mp.toutiao.com/profile_v4/graphic/articles")
        time.sleep(5)

        articles = []
        rows = page.locator("table tbody tr, .article-table tbody tr, [class*='table'] tbody tr")
        count = rows.count()
        for i in range(count):
            row = rows.nth(i)
            cells = row.locator("td")
            if cells.count() < 4:
                continue
            post_id = row.get_attribute("data-id") or ""
            title = cells.nth(1).inner_text() if cells.count() > 1 else ""
            reads_text = cells.nth(3).inner_text() if cells.count() > 3 else "0"
            reads = 0
            for ch in reads_text.strip():
                if ch.isdigit():
                    reads = reads * 10 + int(ch)
            articles.append(Stats(
                post_id=post_id,
                views=0,
                reads=reads,
                likes=0,
                shares=0,
                platform="toutiao"
            ))
        page.close()
        return articles

    def delete(self, post_id: str) -> bool:
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto("https://mp.toutiao.com/profile_v4/graphic/articles")
        time.sleep(5)

        rows = page.locator("table tbody tr, .article-table tbody tr, [class*='table'] tbody tr")
        count = rows.count()
        found = False
        for i in range(count):
            row = rows.nth(i)
            rid = row.get_attribute("data-id") or ""
            if rid == post_id or post_id in row.inner_text():
                delete_btn = row.locator("button:has-text('删除'), span:has-text('删除'), a:has-text('删除')")
                if delete_btn.is_visible():
                    delete_btn.click()
                    time.sleep(2)
                    confirm_btn = page.locator("button:has-text('确认'), button:has-text('确定'), .confirm-btn")
                    if confirm_btn.is_visible():
                        confirm_btn.click()
                        time.sleep(3)
                    found = True
                break

        page.close()
        return found

    def get_stats(self, post_id: str) -> Stats:
        articles = self.list_articles()
        for a in articles:
            if a.post_id == post_id:
                return a
        return Stats(post_id=post_id, views=0, reads=0, likes=0, shares=0, platform="toutiao")

    def get_messages(self) -> list[Message]:
        raise NotImplementedError

    def get_comments(self, post_id: str) -> list[Comment]:
        raise NotImplementedError

    def reply_comment(self, comment_id: str, text: str) -> bool:
        raise NotImplementedError

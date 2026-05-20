import time
from typing import Optional
from ptfd.adapters.base import BaseAdapter
from ptfd.browser import BrowserManager
from ptfd.cookie import get_cookie_path, has_cookie
from ptfd.models.schemas import Message, Comment, Stats


class ToutiaoAdapter(BaseAdapter):
    LOGIN_URL = "https://mp.toutiao.com"
    PUBLISH_URL = "https://mp.toutiao.com/profile_v4/graphic/publish"
    MANAGE_URL = "https://mp.toutiao.com/profile_v4/graphic/articles"
    MESSAGES_URL = "https://mp.toutiao.com/creator-home/message"

    def __init__(self):
        self.browser = BrowserManager()

    def login(self):
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(self.LOGIN_URL)
        print("=" * 60)
        print("Chrome 浏览器已打开")
        print("请在弹出的窗口中完成扫码登录")
        print("登录后会显示管理后台页面，无需额外操作")
        print("等待中...（10 分钟内扫码即可，随时可按 Ctrl+C 终止）")
        print("=" * 60)

        import datetime
        deadline = datetime.datetime.now() + datetime.timedelta(minutes=10)
        last_url = ""
        while datetime.datetime.now() < deadline:
            try:
                url = page.url
                if url != last_url:
                    print(f"  当前页面: {url}")
                    last_url = url
                if not ("login" in url or "auth" in url or url == "about:blank" or url == self.LOGIN_URL + "/"):
                    print(f"检测到登录成功！")
                    break
            except:
                pass
            try:
                page.wait_for_url("**/profile_v4/**", timeout=3000)
                print("检测到登录成功！")
                break
            except:
                pass
            try:
                page.wait_for_url("**/creator-home/**", timeout=3000)
                print("检测到登录成功！")
                break
            except:
                pass

        print("保存登录状态...")
        self.browser.save_context(context, "toutiao", close=False)
        print("浏览器保持打开，你可以关闭它")

    def check_login(self) -> bool:
        if not has_cookie("toutiao"):
            return False
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(self.LOGIN_URL)
        try:
            page.wait_for_url("**/profile_v4/**", timeout=15000)
            page.close()
            return True
        except:
            pass
        try:
            page.wait_for_url("**/creator-home/**", timeout=5000)
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

    def _extract_articles_js(self) -> str:
        return """
() => {
  function parseNum(s) {
    if (!s) return 0;
    s = s.replace(/,/g, '');
    var m = s.match(/[\\d.]+/);
    if (!m) return 0;
    var val = parseFloat(m[0]);
    if (s.indexOf('\\u4e07') >= 0 || s.indexOf('w') >= 0) val *= 10000;
    return Math.round(val);
  }

  var links = document.querySelectorAll('a[href*=\"/item/\"]');
  var seen = {};
  var results = [];

  for (var i = 0; i < links.length; i++) {
    var a = links[i];
    var href = a.getAttribute('href') || '';
    var m = href.match(/\\/item\\/(\\d+)/);
    if (!m || seen[m[1]]) continue;
    seen[m[1]] = true;

    var row = a.closest('[class*=\"item\"], [class*=\"row\"], li, [class*=\"card\"], [class*=\"list\"]') || a.parentElement;
    var text = row ? (row.innerText || '') : (a.innerText || '');
    var title = (a.textContent || a.innerText || '').trim();

    var viewMatch = text.match(/\\u5c55\\u73b0[\\s\\uFF1A:]*([\\d.]+[\\u4e07w]?)/);
    var readMatch = text.match(/\\u9605\\u8bfb[\\s\\uFF1A:]*([\\d.]+[\\u4e07w]?)/);
    var commentMatch = text.match(/\\u8bc4\\u8bba[\\s\\uFF1A:]*([\\d.]+[\\u4e07w]?)/);

    results.push({
      post_id: m[1],
      title: title,
      reads: readMatch ? parseNum(readMatch[1]) : 0,
      views: viewMatch ? parseNum(viewMatch[1]) : 0,
      comments: commentMatch ? parseNum(commentMatch[1]) : 0
    });
  }
  return JSON.stringify(results);
}
"""

    def list_articles(self, page=None) -> list[Stats]:
        close_page = False
        if page is None:
            context = self.browser.get_context("toutiao")
            page = context.new_page()
            close_page = True

        page.goto(self.MANAGE_URL)
        # Wait for content to load (articles load via API)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass
        time.sleep(3)

        # Wait for article list to load
        try:
            page.wait_for_function("() => { const t = document.body.innerText; return (t.includes('展现') || t.includes('阅读')) && t.length > 500; }", timeout=20000)
        except:
            pass

        raw = page.evaluate(self._extract_articles_js())
        articles = []

        import json
        try:
            data = json.loads(raw)
        except:
            data = []

        # Check if we got stat data vs article data
        if data and "raw" in data[0]:
            print(f"页面统计数据片段: {[(d.get('raw',''), d.get('count',0)) for d in data[:10]]}")

        for item in data:
            if "post_id" not in item or not item.get("post_id"):
                continue
            articles.append(Stats(
                post_id=item.get("post_id", ""),
                title=item.get("title", ""),
                views=item.get("views", 0),
                reads=item.get("reads", 0),
                comments=item.get("comments", 0),
                platform="toutiao"
            ))

        if not articles:
            title = page.title() or ""
            body_len = page.evaluate("() => document.body.innerText.length")
            print(f"警告: 未找到文章 (页面标题: {title}, 页面文本长度: {body_len})")

        if close_page:
            page.close()
        return articles

    def delete(self, post_id: str, page=None) -> bool:
        close_page = False
        if page is None:
            context = self.browser.get_context("toutiao")
            page = context.new_page()
            close_page = True

        page.goto(self.MANAGE_URL)
        page.locator('a[href*="/item/"]').first.wait_for(timeout=15000)

        # Find the article link
        link = page.locator(f'a[href*="{post_id}"]')
        if link.count() == 0:
            if close_page: page.close()
            return False

        # Find the article card by walking up to the parent container
        card = link.first.locator('xpath=ancestor::*[contains(@class, "article-card") or contains(@class, "card-wrap")]')

        # Click "更多" button (last span in .article-action-list)
        more_btn = card.locator('.article-action-list span:last-child')
        if more_btn.count() == 0:
            if close_page: page.close()
            return False

        more_btn.first.click()
        time.sleep(2)

        # Click "删除作品" in the popover menu
        delete_btn = page.locator('text=删除作品')
        if delete_btn.count() == 0:
            if close_page: page.close()
            return False

        delete_btn.first.click()

        # Wait for confirmation modal
        confirm = page.locator('.byte-modal-footer .byte-btn-primary')
        confirm.first.wait_for(timeout=5000)
        confirm.first.click()

        # Wait for modal to disappear (deletion processed)
        page.locator('.byte-modal-mask').wait_for(state='hidden', timeout=10000)
        # Extra wait for server to process
        time.sleep(2)

        if close_page:
            page.close()
        return True

    def get_stats(self, post_id: str) -> Stats:
        articles = self.list_articles()
        for a in articles:
            if a.post_id == post_id:
                return a

        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(f"https://mp.toutiao.com/profile_v4/manage/content")
        time.sleep(5)

        stats = page.evaluate(f"""
() => {{
  const postId = {repr(post_id)};
  const links = document.querySelectorAll('a[href*="/item/" + postId]');
  for (const a of links) {{
    const row = a.closest('[class*="item"], [class*="row"], tr, li') || a.parentElement;
    if (!row) continue;
    const text = row.innerText || '';
    const reads = (text.match(/阅读[：:\\s]*([\\d,]+)/) || [])[1] || '0';
    const views = (text.match(/展现[：:\\s]*([\\d,]+)/) || [])[1] || '0';
    return {{ reads: parseInt(reads.replace(/,/g, '')), views: parseInt(views.replace(/,/g, '')) }};
  }}
  return null;
}}
""")

        page.close()

        if stats:
            return Stats(
                post_id=post_id,
                views=stats.get("views", 0),
                reads=stats.get("reads", 0),
                comments=stats.get("comments", 0),
                platform="toutiao"
            )

        return Stats(post_id=post_id, platform="toutiao")

    def get_messages(self) -> list[Message]:
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(self.MESSAGES_URL)
        time.sleep(5)

        raw = page.evaluate("""
() => {
  const results = [];
  const items = document.querySelectorAll('[class*="message-item"], [class*="msg-item"], [class*="notification"]');
  for (const item of items) {
    const text = item.innerText || '';
    const links = item.querySelectorAll('a');
    const fromEl = item.querySelector('[class*="from"], [class*="sender"], [class*="user"]');
    const fromUser = fromEl ? (fromEl.textContent || '').trim() : '';
    const content = text.substring(0, 200);
    results.push({
      id: item.getAttribute('data-id') || item.getAttribute('data-msg-id') || String(Math.random()),
      from_user: fromUser,
      content: content,
      time: new Date().toISOString(),
      platform: 'toutiao'
    });
  }
  return JSON.stringify(results);
}
""")

        import json
        try:
            data = json.loads(raw)
        except:
            data = []

        messages = []
        from datetime import datetime
        for item in data:
            messages.append(Message(
                id=item.get("id", ""),
                from_user=item.get("from_user", ""),
                content=item.get("content", ""),
                time=datetime.fromisoformat(item.get("time", datetime.now().isoformat())),
                platform=item.get("platform", "toutiao")
            ))

        page.close()
        return messages

    def get_comments(self, post_id: str) -> list[Comment]:
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(f"https://mp.toutiao.com/profile_v4/manage/comments")
        time.sleep(5)

        raw = page.evaluate(f"""
() => {{
  const results = [];
  const items = document.querySelectorAll('[class*="comment-item"], [class*="comment"], [class*="reply"]');
  for (const item of items) {{
    const text = item.innerText || '';
    const authorEl = item.querySelector('[class*="author"], [class*="user"], [class*="name"]');
    const author = authorEl ? (authorEl.textContent || '').trim() : '';
    results.push({{
      id: item.getAttribute('data-id') || item.getAttribute('data-comment-id') || String(Math.random()),
      post_id: {repr(post_id)},
      author: author,
      content: text.substring(0, 500),
      time: new Date().toISOString(),
      reply_count: 0
    }});
  }}
  return JSON.stringify(results);
}}
""")

        import json
        try:
            data = json.loads(raw)
        except:
            data = []

        comments = []
        from datetime import datetime
        for item in data:
            comments.append(Comment(
                id=item.get("id", ""),
                post_id=item.get("post_id", post_id),
                author=item.get("author", ""),
                content=item.get("content", ""),
                time=datetime.fromisoformat(item.get("time", datetime.now().isoformat())),
                reply_count=item.get("reply_count", 0)
            ))

        page.close()
        return comments

    def reply_comment(self, comment_id: str, text: str) -> bool:
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto("https://mp.toutiao.com/profile_v4/manage/comments")
        time.sleep(5)

        result = page.evaluate(f"""
() => {{
  const commentId = {repr(comment_id)};

  // Find the comment element
  let commentEl = document.querySelector('[data-id="{comment_id}"], [data-comment-id="{comment_id}"]');
  if (!commentEl) {{
    const items = document.querySelectorAll('[class*="comment-item"], [class*="comment"]');
    for (const item of items) {{
      if ((item.innerText || '').includes(commentId)) {{
        commentEl = item;
        break;
      }}
    }}
  }}

  if (!commentEl) return {{ success: false, reason: '未找到评论' }};

  // Click reply button
  const replyBtn = commentEl.querySelector('button:has-text("回复"), span:has-text("回复"), a:has-text("回复"), [class*="reply"]');
  if (replyBtn) {{
    replyBtn.click();
    return {{ success: true, action: 'clicked_reply' }};
  }}
  return {{ success: false, reason: '未找到回复按钮' }};
}}
""")

        if not result.get("success"):
            page.close()
            return False

        time.sleep(2)

        try:
            reply_input = page.wait_for_selector('[placeholder*="回复"], textarea, [contenteditable="true"]', timeout=5000)
            if reply_input:
                reply_input.fill(text)
                time.sleep(1)
                submit_btn = page.locator("button:has-text('发送'), button:has-text('提交'), button:has-text('回复')")
                if submit_btn.is_visible():
                    submit_btn.click()
                    time.sleep(2)
                    page.close()
                    return True
        except:
            pass

        page.close()
        return False

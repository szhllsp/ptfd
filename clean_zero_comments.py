"""登录头条号，删除评论数为 0 的文章（复用同一页面）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'F:\\ptfd')

from ptfd import PTFD
from ptfd.browser import BrowserManager

ptfd = PTFD()

if not ptfd.check_login("toutiao"):
    print("需要登录头条号...")
    ptfd.login("toutiao")

# 建一个页面，全程复用
browser = BrowserManager()
context = browser.get_context("toutiao")
page = context.new_page()

print("正在获取文章列表...")
articles = ptfd.list_articles("toutiao", page=page)

if not articles:
    print("没有找到文章")
    page.close()
    sys.exit(1)

to_delete = [a for a in articles if a.comments == 0]
print(f"共 {len(articles)} 篇文章，其中 {len(to_delete)} 篇评论数为 0")

for a in to_delete:
    print(f"  删除: 评论={a.comments} 阅读={a.reads} id={a.post_id}")
    if a.title:
        print(f"    标题: {a.title[:40]}")
    ok = ptfd.delete("toutiao", a.post_id, page=page)
    print(f"  {'OK' if ok else 'FAIL'}")

page.close()
print("完成！")

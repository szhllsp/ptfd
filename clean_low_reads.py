"""登录头条号，删除阅读量低于 1000 的文章"""
import sys
sys.path.insert(0, 'F:\\ptfd')

from ptfd import PTFD

ptfd = PTFD()

if not ptfd.check_login("toutiao"):
    print("需要登录头条号...")
    ptfd.login("toutiao")

print("正在获取文章列表...")
articles = ptfd.list_articles("toutiao")

if not articles:
    print("没有找到文章，请确认已登录且头条号有文章")
    sys.exit(1)

to_delete = [a for a in articles if a.reads < 1000]
print(f"共 {len(articles)} 篇文章，其中 {len(to_delete)} 篇阅读量低于 1000")

for a in to_delete:
    print(f"  删除: 阅读={a.reads} 评论={a.comments} id={a.post_id}")
    if a.title:
        print(f"    标题: {a.title[:40]}")
    ok = ptfd.delete("toutiao", a.post_id)
    print(f"  {'✓ 删除成功' if ok else '✗ 删除失败'}")

print("完成！")

"""登录头条号，删除阅读量低于 1000 的文章"""
from ptfd import PTFD

ptfd = PTFD()

if not ptfd.check_login("toutiao"):
    print("需要登录头条号...")
    ptfd.login("toutiao")

print("正在获取文章列表...")
articles = ptfd.list_articles("toutiao")

to_delete = [a for a in articles if a.reads < 1000]
print(f"共 {len(articles)} 篇文章，其中 {len(to_delete)} 篇阅读量低于 1000")

for a in to_delete:
    print(f"  删除: reads={a.reads}, post_id={a.post_id}")
    ptfd.delete("toutiao", a.post_id)

print("完成！")

import click
from ptfd import PTFD


ptfd = PTFD()


@click.group()
def main():
    """ptfd - 多平台内容发布与管理工具"""


@main.command()
@click.argument("platform", type=click.Choice(["toutiao", "baijiahao", "weixin"]))
def login(platform):
    """首次登录，打开浏览器扫码"""
    ptfd.login(platform)
    click.echo(f"{platform} 登录成功")


@main.command()
@click.argument("platform", type=click.Choice(["toutiao", "baijiahao", "weixin"]))
@click.option("-t", "--title", prompt=True, help="文章标题")
@click.option("-c", "--content", prompt=True, help="文章内容")
@click.option("-i", "--images", multiple=True, help="图片路径 (可多次使用)")
def publish(platform, title, content, images):
    """发布内容"""
    post_id = ptfd.publish(platform, title, content, list(images) or None)
    click.echo(f"发布成功: {post_id}")


@main.command("publish-micro")
@click.argument("platform", type=click.Choice(["toutiao"]))
@click.option("-c", "--content", prompt=True, help="微头条正文")
@click.option("-i", "--images", multiple=True, help="图片路径 (可多次使用)")
@click.option("--topic", multiple=True, help="话题 (可多次使用，如 --topic 话题1 --topic 话题2)")
@click.option("--declare-first", is_flag=True, help="勾选「声明首发」")
@click.option("--source-network", is_flag=True, help="作品声明：取材网络")
@click.option("--source-internal", is_flag=True, help="作品声明：引用站内")
@click.option("--personal-view", is_flag=True, help="作品声明：个人观点仅供参考")
def publish_micro(platform, content, images, topic, declare_first, source_network, source_internal, personal_view):
    """发布微头条（仅支持 toutiao）"""
    post_url = ptfd.publish_micro(
        platform, content,
        images=list(images) or None,
        topics=list(topic) or None,
        declare_first=declare_first,
        source_network=source_network,
        source_internal=source_internal,
        personal_view=personal_view,
    )
    click.echo(f"微头条发布成功: {post_url}")


@main.command()
@click.argument("platform", type=click.Choice(["toutiao", "baijiahao", "weixin"]))
@click.argument("post_id")
def delete(platform, post_id):
    """删除文章"""
    ok = ptfd.delete(platform, post_id)
    click.echo("删除成功" if ok else "删除失败")


@main.command()
@click.argument("platform", type=click.Choice(["toutiao", "baijiahao", "weixin"]))
def messages(platform):
    """查看消息列表"""
    msgs = ptfd.get_messages(platform)
    for m in msgs:
        click.echo(f"[{m.time}] {m.from_user}: {m.content}")


@main.command()
@click.argument("platform", type=click.Choice(["toutiao", "baijiahao", "weixin"]))
@click.argument("post_id")
def comments(platform, post_id):
    """查看评论"""
    cmts = ptfd.get_comments(platform, post_id)
    for c in cmts:
        click.echo(f"[{c.time}] {c.author}: {c.content}")


@main.command()
@click.argument("platform", type=click.Choice(["toutiao", "baijiahao", "weixin"]))
@click.argument("comment_id")
@click.argument("text")
def reply(platform, comment_id, text):
    """回复评论"""
    ok = ptfd.reply_comment(platform, comment_id, text)
    click.echo("回复成功" if ok else "回复失败")


@main.command()
@click.argument("platform", type=click.Choice(["toutiao", "baijiahao", "weixin"]))
@click.argument("post_id")
def stats(platform, post_id):
    """查看展示量/阅读量/评论数"""
    s = ptfd.get_stats(platform, post_id)
    click.echo(f"展示量: {s.views}")
    click.echo(f"阅读量: {s.reads}")
    click.echo(f"评论数: {s.comments}")
    click.echo(f"点赞: {s.likes}")
    click.echo(f"分享: {s.shares}")


if __name__ == "__main__":
    main()

# ptfd — 多平台内容发布与管理工具 设计文档

## 1. 概述

ptfd 是一个 CLI 命令行工具，支持在同一条内容发布到多个自媒体平台，并提供删除文章、查看消息/评论、回复评论、查看展示量/阅读量等功能。支持 OpenClaw 和 Hermes AI Agent 以 skill 方式集成。

## 2. 技术栈

| 组件 | 选择 | 理由 |
|------|------|------|
| 语言 | Python 3.10+ | 参考项目一致，Playwright 生态成熟 |
| 浏览器自动化 | Playwright | 跨平台可靠，支持 Cookie 持久化 |
| CLI 框架 | click | Python 主流 CLI 库，简洁 |
| 数据存储 | SQLite + JSON (Cookie) | 轻量，无需额外服务 |
| 打包 | pyproject.toml + setuptools | pip install 发布到 PyPI |
| 数据类 | pydantic | 结构化数据校验 |

## 3. 项目结构

```
F:\ptfd\
├── pyproject.toml              # 包配置，pip install ptfd
├── SKILL.md                    # OpenClaw / Hermes 共用 skill 描述
├── ptfd/
│   ├── __init__.py             # 导出 PTFD 类 (Hermes Python API)
│   ├── __main__.py             # python -m ptfd 入口
│   ├── cli.py                  # click 命令定义
│   ├── browser.py              # Playwright 浏览器单例管理
│   ├── cookie.py               # Cookie 持久化读写
│   ├── database.py             # SQLite 发布记录
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py             # BaseAdapter 抽象基类
│   │   ├── toutiao.py          # 今日头条适配器
│   │   ├── baijiahao.py        # 百度百家号适配器
│   │   └── weixin.py           # 微信公众号适配器
│   └── models/
│       ├── __init__.py
│       └── schemas.py          # Post, Comment, Message, Stats
└── data/                       # 运行期自动创建
    ├── cookies/                # 各平台 Cookie JSON
    └── database.db             # SQLite 数据库
```

## 4. CLI 命令设计

```
ptfd login <platform>             首次登录（浏览器扫码/账号）
ptfd publish <platform>           发布内容（从 stdin 或文件读取）
ptfd delete <platform> <id>       删除指定文章
ptfd messages <platform>          查看未读消息
ptfd comments <platform> <id>     查看文章评论
ptfd reply <platform> <cid> <txt> 回复评论
ptfd stats <platform> <id>        查看展示量/阅读量
ptfd ls                          列出所有已配置账号及状态
```

参数 `<platform>` 取值: `toutiao`, `baijiahao`, `weixin`

## 5. Python API 设计

```python
from ptfd import PTFD

ptfd = PTFD()

# 登录
ptfd.login("toutiao")                      # 打开浏览器手动登录

# 发布
post_id = ptfd.publish("toutiao", "标题", "内容", images=["1.jpg"])

# 删除
ptfd.delete("toutiao", post_id)

# 查询
messages = ptfd.get_messages("baijiahao")
comments = ptfd.get_comments("weixin", post_id)

# 回复
ptfd.reply_comment("toutiao", "comment_001", "感谢您的评论")

# 统计
stats = ptfd.get_stats("toutiao", post_id)
# stats.views, stats.reads
```

## 6. Adapter 体系

```
BaseAdapter (抽象基类)
├── login()                      → None (打开登录页，等待用户手动登录)
├── check_login()                → bool
├── publish(title, content, images) → str (post_id)
├── delete(post_id)              → bool
├── get_messages()               → list[Message]
├── get_comments(post_id)        → list[Comment]
├── reply_comment(comment_id, text) → bool
└── get_stats(post_id)           → Stats
```

每个 Adapter:
- 继承 `BaseAdapter`
- 实现 8 个接口方法
- 通过 Playwright 操作对应平台页面
- 首次 login 后自动 Cookie 持久化

## 7. 数据模型

```python
class Message:
    id: str
    from_user: str
    content: str
    time: datetime
    platform: str

class Comment:
    id: str
    post_id: str
    author: str
    content: str
    time: datetime
    reply_count: int

class Stats:
    post_id: str
    views: int       # 展示量
    reads: int       # 阅读量
    likes: int
    shares: int
    platform: str
```

## 8. Cookie 持久化

- 首次 `login()` → Playwright 打开登录页，用户手动登录
- 登录成功后导出 `context.storage_state()` 保存为 JSON
- 后续操作自动 `context.add_cookies()` 恢复会话
- Cookie 过期 / 失效时返回登录提示

## 9. OpenClaw / Hermes 集成

共用 `SKILL.md`，声明 permissions 和 inputs，两种 Agent 均原生支持：

```yaml
# SKILL.md (概略)
name: ptfd
description: 多平台内容发布管理工具
permissions:
  browser: true
  fileRead: true
  network: true
inputs:
  - platform   # 平台名
  - action     # publish/delete/messages/comments/reply/stats/login
  - title      # 发布时的标题
  - content    # 发布时的内容
```

OpenClaw: `openclaw skills install ptfd` 或直接调用 `ptfd publish ...`
Hermes: `pip install ptfd` → `from ptfd import PTFD`

## 10. 实施计划

### Phase 1: 基础框架
- pyproject.toml, CLI 入口, models
- Browser 管理 + Cookie 持久化
- 头条号 Adapter (login + publish)

### Phase 2: 平台功能完善
- 头条号: delete / messages / comments / reply / stats
- 百家号 Adapter 全套
- 微信公众号 Adapter 全套

### Phase 3: 集成与发布
- SKILL.md 编写
- PyPI 发布
- README + 使用文档

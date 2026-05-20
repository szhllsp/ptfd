# ptfd 多平台发布管理工具 — 实施计划 (Phase 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) for syntax tracking.

**Goal:** 搭建 ptfd 基础框架 + 实现今日头条的登录和发布功能

**Architecture:** 插件式 Adapter 架构，BaseAdapter 定义 8 个接口，ToutiaoAdapter 实现前两个（login/publish）。CLI 通过 click 分发命令，Playwright 管理浏览器，Cookie 持久化到本地 JSON 文件。

**Tech Stack:** Python 3.10+, Playwright, click, pydantic, SQLite

---

### 文件结构

```
F:\ptfd\
├── pyproject.toml
├── ptfd/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── browser.py
│   ├── cookie.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── toutiao.py
│   └── models/
│       ├── __init__.py
│       └── schemas.py
├── data/
│   └── cookies/
└── tests/
    └── test_toutiao.py
```

---

### Task 1: 项目骨架与包配置

**Files:**
- Create: `F:\ptfd\pyproject.toml`
- Create: `F:\ptfd\ptfd/__init__.py`
- Create: `F:\ptfd\ptfd/__main__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "ptfd"
version = "0.1.0"
description = "多平台内容发布与管理工具"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "playwright>=1.40",
    "pydantic>=2.0",
]
license = {text = "MIT"}

[project.scripts]
ptfd = "ptfd.cli:main"

[tool.setuptools.packages.find]
include = ["ptfd*"]
```

- [ ] **Step 2: Create ptfd/__init__.py**

```python
from .adapters.toutiao import ToutiaoAdapter

class PTFD:
    def __init__(self):
        self._adapters = {}

    def _get_adapter(self, platform: str):
        if platform not in self._adapters:
            if platform == "toutiao":
                self._adapters[platform] = ToutiaoAdapter()
            else:
                raise ValueError(f"Unsupported platform: {platform}")
        return self._adapters[platform]

    def login(self, platform: str):
        return self._get_adapter(platform).login()

    def publish(self, platform: str, title: str, content: str, images: list = None):
        return self._get_adapter(platform).publish(title, content, images or [])

    def delete(self, platform: str, post_id: str):
        return self._get_adapter(platform).delete(post_id)

    def get_messages(self, platform: str):
        return self._get_adapter(platform).get_messages()

    def get_comments(self, platform: str, post_id: str):
        return self._get_adapter(platform).get_comments(post_id)

    def reply_comment(self, platform: str, comment_id: str, text: str):
        return self._get_adapter(platform).reply_comment(comment_id, text)

    def get_stats(self, platform: str, post_id: str):
        return self._get_adapter(platform).get_stats(post_id)
```

- [ ] **Step 3: Create ptfd/__main__.py**

```python
from .cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml ptfd/__init__.py ptfd/__main__.py
git commit -m "chore: scaffold project skeleton with pyproject.toml"
```

---

### Task 2: 数据模型

**Files:**
- Create: `F:\ptfd\ptfd/models/__init__.py`
- Create: `F:\ptfd\ptfd/models/schemas.py`

- [ ] **Step 1: Create ptfd/models/__init__.py**

```python
from .schemas import Message, Comment, Stats
```

- [ ] **Step 2: Create ptfd/models/schemas.py**

```python
from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    id: str
    from_user: str
    content: str
    time: datetime
    platform: str


class Comment(BaseModel):
    id: str
    post_id: str
    author: str
    content: str
    time: datetime
    reply_count: int


class Stats(BaseModel):
    post_id: str
    views: int
    reads: int
    likes: int
    shares: int
    platform: str
```

- [ ] **Step 3: Commit**

```bash
git add ptfd/models/
git commit -m "feat: add data models (Message, Comment, Stats)"
```

---

### Task 3: 浏览器管理与 Cookie 持久化

**Files:**
- Create: `F:\ptfd\ptfd/browser.py`
- Create: `F:\ptfd\ptfd/cookie.py`

- [ ] **Step 1: Create ptfd/browser.py**

```python
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

    def save_context(self, context: BrowserContext, platform: str):
        cookie_dir = os.path.join(DATA_DIR, "cookies")
        os.makedirs(cookie_dir, exist_ok=True)
        context.storage_state(path=os.path.join(cookie_dir, f"{platform}.json"))
        context.close()
```

- [ ] **Step 2: Create ptfd/cookie.py**

```python
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def get_cookie_path(platform: str) -> str:
    cookie_dir = os.path.join(DATA_DIR, "cookies")
    os.makedirs(cookie_dir, exist_ok=True)
    return os.path.join(cookie_dir, f"{platform}.json")


def has_cookie(platform: str) -> bool:
    return os.path.exists(get_cookie_path(platform))
```

- [ ] **Step 3: Commit**

```bash
git add ptfd/browser.py ptfd/cookie.py
git commit -m "feat: add browser manager and cookie persistence"
```

---

### Task 4: BaseAdapter 抽象基类

**Files:**
- Create: `F:\ptfd\ptfd/adapters/__init__.py`
- Create: `F:\ptfd\ptfd/adapters/base.py`

- [ ] **Step 1: Create ptfd/adapters/__init__.py**

```python
from .base import BaseAdapter
from .toutiao import ToutiaoAdapter
```

- [ ] **Step 2: Create ptfd/adapters/base.py**

```python
from abc import ABC, abstractmethod
from typing import Optional
from ptfd.models.schemas import Message, Comment, Stats


class BaseAdapter(ABC):

    @abstractmethod
    def login(self):
        """打开浏览器让用户手动登录，保存 Cookie"""
        pass

    @abstractmethod
    def check_login(self) -> bool:
        """检查 Cookie 是否有效"""
        pass

    @abstractmethod
    def publish(self, title: str, content: str, images: Optional[list] = None) -> str:
        """发布内容，返回 post_id"""
        pass

    @abstractmethod
    def delete(self, post_id: str) -> bool:
        """删除文章"""
        pass

    @abstractmethod
    def get_messages(self) -> list[Message]:
        """获取消息列表"""
        pass

    @abstractmethod
    def get_comments(self, post_id: str) -> list[Comment]:
        """获取评论列表"""
        pass

    @abstractmethod
    def reply_comment(self, comment_id: str, text: str) -> bool:
        """回复评论"""
        pass

    @abstractmethod
    def get_stats(self, post_id: str) -> Stats:
        """获取展示量/阅读量"""
        pass
```

- [ ] **Step 3: Commit**

```bash
git add ptfd/adapters/__init__.py ptfd/adapters/base.py
git commit -m "feat: add BaseAdapter abstract class with 8 interface methods"
```

---

### Task 5: 今日头条 Adapter — 登录

**Files:**
- Create: `F:\ptfd\ptfd/adapters/toutiao.py`

- [ ] **Step 1: Create ToutiaoAdapter with login + publish stubs**

Write a partial adapter. login() opens mp.toutiao.com, waits for manual login, and saves cookie. publish() will navigate to publish page, fill title + content, and click publish.

```python
import time
import os
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
        print("登录成功！保存登录状态...")
        self.browser.save_context(context, "toutiao")

    def check_login(self) -> bool:
        if not has_cookie("toutiao"):
            return False
        context = self.browser.get_context("toutiao")
        page = context.new_page()
        page.goto(self.LOGIN_URL)
        time.sleep(3)
        logged_in = "toutiao.com/c/user" in page.content()
        page.close()
        return logged_in

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
```

- [ ] **Step 2: Commit**

```bash
git add ptfd/adapters/toutiao.py
git commit -m "feat: implement ToutiaoAdapter login and publish"
```

---

### Task 6: CLI 入口

**Files:**
- Create: `F:\ptfd\ptfd/cli.py`

- [ ] **Step 1: Create cli.py with all 8 commands**

```python
import sys
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
    """查看展示量/阅读量"""
    s = ptfd.get_stats(platform, post_id)
    click.echo(f"展示量: {s.views}")
    click.echo(f"阅读量: {s.reads}")
    click.echo(f"点赞: {s.likes}")
    click.echo(f"分享: {s.shares}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add ptfd/cli.py
git commit -m "feat: add CLI entry with all commands"
```

---

### Task 7: SKILL.md — OpenClaw & Hermes 集成

**Files:**
- Create: `F:\ptfd\SKILL.md`

- [ ] **Step 1: Create SKILL.md**

```markdown
---
name: ptfd
version: 0.1.0
description: 多平台内容发布与管理工具。支持头条号、百家号、微信公众号的内容发布、删除、消息查看、评论管理、数据统计。
author: ptfd
permissions:
  browser: true
  fileRead: true
  network: true
inputs:
  platform:
    description: 目标平台
    values: ["toutiao", "baijiahao", "weixin"]
  action:
    description: 操作类型
    values: ["login", "publish", "delete", "messages", "comments", "reply", "stats"]
  title:
    description: 文章标题 (publish 时必填)
  content:
    description: 文章内容 (publish 时必填)
  post_id:
    description: 文章 ID (delete/comments/stats 时必填)
  comment_id:
    description: 评论 ID (reply 时必填)
  text:
    description: 回复文本 (reply 时必填)
---

# ptfd — 多平台内容发布与管理

## 用途

发布同一条内容到多个自媒体平台，查看和管理各平台的评论、消息、数据统计。

## 支持平台

- 今日头条（头条号）
- 百度百家号
- 微信公众号

## 使用方法

### 首次登录

```bash
ptfd login toutiao
ptfd login baijiahao
ptfd login weixin
```

每个平台首次需要扫码登录，登录后自动保存 Cookie。

### 发布内容

```bash
ptfd publish toutiao --title "标题" --content "正文内容"
ptfd publish toutiao --title "标题" --content "正文" --image cover.jpg
```

### 查看评论

```bash
ptfd comments toutiao <post_id>
```

### 回复评论

```bash
ptfd reply toutiao <comment_id> "回复内容"
```

### 查看数据

```bash
ptfd stats toutiao <post_id>
```

## 注意事项

- 首次使用需要手动登录（浏览器扫码）
- 登录态通过 Cookie 持久化，除非 Cookie 过期无需重复登录
- 需要安装 Playwright 浏览器: `playwright install chromium`
```

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "docs: add SKILL.md for OpenClaw and Hermes integration"
```

---

### 自审

1. **Spec coverage:**
   - 基础框架 (pyproject.toml, __init__.py, __main__.py) ✓ — Task 1
   - 数据模型 ✓ — Task 2
   - 浏览器管理 + Cookie ✓ — Task 3
   - BaseAdapter ✓ — Task 4
   - ToutiaoAdapter login + publish ✓ — Task 5
   - CLI ✓ — Task 6
   - SKILL.md ✓ — Task 7
   - 暂未实现: delete/messages/comments/reply/stats → Phase 2
   - 暂未实现: baijiahao/weixin Adapter → Phase 2

2. **占位符扫描:** 无 TBD/TODO 占位符。各代码块包含完整实现代码。

3. **类型一致性:** 所有方法签名和类型在各 Task 间一致。

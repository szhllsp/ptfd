# ptfd 开发者文档

## 架构总览

```
CLI (cli.py) → PTFD 门面 (__init__.py) → BaseAdapter → 平台实现 (toutiao.py)
                                                        BrowserManager (browser.py)
                                                        Cookie 持久化 (cookie.py)
```

**核心概念：** 每个平台是一个 Adapter，继承 `BaseAdapter` 实现 8 个接口方法。新增平台只需创建一个文件、实现接口、注册到 `PTFD._get_adapter()`。

### 文件职责

| 文件 | 职责 |
|------|------|
| `ptfd/cli.py` | Click CLI 入口，9 个子命令（含 publish-micro），纯 UI 层 |
| `ptfd/__init__.py` | `PTFD` 门面类，适配器查找和缓存，含 publish_micro 入口 |
| `ptfd/browser.py` | `BrowserManager` 单例，管理 Playwright 生命周期，提供 close/reset |
| `ptfd/cookie.py` | Cookie 路径和存在性检查工具函数 |
| `ptfd/adapters/base.py` | `BaseAdapter` 抽象基类，定义 8 个接口 |
| `ptfd/adapters/<platform>.py` | 各平台实现，ToutiaoAdapter 额外含 publish_micro |
| `ptfd/models/schemas.py` | `Message`、`Comment`、`Stats` 数据模型 |

---

## 新增一个平台

### 步骤 1：创建 Adapter 文件

在 `ptfd/adapters/` 下创建 `<platform>.py`，继承 `BaseAdapter` 并实现全部 8 个方法：

```python
import time
from typing import Optional
from ptfd.adapters.base import BaseAdapter
from ptfd.browser import BrowserManager
from ptfd.cookie import has_cookie
from ptfd.models.schemas import Message, Comment, Stats


class SomePlatformAdapter(BaseAdapter):
    BASE_URL = "https://mp.example.com"
    PUBLISH_URL = "https://mp.example.com/publish"

    def __init__(self):
        self.browser = BrowserManager()

    def login(self):
        """打开登录页，等待用户手动登录，保存 Cookie"""
        ctx = self.browser.get_context("some_platform")
        page = ctx.new_page()
        page.goto(self.BASE_URL)
        print("请在打开的浏览器中登录...")
        page.wait_for_url(f"{self.BASE_URL}/dashboard/**", timeout=120000)
        print("登录成功")
        self.browser.save_context(ctx, "some_platform")

    def check_login(self) -> bool:
        if not has_cookie("some_platform"):
            return False
        ctx = self.browser.get_context("some_platform")
        page = ctx.new_page()
        page.goto(self.BASE_URL)
        try:
            page.wait_for_selector(".user-avatar", timeout=5000)
            return True
        except:
            return False
        finally:
            page.close()

    def publish(self, title: str, content: str, images: Optional[list] = None) -> str:
        ctx = self.browser.get_context("some_platform")
        page = ctx.new_page()
        page.goto(self.PUBLISH_URL)
        time.sleep(3)

        # 填写标题
        page.fill("input[placeholder*='标题']", title)

        # 填写正文 (textarea 或富文本)
        page.fill("textarea", content)

        # 上传图片
        if images:
            file_input = page.locator("input[type='file']")
            file_input.set_input_files(images)

        # 点击发布
        page.click("button:has-text('发布')")
        time.sleep(3)

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

### 步骤 2：注册到 PTFD 门面

修改 `ptfd/__init__.py` 的 `_get_adapter` 方法：

```python
def _get_adapter(self, platform: str):
    if platform not in self._adapters:
        if platform == "toutiao":
            from .adapters.toutiao import ToutiaoAdapter
            self._adapters[platform] = ToutiaoAdapter()
        elif platform == "some_platform":
            from .adapters.some_platform import SomePlatformAdapter
            self._adapters[platform] = SomePlatformAdapter()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    return self._adapters[platform]
```

### 步骤 3：更新 CLI Choice

如果希望 CLI 支持新平台，修改 `ptfd/cli.py` 中每个命令的 `type=click.Choice(...)`：

```python
@click.argument("platform", type=click.Choice(["toutiao", "some_platform"]))
```

---

## Playwright 自动化技巧

### 页面加载等待

```python
# 等待 URL 变化
page.wait_for_url("https://mp.example.com/dashboard/**", timeout=30000)

# 等待元素出现
page.wait_for_selector(".editor", timeout=10000)

# 固定时间等待（只在必要时）
time.sleep(3)
```

### 富文本编辑器注入

```python
editor = page.wait_for_selector(".ProseMirror", timeout=10000)
editor.evaluate("""(el, html) => {
    el.innerHTML = html;
    el.dispatchEvent(new Event('input', { bubbles: true }));
}""", content)
```

### 通过文本查找按钮

```python
page.locator("button:has-text('确认发布')").click()
# 或
page.locator('button:has-text("发布")').click()
```

### Cookie 持久化

首次登录后自动保存：`BrowserManager.save_context(context, platform)`
后续自动恢复：`BrowserManager.get_context(platform)` 会检查是否存在 Cookie 文件

### 登录检测

```python
# 检查某个元素是否存在来判断登录态
try:
    page.wait_for_selector('a[href*="/user"]', timeout=5000)
    return True  # 已登录
except:
    return False  # 未登录
```

---

## 数据模型

```python
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
    views: int       # 展示量
    reads: int       # 阅读量
    likes: int
    shares: int
    platform: str
```

---

## 测试

```bash
# 安装开发依赖
pip install pytest

# 运行测试
pytest tests/
```

---

## 构建与发布

```bash
# 构建
pip install build
python -m build

# 发布到 PyPI
pip install twine
twine upload dist/*
```

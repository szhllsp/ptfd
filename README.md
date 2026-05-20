# ptfd — 多平台内容发布与管理工具

一键发布、管理头条号等自媒体平台的内容，查看和回复评论，查看数据统计。

## 安装

```bash
cd F:\ptfd
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m playwright install chromium
```

或者直接运行（自动使用独立环境）：
```bash
.venv\Scripts\python -m ptfd --help
```

## 快速开始

```bash
# 首次登录（会打开浏览器扫码）
.venv\Scripts\python -m ptfd login toutiao

# 发布内容
.venv\Scripts\python -m ptfd publish toutiao -t "标题" -c "正文"

# 查看消息
.venv\Scripts\python -m ptfd messages toutiao

# 查看评论
.venv\Scripts\python -m ptfd comments toutiao <文章ID>

# 回复评论
.venv\Scripts\python -m ptfd reply toutiao <评论ID> "回复内容"

# 查看展示量/阅读量
.venv\Scripts\python -m ptfd stats toutiao <文章ID>

# 删除文章
.venv\Scripts\python -m ptfd delete toutiao <文章ID>

# 删除阅读量低于 1000 的文章
.venv\Scripts\python clean_low_reads.py
```

## 功能

- 登录（浏览器扫码，Cookie 持久化）
- 发布图文内容
- 删除文章
- 查看消息通知
- 查看和回复评论
- 查看展示量、阅读量等数据
- 批量删除低阅读量文章

## 支持平台

- 今日头条（头条号）✅
- 百度百家号（开发中）
- 微信公众号（开发中）

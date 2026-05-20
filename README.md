# ptfd — 多平台内容发布与管理工具

发布同一条内容到多个自媒体平台，管理评论、消息、数据统计。

## 安装

```bash
pip install ptfd
playwright install chromium
```

## 快速开始

```bash
# 首次登录
ptfd login toutiao

# 发布内容
ptfd publish toutiao --title "标题" --content "正文"
```

## 支持平台

- 今日头条（头条号）
- 百度百家号（开发中）
- 微信公众号（开发中）

## OpenClaw / Hermes 集成

本工具提供 SKILL.md，OpenClaw 和 Hermes AI Agent 均可直接调用安装。

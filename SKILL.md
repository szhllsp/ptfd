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
    values: ["login", "publish", "publish-micro", "delete", "messages", "comments", "reply", "stats"]
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

### 发布微头条（仅头条号）

```bash
ptfd publish-micro toutiao -c "正文" -i 图片.jpg \
  --topic 关键词 --declare-first \
  --source-network --source-internal --personal-view
```

- `--topic` 可多次使用，自动搜索热度最高的前 2 个话题添加
- `--declare-first` 勾选「声明首发」
- `--source-network` / `--source-internal` / `--personal-view` 勾选作品声明

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

# xiaohongshu-mcp Bug 追踪

**创建时间：** 2026-03-11 02:20  
**状态：** 🟡 等待修复

---

## 🐛 Bug 描述

### Bug 1: MCP 协议会话初始化问题

**错误信息：**
```
method "tools/call" is invalid during session initialization
```

**表现：**
- 初始化成功（返回 200）
- 发送 initialized 通知（返回 202）
- 调用任何工具（tools/list, tools/call）都失败
- 错误始终是"invalid during session initialization"

**影响：**
- ❌ 无法通过 MCP 协议调用任何功能
- ❌ 无法发布内容
- ❌ 无法搜索笔记
- ❌ 无法获取推荐列表

**已尝试方案：**
1. ❌ 正确的 Accept 头（`application/json,text/event-stream`）
2. ❌ 等待更长时间（5 秒）
3. ❌ 先调用简单工具（check_login_status）
4. ❌ 使用 HTTP 图片链接
5. ❌ 使用本地图片路径

**根本原因：**
- xiaohongshu-mcp Docker 容器的会话管理实现有 bug
- 即使初始化成功，也认为还在"session initialization"阶段

**修复建议：**
- 需要修复 Docker 容器中的会话状态管理
- 或者更新 xiaohongshu-mcp 到最新版本

---

### Bug 2: 图片上传超时

**错误信息：**
```
UploadTimeoutError: 第 1 张图片上传超时 (60s)
```

**表现：**
- 登录成功
- 导航到发布页面成功
- 图片上传超时（60 秒限制）
- 无论图片大小（1.6MB → 0.25MB → 0.06MB）都超时

**影响：**
- ❌ 无法发布图文内容
- ❌ xiaohongshu-mcp-skills 无法使用

**已尝试方案：**
1. ❌ 原图（1.6MB, 3840x2160）
2. ❌ 压缩图（0.25MB, 1080x608）
3. ❌ 小图（0.06MB, 600x338）
4. ❌ 多次尝试

**可能原因：**
- 小红书图片上传服务器响应慢
- 网络连接问题
- 浏览器自动化不稳定
- 小红书反爬虫机制

**修复建议：**
- 增加上传超时时间（60s → 180s）
- 或者使用 HTTP 图片链接方式
- 或者检查网络连接

---

## 📊 影响评估

| 功能 | 状态 | 替代方案 |
|------|------|----------|
| MCP 协议调用 | ❌ 不可用 | 手动发布 |
| 图片上传 | ❌ 超时 | 手动发布 |
| 登录状态 | ✅ 正常 | - |
| 扫码登录 | ✅ 正常 | - |

---

## 🔍 相关项目

| 项目 | 状态 | 说明 |
|------|------|------|
| [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) | 🟡 有 bug | Docker 容器版本 |
| [xiaohongshu-mcp-skills](https://github.com/autoclaw-cc/xiaohongshu-mcp-skills) | 🟡 依赖 MCP | OpenClaw Skills |
| [xiaohongshu-skills](https://github.com/autoclaw-cc/xiaohongshu-skills) | 🟡 依赖 MCP | 开箱即用版 |
| [x-mcp](https://github.com/xpzouying/x-mcp) | ✅ 推荐 | 浏览器插件版（零配置） |

---

## 💡 临时解决方案

### 方案 1: 手动发布（推荐）⭐
- 打开小红书 APP
- 选择图片
- 粘贴标题和正文
- 发布

### 方案 2: 使用 x-mcp 插件版
- 安装浏览器插件
- 零配置
- 可能更稳定

### 方案 3: 等待修复
- 关注 GitHub Issues
- 等待官方修复

---

## 📝 待办事项

- [ ] 关注 GitHub Issues 更新
- [ ] 检查是否有新版本发布
- [ ] 尝试 x-mcp 插件版
- [ ] 或者手动发布

---

**最后更新：** 2026-03-11 02:20

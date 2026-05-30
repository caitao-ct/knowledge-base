# MCP Server API 文档

## 概述

MCP RAG Server 提供语义搜索知识库的功能，供 AI Agent（如 Codex、Claude）接入使用。

## 传输协议

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `stdio` | 标准输入输出，适合本地进程调用 | Claude Desktop, Codex |
| `http` | HTTP REST API，适合远程调用 | Web 服务 |
| `sse` | Server-Sent Events，适合流式响应 | 需要实时推送的场景 |

## 启动参数

| 参数 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `--kb-dir` | `KB_DIR` | `./docs` | 知识库文档目录 |
| `--chroma-dir` | `CHROMA_DIR` | `.chroma` | ChromaDB 持久化目录 |
| `--collection` | `CHROMA_COLLECTION` | `knowledge` | 向量集合名称 |
| `--embed-model` | `EMBED_MODEL` | `BAAI/bge-small-zh-v1.5` | 嵌入模型 |
| `--index-on-startup` | `INDEX_ON_STARTUP` | `true` | 启动时是否建立索引 |
| `--transport` | `MCP_TRANSPORT` | `stdio` | 传输协议 |
| `--host` | `MCP_HOST` | `127.0.0.1` | HTTP 服务地址 |
| `--port` | `MCP_PORT` | `8000` | HTTP 服务端口 |
| `--token` | `MCP_TOKEN` | - | 认证 Token |

## 工具 (Tools)

### search_knowledge

语义搜索最相关的知识片段。

**参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 搜索关键词 |
| `top_k` | integer | 否 | 返回结果数，默认 5 |
| `format` | string | 否 | 返回格式：`markdown`（默认）或 `json` |

**返回示例（markdown）：**

```markdown
### [UI组件/Button.md] Button 按钮

## Button 按钮

用于触发操作的交互元素...

---
### [编码规范/vue-style-guide.md] Vue 风格指南

## Vue 风格指南

1. 组件名使用 PascalCase...
```

---

### get_document

获取完整文档内容。

**参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | 是 | 文档相对路径，如 `UI组件/Button.md` |

**返回：** 文档完整内容（Markdown 格式）

**错误响应：** `非法路径` 或 `文件不存在: <path>`

---

### refresh_index

触发知识库增量同步。

**参数：** 无

**返回：**

```json
{
  "ok": true,
  "stats": {
    "files_added": 1,
    "files_updated": 0,
    "files_removed": 0
  }
}
```

---

## 资源 (Resources)

知识库中的 Markdown 文档以 `kb://` 协议暴露。

**URI 格式：** `kb:///<相对路径>`

**示例：**
- `kb:///UI组件/Button.md`
- `kb:///业务场景/订单流程.md`

---

## 提示 (Prompts)

### kb_search_and_cite

指导 Agent 如何检索、引用、溯源知识库内容。

**参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task` | string | 是 | 当前要解决的任务 |

---

## 安全配置

### Token 认证

HTTP/SSE 模式支持三种 Token 验证方式：

1. **Authorization Header（推荐）**
   ```
   Authorization: Bearer <token>
   ```

2. **X-MCP-Token Header**
   ```
   X-MCP-Token: <token>
   ```

3. **Query Parameter（仅当 token 已设置时）**
   ```
   ?token=<token>
   ```

**注意：** 生产环境请通过 HTTPS 部署，防止 Token 在传输过程中被截获。

---

## 环境变量示例

```bash
# MCP Server
export KB_DIR="./docs"
export CHROMA_DIR="/path/to/.chroma"
export MCP_TRANSPORT="stdio"
export MCP_TOKEN="your-secret-token"

# HuggingFace（国内镜像）
export HF_ENDPOINT="https://hf-mirror.com"
```

---

## 客户端配置示例

### Claude Desktop (stdio)

```json
{
  "mcpServers": {
    "frontend-knowledge": {
      "command": "bash",
      "args": ["-lc", "cd /path/to/knowledge && ./bin/knowledge-mcp --transport stdio"],
      "env": {
        "KB_DIR": "./docs"
      }
    }
  }
}
```

### HTTP 模式（cURL）

```bash
curl -X POST http://localhost:8000/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```
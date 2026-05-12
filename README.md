# 知识库 (Knowledge Base) & MCP Server

这是一个双用途的知识库项目：它既是一个美观的 **VitePress 文档站点**，也是一个功能强大的 **MCP (Model Context Protocol) 资料库**。你可以通过它来沉淀团队知识，并无缝接入 AI Agent（如 Codex、Claude、Cursor）来辅助开发。

---

## 🚀 核心特性

- **双向使用**：支持人工在线查阅（VitePress）与 AI Agent 语义检索（MCP RAG）。
- **语义搜索**：集成 ChromaDB 向量数据库，支持基于语义而非关键词的知识召回。
- **通用接入**：支持 stdio、HTTP、SSE 三种传输协议，兼容所有主流 MCP 客户端。
- **增量索引**：自动追踪文件变更，仅对更新内容进行索引，高效稳定。
- **安全加固**：内置路径校验，防止路径穿越风险。

---

## 📂 项目结构

```text
.
├── bin/
│   └── knowledge-mcp      # MCP 服务启动脚本 (推荐入口)
├── docs/
│   ├── 业务场景/          # 业务规则、流程文档
│   ├── UI组件/            # 前端组件 API 与用法
│   ├── 编码规范/          # 团队代码风格指南
│   └── .vitepress/        # VitePress 站点配置与构建产物
├── mcp-server/
│   ├── server.py          # MCP RAG 服务核心逻辑
│   ├── requirements.txt   # Python 依赖声明
│   └── examples/          # 客户端配置示例
├── MAINTENANCE.md         # 详细的知识库维护手册
└── README.md              # 项目主说明文档
```

---

## 🛠️ 快速上手

### 1. 环境准备
确保你的系统中安装了 Node.js 和 Python 3.10+。

### 2. 安装依赖
```bash
# 安装前端文档站依赖
npm install

# 安装 MCP Server 依赖
cd mcp-server
pip install -r requirements.txt
```

### 3. 运行文档站 (人工查阅)
```bash
npm run docs:dev
```
访问 `http://localhost:5173` 即可实时预览文档。

### 4. 启动 MCP 服务 (Agent 接入)
使用根目录的脚本启动：
```bash
# 默认 stdio 模式启动
./bin/knowledge-mcp

# 以 HTTP 模式启动并开启安全验证
./bin/knowledge-mcp --transport http --port 8000 --token my-secret-token
```

---

## 🤖 Agent 接入指南

### 接入 Codex / Claude Desktop
在你的 MCP 配置文件中添加如下片段：

```json
{
  "mcpServers": {
    "frontend-knowledge": {
      "command": "bash",
      "args": ["-lc", "cd /path/to/project && ./bin/knowledge-mcp --transport stdio"],
      "env": {
        "KB_DIR": "./docs"
      }
    }
  }
}
```

### 可用工具 (Tools)
- `search_knowledge`: 语义搜索最相关的知识片段。
- `get_document`: 获取指定路径的完整 Markdown 文档。
- `refresh_index`: 触发知识库增量同步。

---

## 📝 维护说明

为了保证 Agent 检索的准确性，请在编写文档时遵循以下规范：
1. **二级标题分块**：MCP Server 按 `##` 标题切分内容，请确保每个二级标题下的内容完整且独立。
2. **刷新索引**：新增或修改文档后，需重启服务或让 Agent 调用 `refresh_index`。

更多细节请参阅：[MAINTENANCE.md](file:///Users/caitao/work/knowledge/MAINTENANCE.md)。

---

## 📜 许可证
[MIT License]

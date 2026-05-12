# knowledge MCP server

## 能力

- Tools
  - search_knowledge(query, top_k=5, format=markdown|json)
  - get_document(path)
  - refresh_index()
- Resources
  - kb:///相对路径.md
- Prompts
  - kb_search_and_cite(task)

## 启动

### stdio（默认）

```bash
python server.py
```

### HTTP（streamable HTTP）

```bash
python server.py --transport http --host 127.0.0.1 --port 8000
```

### SSE

```bash
python server.py --transport sse --host 127.0.0.1 --port 8000
```

## 配置

启动参数可用环境变量覆盖：

- KB_DIR
- CHROMA_DIR
- CHROMA_COLLECTION
- EMBED_MODEL
- INDEX_ON_STARTUP
- MCP_TRANSPORT
- MCP_HOST
- MCP_PORT
- MCP_TOKEN


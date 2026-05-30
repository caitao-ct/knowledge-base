"""
MCP RAG Server — 知识库语义搜索
用法: python server.py
"""
import os
import glob
import json
import asyncio
import argparse
import hashlib
import signal
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from mcp.server import Server
from mcp.server.models import InitializationOptions

# ── 配置 ──
REPO_DIR = Path(__file__).resolve().parent.parent
DEFAULT_KB_DIR = (REPO_DIR / "docs").as_posix()
DEFAULT_CHROMA_DIR = (Path(__file__).resolve().parent / ".chroma").as_posix()
DEFAULT_COLLECTION = "knowledge"
DEFAULT_EMBED_MODEL = "BAAI/bge-small-zh-v1.5"
DEFAULT_INDEX_ON_STARTUP = True

# 资源列表缓存 TTL（秒），0 表示禁用缓存
RESOURCE_CACHE_TTL = 300

# 操作超时（秒）
EMBED_TIMEOUT = 30
INDEX_TIMEOUT = 300

# 常量
SCHEME_KB = "kb"
METADATA_HNSW_SPACE = "cosine"
METADATA_HNSW_KEY = "hnsw:space"

# HuggingFace 国内镜像
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

def parse_args():
    parser = argparse.ArgumentParser(prog="knowledge-mcp")
    parser.add_argument("--kb-dir", default=os.environ.get("KB_DIR", DEFAULT_KB_DIR))
    parser.add_argument("--chroma-dir", default=os.environ.get("CHROMA_DIR", DEFAULT_CHROMA_DIR))
    parser.add_argument("--collection", default=os.environ.get("CHROMA_COLLECTION", DEFAULT_COLLECTION))
    parser.add_argument("--embed-model", default=os.environ.get("EMBED_MODEL", DEFAULT_EMBED_MODEL))
    parser.add_argument("--index-on-startup", action=argparse.BooleanOptionalAction, default=os.environ.get("INDEX_ON_STARTUP", "").strip().lower() not in {"0", "false", "no"} if os.environ.get("INDEX_ON_STARTUP") is not None else DEFAULT_INDEX_ON_STARTUP)
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default=os.environ.get("MCP_TRANSPORT", "stdio"))
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MCP_PORT", "8000")))
    parser.add_argument("--token", default=os.environ.get("MCP_TOKEN"))
    return parser.parse_args()


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def safe_join(base_dir: str, user_path: str) -> Path:
    """
    安全地拼接 base_dir 和 user_path，防止路径穿越攻击。
    使用 Path.resolve() 获取绝对路径并解析 symlink。
    """
    base = Path(base_dir).resolve()
    # 防止空路径或绝对路径穿越
    clean_path = user_path.lstrip("/")
    candidate = (base / clean_path).resolve()
    # 检查 candidate 是否在 base 目录内
    try:
        candidate.relative_to(base)
    except ValueError:
        raise ValueError("Invalid path: 路径穿越检测")
    return candidate


class KnowledgeIndex:
    def __init__(self, kb_dir: str, chroma_dir: str, collection: str, embed_model: str):
        self.kb_dir = os.path.expanduser(kb_dir)
        self.chroma_dir = os.path.expanduser(chroma_dir)
        self.collection_name = collection
        self.embed_model = embed_model
        Path(self.chroma_dir).mkdir(parents=True, exist_ok=True)
        self.chroma = chromadb.PersistentClient(path=self.chroma_dir)
        self.model = SentenceTransformer(self.embed_model)

    @property
    def state_path(self) -> Path:
        return Path(self.chroma_dir) / "index_state.json"

    def load_state(self) -> dict:
        if not self.state_path.exists():
            return {"files": {}}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"files": {}}

    def save_state(self, state: dict) -> None:
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.state_path)

    def get_collection(self):
        return self.chroma.get_or_create_collection(
            self.collection_name,
            metadata={METADATA_HNSW_KEY: METADATA_HNSW_SPACE},
        )

    def chunk_markdown(self, text: str, source: str) -> list[dict]:
        lines = text.split("\n")
        chunks = []
        current_title = "概述"
        current_lines = []
        for line in lines:
            if line.startswith("## "):
                if current_lines:
                    chunks.append(
                        {
                            "content": "\n".join(current_lines).strip(),
                            "title": current_title,
                            "source": source,
                        }
                    )
                current_title = line.strip("# ").strip()
                current_lines = [line]
            else:
                current_lines.append(line)
        if current_lines:
            chunks.append(
                {
                    "content": "\n".join(current_lines).strip(),
                    "title": current_title,
                    "source": source,
                }
            )
        return chunks

    def index_knowledge(self) -> dict:
        collection = self.get_collection()
        kb_dir = Path(self.kb_dir)
        md_files = glob.glob(str(kb_dir / "**" / "*.md"), recursive=True)
        state = self.load_state()
        state_files: dict = state.get("files", {})

        current_rel_paths = set()
        added = 0
        updated = 0
        removed = 0

        for fpath in md_files:
            rel_path = os.path.relpath(fpath, self.kb_dir)
            current_rel_paths.add(rel_path)
            mtime = os.path.getmtime(fpath)
            prev = state_files.get(rel_path)
            if prev and float(prev.get("mtime", 0)) == float(mtime):
                continue

            old_ids = prev.get("chunk_ids", []) if prev else []
            if old_ids:
                collection.delete(ids=old_ids)

            text = Path(fpath).read_text(encoding="utf-8")
            chunks = self.chunk_markdown(text, rel_path)
            docs, metas, ids = [], [], []
            for chunk in chunks:
                content = chunk["content"]
                chunk_id = f"{rel_path}:{sha1_text(content)}"
                docs.append(content)
                metas.append({"title": chunk["title"], "source": chunk["source"]})
                ids.append(chunk_id)

            if docs:
                embs = self.model.encode(docs, show_progress_bar=False).tolist()
                collection.add(documents=docs, embeddings=embs, metadatas=metas, ids=ids)

            state_files[rel_path] = {"mtime": mtime, "chunk_ids": ids}
            if prev:
                updated += 1
            else:
                added += 1

        deleted_paths = [p for p in list(state_files.keys()) if p not in current_rel_paths]
        for rel_path in deleted_paths:
            ids = state_files.get(rel_path, {}).get("chunk_ids", [])
            if ids:
                collection.delete(ids=ids)
            state_files.pop(rel_path, None)
            removed += 1

        state["files"] = state_files
        self.save_state(state)
        return {"files_added": added, "files_updated": updated, "files_removed": removed}

    async def embed_query(self, query: str) -> list[float]:
        def timeout_handler(signum, frame):
            raise TimeoutError(f"embed_query 超时 ({EMBED_TIMEOUT}s)")

        # 设置超时
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(EMBED_TIMEOUT)
        try:
            result = await asyncio.to_thread(self.model.encode, query, show_progress_bar=False)
            return result.tolist()
        finally:
            signal.alarm(0)  # 取消闹钟


args = parse_args()
indexer = KnowledgeIndex(
    kb_dir=args.kb_dir,
    chroma_dir=args.chroma_dir,
    collection=args.collection,
    embed_model=args.embed_model,
)
server = Server("knowledge")

@server.list_tools()
async def list_tools():
    from mcp.types import Tool, TextContent
    return [
        Tool(
            name="search_knowledge",
            description="语义搜索知识库，返回最相关的知识片段（包含组件用法、业务规则、编码规范）",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "top_k": {"type": "integer", "description": "返回结果数", "default": 5},
                    "format": {"type": "string", "description": "返回格式：markdown 或 json", "default": "markdown"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_document",
            description="获取完整文档内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文档相对路径，如 UI组件/Button.md"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="refresh_index",
            description="重新索引知识库（新增/修改文档后调用）",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    from mcp.types import TextContent

    if name == "search_knowledge":
        query = arguments["query"]
        top_k = arguments.get("top_k", 5)
        fmt = arguments.get("format", "markdown")
        collection = indexer.get_collection()
        emb = await indexer.embed_query(query)
        results = collection.query(query_embeddings=[emb], n_results=top_k, include=["documents", "metadatas", "distances", "ids"])
        items = []
        for i in range(len(results["ids"][0])):
            items.append(
                {
                    "id": results["ids"][0][i],
                    "distance": results.get("distances", [[None]])[0][i],
                    "source": results["metadatas"][0][i].get("source"),
                    "title": results["metadatas"][0][i].get("title"),
                    "content": results["documents"][0][i],
                }
            )
        if fmt == "json":
            return [TextContent(type="text", text=json.dumps({"query": query, "results": items}, ensure_ascii=False, indent=2))]
        output = []
        for item in items:
            output.append(f"### [{item['source']}] {item['title']}\n{item['content']}\n")
        return [TextContent(type="text", text="\n---\n".join(output))]

    if name == "get_document":
        user_path = arguments["path"]
        try:
            fpath = safe_join(indexer.kb_dir, user_path)
        except ValueError:
            return [TextContent(type="text", text="非法路径")]
        if not fpath.exists() or not fpath.is_file():
            return [TextContent(type="text", text=f"文件不存在: {user_path}")]
        return [TextContent(type="text", text=fpath.read_text(encoding="utf-8", errors="replace"))]

    if name == "refresh_index":
        stats = await asyncio.to_thread(indexer.index_knowledge)
        _resource_cache.invalidate()
        return [TextContent(type="text", text=json.dumps({"ok": True, "stats": stats}, ensure_ascii=False, indent=2))]

    raise ValueError(f"未知工具: {name}")

class ResourceCache:
    """简单的资源列表缓存"""

    def __init__(self, ttl: int = 300):
        self._cache: dict | None = None
        self._cache_time: float = 0
        self._ttl = ttl

    def get(self) -> dict | None:
        if self._ttl <= 0 or self._cache is None:
            return None
        import time
        if time.time() - self._cache_time > self._ttl:
            self._cache = None
        return self._cache

    def set(self, data: dict) -> None:
        if self._ttl <= 0:
            return
        import time
        self._cache = data
        self._cache_time = time.time()

    def invalidate(self) -> None:
        self._cache = None


_resource_cache = ResourceCache(ttl=RESOURCE_CACHE_TTL)


@server.list_resources()
async def list_resources():
    from mcp.types import Resource

    cached = _resource_cache.get()
    if cached is not None:
        return cached

    kb_dir = Path(indexer.kb_dir)
    md_files = glob.glob(str(kb_dir / "**" / "*.md"), recursive=True)
    resources = []
    for fpath in md_files:
        rel_path = os.path.relpath(fpath, indexer.kb_dir)
        uri = f"{SCHEME_KB}:///{rel_path}"
        try:
            size = Path(fpath).stat().st_size
        except OSError:
            size = None
        resources.append(
            Resource(
                name=rel_path,
                title=rel_path,
                uri=uri,
                mimeType="text/markdown",
                size=size,
            )
        )

    _resource_cache.set(resources)
    return resources


@server.read_resource()
async def read_resource(uri):
    from urllib.parse import urlparse, unquote

    parsed = urlparse(str(uri))
    if parsed.scheme != SCHEME_KB:
        raise ValueError("Unsupported uri")
    rel_path = unquote(parsed.path.lstrip("/"))
    fpath = safe_join(indexer.kb_dir, rel_path)
    return fpath.read_text(encoding="utf-8", errors="replace")


@server.list_prompts()
async def list_prompts():
    from mcp.types import Prompt, PromptArgument

    return [
        Prompt(
            name="kb_search_and_cite",
            title="知识库检索与引用",
            description="指导 agent 如何检索、引用、溯源本知识库内容",
            arguments=[
                PromptArgument(name="task", description="当前要解决的任务", required=True),
            ],
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None):
    from mcp.types import GetPromptResult, PromptMessage, TextContent

    if name != "kb_search_and_cite":
        raise ValueError("Unknown prompt")
    task = (arguments or {}).get("task", "")
    text = "\n".join(
        [
            "你可以使用当前 MCP Server 提供的 knowledge 工具与资源来辅助开发：",
            "",
            "1) 先用 search_knowledge 查询与你的任务最相关的组件/规范/业务规则，优先选择距离更小的结果。",
            "2) 对关键结论，使用 get_document 或 resources/read 获取原文上下文，避免只依据片段做决定。",
            "3) 在输出方案或代码时，明确引用来源文件路径与标题，必要时贴出原文关键段落。",
            "4) 若发现知识库缺失内容，列出需要补充的文档条目或目录结构建议。",
            "",
            f"当前任务：{task}".strip(),
        ]
    )
    return GetPromptResult(
        description="知识库使用指南",
        messages=[PromptMessage(role="system", content=TextContent(type="text", text=text))],
    )


def build_starlette_app(token: str | None, transport: str):
    from starlette.applications import Starlette
    from starlette.responses import Response
    from starlette.routing import Mount, Route
    from starlette.types import Receive, Scope, Send

    def check_token(scope: Scope, token: str | None) -> bool:
        """
        验证请求 token。
        支持三种方式：
        1. Authorization: Bearer <token>
        2. X-MCP-Token: <token>
        3. ?token=<token> (仅当 token 已设置时生效)
        注意：生产环境应通过 HTTPS 部署，防止 token 在传输过程中被截获。
        """
        if not token:
            return True
        import secrets
        headers = {k.decode("latin1").lower(): v.decode("latin1") for k, v in scope.get("headers", [])}
        auth = headers.get("authorization", "")
        x_token = headers.get("x-mcp-token", "")
        query_token = dict(scope.get("query_string", b"").decode().split("=") for p in scope.get("root_path", "").split("&") if "=" in p).get("token", "")
        if auth.startswith("Bearer "):
            return secrets.compare_digest(auth.removeprefix("Bearer ").strip(), token)
        if x_token:
            return secrets.compare_digest(x_token.strip(), token)
        if query_token:
            return secrets.compare_digest(query_token, token)
        return False

    async def guard(scope: Scope, receive: Receive, send: Send, next_app):
        if not check_token(scope, token):
            await Response("Unauthorized", status_code=401)(scope, receive, send)
            return
        await next_app(scope, receive, send)

    if transport == "sse":
        from mcp.server.sse import SseServerTransport

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await server.run(streams[0], streams[1], server.create_initialization_options())
            return Response()

        routes = [
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ]
        app = Starlette(routes=routes)
    else:
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        import contextlib

        manager = StreamableHTTPSessionManager(app=server)

        async def handle(scope: Scope, receive: Receive, send: Send) -> None:
            await manager.handle_request(scope, receive, send)

        @contextlib.asynccontextmanager
        async def lifespan(app: Starlette):
            async with manager.run():
                yield

        app = Starlette(routes=[Mount("/", app=handle)], lifespan=lifespan)

    async def guarded(scope: Scope, receive: Receive, send: Send):
        await guard(scope, receive, send, app)

    return guarded


async def main():
    print("🚀 知识库 MCP RAG Server 启动中...")
    if args.index_on_startup:
        indexer.index_knowledge()
    if args.transport == "stdio":
        async with server.run_stdio():
            pass
        return

    app = build_starlette_app(args.token, args.transport)
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    asyncio.run(main())

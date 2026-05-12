# 仓库规范

## 项目结构
- `docs/` 存放知识库 Markdown 原文，也是 VitePress 站点内容来源。
- `docs/.vitepress/config.js` 定义导航和侧边栏。
- `mcp-server/` 存放 Python MCP RAG 服务，核心文件是 `server.py`，索引数据在 `.chroma/`。
- `bin/knowledge-mcp` 是 MCP 服务启动脚本。

## 构建与运行
- `npm run docs:dev` 本地启动 VitePress 文档站。
- `npm run docs:build` 构建静态站点到 `docs/.vitepress/dist/`。
- `npm run docs:preview` 预览构建后的站点。
- `cd mcp-server && python server.py` 直接启动 MCP 服务。
- `bin/knowledge-mcp` 使用仓库默认配置启动 MCP 服务。

## 编写规范
- 文档请使用 Markdown，并尽量用清晰的 `##` 作为二级分段；MCP 索引会按二级标题切片。
- 新文件路径请保持与现有分类一致，例如 `docs/UI组件/Button.md`、`docs/业务场景/订单流程.md`。
- 标题建议简短、明确，优先使用中文。
- Python 代码风格保持和 `server.py` 一致：标准库优先导入、函数短小、路径处理明确。

## 验证方式
- 本仓库没有完整的自动化测试套件。
- 修改文档后，至少运行 `npm run docs:build` 检查是否能正常构建。
- 修改 MCP 相关代码后，启动 `bin/knowledge-mcp`，确认可以正常索引 `docs/`，且没有报错。
- 调整知识文档时，注意 `##` 分段是否仍然清晰可切。

## 提交与 PR
- 当前工作区没有可用的本地 git 历史，因此没有固定的仓库专属提交模板可参考。
- 提交信息建议简短、祈使式，例如 `docs: update payment rules` 或 `mcp: fix index refresh`。
- PR 说明应写清楚改了哪些内容、影响哪些路径、做了哪些验证。
- 只有 VitePress 界面变化时才需要附截图，纯文档修改通常只需文字说明。

## Agent 说明
- 修改 `docs/` 下的文件后，记得重启服务或调用 `refresh_index` 让索引同步。
- 不要直接修改 `docs/.vitepress/dist/` 和 `mcp-server/.chroma/` 这类生成产物，应该通过构建或索引流程重新生成。

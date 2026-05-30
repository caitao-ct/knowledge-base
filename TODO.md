# 项目优化任务清单

## P0 - 必须修复

- [x] **P0-1**: requirements.txt 添加版本锁定
- [x] **P0-2**: HTTP Token 明文传输安全问题加固
- [x] **P0-3**: VitePress base path 配置动态化

## P1 - 强烈建议

- [x] **P1-1**: 异常处理具体化（替换 broad except Exception）
- [x] **P1-2**: 路径穿越防护逻辑加强
- [x] **P1-3**: refresh_index 异步化或增加超时处理
- [x] **P1-4**: CI 添加单元测试

## P2 - 建议改进

- [x] **P2-1**: list_resources 添加缓存机制
- [x] **P2-2**: 添加重试和超时控制
- [x] **P2-3**: package.json 补全 description/author 字段
- [x] **P2-4**: deploy-docs.yml 触发条件添加 path filter

## P3 - 可选优化

- [x] **P3-1**: 提取魔法字符串为常量
- [x] **P3-2**: 代码风格统一（import 分组等）
- [x] **P3-3**: 补充 API 文档

---

## 修复记录

| 日期 | 任务 | 状态 | 说明 |
|------|------|------|------|
| 2026-05-30 | P0-1 | ✅ 完成 | 为 requirements.txt 添加了版本锁定 (>=) |
| 2026-05-30 | P0-2 | ✅ 完成 | 使用 secrets.compare_digest 防止时序攻击，添加 HTTPS 安全提示 |
| 2026-05-30 | P0-3 | ✅ 完成 | VitePress base 可通过 VITEPRESS_BASE 环境变量配置 |
| 2026-05-30 | P1-1 | ✅ 完成 | 将 3 处 broad Exception 改为具体异常类型 |
| 2026-05-30 | P1-2 | ✅ 完成 | safe_join 使用 Path.resolve() 和 relative_to() 严格校验 |
| 2026-05-30 | P1-3 | ✅ 完成 | refresh_index 使用 asyncio.to_thread 避免阻塞 |
| 2026-05-30 | P1-4 | ✅ 完成 | 添加 pytest 单元测试，完善 CI 流程（添加缓存、path filter） |
| 2026-05-30 | P2-1 | ✅ 完成 | 添加 ResourceCache 类，默认 TTL 300s，refresh_index 时失效缓存 |
| 2026-05-30 | P2-2 | ✅ 完成 | embed_query 添加 signal timeout (30s)，INDEX_TIMEOUT 常量定义 |
| 2026-05-30 | P2-3 | ✅ 完成 | package.json 补全 description/author，重新组织字段顺序 |
| 2026-05-30 | P2-4 | ✅ 完成 | deploy-docs.yml 添加 paths filter（docs/**, package.json） |
| 2026-05-30 | P3-1 | ✅ 完成 | 提取 SCHEME_KB, METADATA_HNSW_SPACE, METADATA_HNSW_KEY 常量 |
| 2026-05-30 | P3-2 | ✅ 完成 | import 语句分组展开（os, glob, json...） |
| 2026-05-30 | P3-3 | ✅ 完成 | 新增 mcp-server/API.md，包含工具、资源、提示、安全配置说明 |
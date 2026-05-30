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

- [ ] **P2-1**: list_resources 添加缓存机制
- [ ] **P2-2**: 添加重试和超时控制
- [ ] **P2-3**: package.json 补全 description/author 字段
- [ ] **P2-4**: deploy-docs.yml 触发条件添加 path filter

## P3 - 可选优化

- [ ] **P3-1**: 提取魔法字符串为常量
- [ ] **P3-2**: 代码风格统一（import 分组等）
- [ ] **P3-3**: 补充 API 文档

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
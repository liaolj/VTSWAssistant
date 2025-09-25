# 贡献指南

## 分支与提交
- `main`：稳定分支；`dev/*`：开发分支；`feat/*`、`fix/*`：功能/修复
- 提交信息使用 `type(scope): subject`，如 `feat(asr): support reconnect`

## 代码与风格
- 遵循项目 linter/formatter 规则（提交前运行 `lint`/`format` 任务）
- 重要路径需附单元/集成测试与文档更新

## PR 要求
- 关联 Issue，勾选检查清单
- 附带截图/日志（脱敏），说明兼容性影响与回滚方案

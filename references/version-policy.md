# YD-job 版本策略（Version Policy）v1

> 对齐 YD-bus `version-policy.md`。

- `.harness-plugin/plugin.json` 的 `version` **只在用户明确要求升级/降级/设版本号时修改**
- 普通功能、规则、参考文档、测试、内容变更 **禁止** 自行升版本号
- 不得因为改动大小推断版本升级；版本号一律逐字保留现状
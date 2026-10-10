# 证据摘要

| 文件 | 来源与含义 |
| --- | --- |
| `snapshot.json` | 已提交来源仓库、提交哈希和提取范围 |
| `dotnet-validation.json` | 本地历史方法恢复验证：资源长度、补丁数、1269 条方法体匹配，以及原始 / 恢复 DLL 哈希 |
| `firmware-validation.json` | 本地历史容器校验与损坏输入拒绝结果 |
| `firmware-5.8-summary.json` | 本地 5.8 样本的头部、长度、向量、地址与哈希，不含应用正文 |
| `publication-validation.json` | 本次整理后的测试与离线验证结果 |

历史摘要直接取自先前本地分析输出；未包含厂商代码体、设备标识或原始通信捕获。摘要中的 `true` 是当时的分析结果，不代表本次重跑，也不能替代原始输入的独立验证。输入复现方法见 [复现指南](../docs/reproduction.md)。

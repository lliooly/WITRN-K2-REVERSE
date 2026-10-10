# 逐文件目录

每项对应一个公开文件。`MANIFEST.json` 记录文件大小与 SHA-256（不对其自身计算递归哈希）。

| 文件 | 用途 |
| --- | --- |
| [.github/workflows/verify.yml](.github/workflows/verify.yml) | Python 3.9 / 3.13 离线测试和清单 CI |
| [.gitignore](.gitignore) | 本地输入、厂商文件、私人数据及生成物忽略规则 |
| [CATALOG.md](CATALOG.md) | 本逐文件索引 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献证据、第三方来源与合成测试要求 |
| [LICENSE](LICENSE) | 来源项目标准 MIT 许可证 |
| [MANIFEST.json](MANIFEST.json) | 全部发布文件的大小与 SHA-256 清单 |
| [NOTICE.md](NOTICE.md) | 许可证适用范围、第三方权利及侵权联系删除声明 |
| [README.md](README.md) | 研究总览、主题导航与离线入口 |
| [TAKEDOWN.md](TAKEDOWN.md) | 联系入口和删除请求处理方法 |
| [docs/k2-emark-design.md](docs/k2-emark-design.md) | E-Mark 设计背景 |
| [docs/k2-monitor-design.md](docs/k2-monitor-design.md) | 遥测和记录设计背景 |
| [docs/k2-monitor-hardware-validation.md](docs/k2-monitor-hardware-validation.md) | K2 5.8 历史只读遥测实测汇总 |
| [docs/k2-monitor-plan.md](docs/k2-monitor-plan.md) | 遥测实现阶段计划历史记录 |
| [docs/k2-monitor-research.md](docs/k2-monitor-research.md) | Qt 上位机调查、遥测与官方交换格式证据 |
| [docs/k2-monitor.md](docs/k2-monitor.md) | 采集、文件交换与统计使用说明 |
| [docs/k2picture-design.md](docs/k2picture-design.md) | 图片和表盘实现设计背景 |
| [docs/k2picture-plan.md](docs/k2picture-plan.md) | 图片和表盘实现计划历史记录 |
| [docs/macos-app.md](docs/macos-app.md) | 原应用构建与打包说明；完整应用见来源仓库 |
| [docs/materials.md](docs/materials.md) | 输入来源与未公开材料类别 |
| [docs/monitor-performance.md](docs/monitor-performance.md) | 记录和图表查询性能背景 |
| [docs/protocol.md](docs/protocol.md) | 固件容器、帧、命令、升级顺序与测速实测 |
| [docs/reproduction.md](docs/reproduction.md) | 依赖、输入哈希、复现顺序与自动化缺口 |
| [docs/ui-layout-design.md](docs/ui-layout-design.md) | 原应用 UI 设计背景 |
| [docs/ui-layout-plan.md](docs/ui-layout-plan.md) | 原应用 UI 实现计划背景 |
| [docs/ui-layout-validation.md](docs/ui-layout-validation.md) | 原应用历史布局验证背景 |
| [docs/validation.md](docs/validation.md) | 静态、合成测试和历史实机结果边界 |
| [evidence/README.md](evidence/README.md) | 历史摘要来源及证据限制 |
| [evidence/dotnet-validation.json](evidence/dotnet-validation.json) | 历史方法恢复验证摘要 |
| [evidence/firmware-5.8-summary.json](evidence/firmware-5.8-summary.json) | 5.8 固件格式 / 向量 / 地址摘要，不含正文 |
| [evidence/firmware-validation.json](evidence/firmware-validation.json) | 历史固件校验与破坏样本拒绝摘要 |
| [evidence/publication-validation.json](evidence/publication-validation.json) | 本次发布离线核验结果 |
| [evidence/snapshot.json](evidence/snapshot.json) | 来源仓库提交与提取范围 |
| [k2_gui_backend.py](k2_gui_backend.py) | JSON 后台兼容入口 |
| [k2_updater.py](k2_updater.py) | 命令行兼容入口 |
| [k2up/__init__.py](k2up/__init__.py) | 参考实现版本标识 |
| [k2up/__main__.py](k2up/__main__.py) | python -m k2up 入口 |
| [k2up/backup.py](k2up/backup.py) | 完整应用区双遍读取与恢复容器生成 |
| [k2up/cli.py](k2up/cli.py) | 离线检查、模拟、探测、备份和真实升级 CLI |
| [k2up/data/firmware_decode.bin](k2up/data/firmware_decode.bin) | 256 字节协议替换表；第三方权利另见 NOTICE |
| [k2up/demo.py](k2up/demo.py) | GUI 模拟数据与合成样例 |
| [k2up/emark.py](k2up/emark.py) | E-Mark 单条记录、集合、工程及位字段 |
| [k2up/firmware.py](k2up/firmware.py) | 固件格式校验、应用向量与提交标记 |
| [k2up/gui_bridge.py](k2up/gui_bridge.py) | JSON 请求、身份核验与后台操作桥接 |
| [k2up/monitor.py](k2up/monitor.py) | 只读遥测采集及后台记录控制 |
| [k2up/official_firmware.py](k2up/official_firmware.py) | 官方固件来源与下载校验逻辑 |
| [k2up/picture.py](k2up/picture.py) | 表盘参数与 RGB565 图像格式 |
| [k2up/picture_device.py](k2up/picture_device.py) | 固定资源范围、双遍备份及读回比较 |
| [k2up/picture_simulator.py](k2up/picture_simulator.py) | 资源模拟器与失败注入 |
| [k2up/protocol.py](k2up/protocol.py) | 64 字节 HID 帧、双校验与同步命令 |
| [k2up/recording.py](k2up/recording.py) | 分段记录、采样和本地存储 |
| [k2up/recording_files.py](k2up/recording_files.py) | CSV / SQLite 文件交换 |
| [k2up/recording_stats.py](k2up/recording_stats.py) | 区间统计与积分 |
| [k2up/simulator.py](k2up/simulator.py) | 升级主机流程内存模拟器 |
| [k2up/telemetry.py](k2up/telemetry.py) | 普通模式遥测字段与报告校验；含 MIT 改编 |
| [k2up/transport.py](k2up/transport.py) | HIDAPI 枚举、选择与报告 ID 适配 |
| [k2up/updater.py](k2up/updater.py) | 型号核验、擦写阶段、完整比较及提交 |
| [requirements-analysis.txt](requirements-analysis.txt) | 可选静态 .NET 分析依赖 |
| [requirements.txt](requirements.txt) | 真实 HID 操作所需 HIDAPI 依赖 |
| [reverse/K2EMARK.md](reverse/K2EMARK.md) | E-Mark 文件、VDO 位字段、集合与资源地址 |
| [reverse/K2PICTURE.md](reverse/K2PICTURE.md) | 图片、表盘布局、资源地址与静态方法证据 |
| [reverse/README.md](reverse/README.md) | 分析脚本操作说明 |
| [reverse/REPORT.md](reverse/REPORT.md) | UP V30 方法恢复、固件与实现边界总报告 |
| [reverse/benchmark_dfu_reads.py](reverse/benchmark_dfu_reads.py) | 仅放行 3 / 10 / 11 命令的实机只读测速 |
| [reverse/extract_delegates.py](reverse/extract_delegates.py) | 恢复代理字段与目标 token |
| [reverse/extract_tables.py](reverse/extract_tables.py) | 提取字节替换与扇区配置表 |
| [reverse/inspect_dotnet.py](reverse/inspect_dotnet.py) | 导出托管方法 IL 与嵌入资源 |
| [reverse/inspect_firmware.py](reverse/inspect_firmware.py) | 依赖本地导出表的离线固件研究检查 |
| [reverse/parse_vm.py](reverse/parse_vm.py) | 解析保护器 VM 与初始化常量 |
| [reverse/restore_methods.py](reverse/restore_methods.py) | 恢复方法体并校验记录长度；仅本地生成 DLL |
| [reverse/unpack_static.py](reverse/unpack_static.py) | 静态解释资源解码器 IL |
| [tests/test_dfu_read_benchmark.py](tests/test_dfu_read_benchmark.py) | 合成 / 模拟回归：dfu_read_benchmark |
| [tests/test_emark.py](tests/test_emark.py) | 合成 / 模拟回归：emark |
| [tests/test_gui_bridge.py](tests/test_gui_bridge.py) | 合成 / 模拟回归：gui_bridge |
| [tests/test_k2up.py](tests/test_k2up.py) | 合成 / 模拟回归：k2up |
| [tests/test_monitor.py](tests/test_monitor.py) | 合成 / 模拟回归：monitor |
| [tests/test_official_firmware.py](tests/test_official_firmware.py) | 合成 / 模拟回归：official_firmware |
| [tests/test_picture.py](tests/test_picture.py) | 合成 / 模拟回归：picture |
| [tests/test_recording.py](tests/test_recording.py) | 合成 / 模拟回归：recording |
| [tests/test_recording_stats.py](tests/test_recording_stats.py) | 合成 / 模拟回归：recording_stats |
| [tests/test_telemetry.py](tests/test_telemetry.py) | 合成 / 模拟回归：telemetry |
| [third_party/README.md](third_party/README.md) | 实际改编代码的来源及修改说明 |
| [third_party/witrn-driver-LICENSE.txt](third_party/witrn-driver-LICENSE.txt) | didim99 上游 MIT 许可证全文 |
| [tools/manifest.py](tools/manifest.py) | 生成与核验 SHA-256 发布清单 |

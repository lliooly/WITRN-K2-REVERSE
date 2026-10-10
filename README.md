# WITRN K2 逆向研究资料库

面向 WITRN UP V30、K2Picture 1.1 与 WITRN PC V1.0.4 的独立逆向研究：汇总协议、文件格式、静态分析脚本、Python 参考实现、合成测试与已有实机结果。

本库整理日期为 **2026-10-10**。研究快照来自 [应用仓库](https://github.com/lliooly/witrn-k2-updater-re)，来源提交见 [snapshot.json](evidence/snapshot.json)。本库专注研究资料；SwiftUI 应用、安装包与后续应用开发请查看原仓库。

## 阅读导航

| 主题 | 主要文档 | 主要实现 / 工具 |
| --- | --- | --- |
| 主程序方法恢复、代理映射与 VM 常量 | [逆向总报告](reverse/REPORT.md)、[复现指南](docs/reproduction.md) | `reverse/inspect_dotnet.py`、`unpack_static.py`、`restore_methods.py`、`extract_delegates.py`、`parse_vm.py` |
| `.k2` 固件容器、替换表、GUID、向量与提交标记 | [固件与 HID 协议](docs/protocol.md) | `reverse/extract_tables.py`、`reverse/inspect_firmware.py`、`k2up/firmware.py` |
| 64 字节 HID 帧、双校验、DFU 命令与升级顺序 | [协议说明](docs/protocol.md) | `k2up/protocol.py`、`transport.py`、`updater.py`、`backup.py` |
| `.pic` 表盘、RGB565 图片、资源地址与整扇区保留 | [K2Picture 静态分析](reverse/K2PICTURE.md) | `k2up/picture.py`、`picture_device.py` |
| `.wtemark`、VDO 位字段、10 组集合与工程格式 | [E-Mark 静态分析](reverse/K2EMARK.md) | `k2up/emark.py` |
| 普通模式遥测报告、温度、电流符号与采样 | [上位机调查](docs/k2-monitor-research.md)、[采集说明](docs/k2-monitor.md) | `k2up/telemetry.py`、`monitor.py` |
| CSV / SQLite 交换、分段、统计和区间查询 | [采集说明](docs/k2-monitor.md)、[性能说明](docs/monitor-performance.md) | `k2up/recording.py`、`recording_files.py`、`recording_stats.py` |
| 只读 DFU 测速、短读取与大批量读取 | [测速结果](docs/protocol.md#dfu-读取性能实测)、[工具用法](reverse/README.md#dfu-只读测速) | `reverse/benchmark_dfu_reads.py` |
| 单台 K2 实机验证及未验证范围 | [验证边界](docs/validation.md)、[采集实测](docs/k2-monitor-hardware-validation.md) | `evidence/` 中的历史分析摘要 |

全部文件逐项说明见 [文件目录](CATALOG.md)，文件大小和 SHA-256 见 [发布清单](MANIFEST.json)。

## 已整理的关键结论

- 主程序集恢复：292208 字节资源、650 处头部 / 元数据补丁、1269 条方法记录、574 组代理映射、118 个 VM 混淆常量。
- K2 固件：48 字节头部，应用起点 `0x08003800`，`0xC00` 正文偏移处提交标记；文件校验不构成数字签名或来源认证。
- HID：64 字节帧，52 字节负载空间，两项累加校验；写入包的数据最多 40 字节。命令、ACK、失败停止行为均列在协议文档。
- K2Picture：400 字节 `.pic`、22 条元素记录；235 × 235 开机图、240 × 240 背景、RGB565 小端像素；参数、背景和开机图各有固定资源范围。
- E-Mark：66 字节单条记录、666 字节配置集合；保留未知位、未使用槽位和完整扇区尾部。
- 遥测：普通模式 `0x1A` 报告，电压、有符号电流、温度、D±、累计 Ah / Wh 和运行时间；记录格式分别保存设备累计值与电脑积分值。

以上数字对应特定分析输入，不能直接推广到其他型号或版本。哈希、方法 RID、地址及验证范围见原始研究文档。

## 目录

```text
reverse/       静态分析脚本、总报告、图片和 E-Mark 格式报告
k2up/          Python 协议、文件格式、采集、升级与模拟参考实现
tests/         合成文件、内存模拟传输及失败路径测试
docs/          协议、实测、复现与设计资料
evidence/      不含代码体和私人设备标识的历史分析摘要
third_party/   实际使用的第三方代码来源及许可证
tools/         发布文件清单生成与核验工具
LICENSE        标准 MIT 许可证
NOTICE.md      许可范围、第三方权利与侵权联系删除说明
TAKEDOWN.md    联系入口和删除请求处理方法
```

设计和 UI 文档保留作研究背景，其中提到的 SwiftUI 文件、构建脚本、应用版本和 `dist/` 路径属于原应用仓库，未包含在本研究快照中。

## 离线开始

Python 3.9 或以上。在仓库根目录执行：

```sh
python3 -m unittest discover -s tests -v
python3 -m k2up --help
python3 tools/manifest.py --check
```

这些命令不连接 USB。固件离线检查使用你自行合法取得的本地文件：

```sh
python3 -m k2up inspect /path/to/K2_APP.k2
python3 -m k2up dry-run /path/to/K2_APP.k2
```

`.NET` 静态复现的依赖、输入哈希、顺序和工具限制见 [复现指南](docs/reproduction.md)。真实 HID 操作需要 `requirements.txt` 中的 HIDAPI，只有在明确选择相应命令时才连接设备。擦写功能为实验实现；支持范围和恢复尚未验证事项请先阅读 [验证边界](docs/validation.md)。

## 内容完整性与公开范围

本库保留已提交的全部 Python 研究脚本、参考模块和测试，以及技术报告、相关设计 / UI 背景文档；补充历史方法恢复和固件校验摘要。尚未整理成通用脚本的 K2Picture 局部分析步骤会明确标注，不将报告伪装成可一键复现的流程。

厂商可执行文件、官方固件、恢复 DLL、完整反编译文本、IDA 数据库、设备备份、序列号和原始通信日志留在本地。对应类别、原因和可复现方式见 [材料与来源](docs/materials.md)。公开研究采用文档、哈希、脚本和合成测试提供可复核信息。

## 许可证与侵权联系删除

项目原创代码和文档使用 [MIT](LICENSE)，复用时保留版权与许可证声明；MIT 允许修改、分发及商业使用，详见 [MIT 说明](https://choosealicense.com/licenses/mit/)。第三方代码保留原许可证，厂商材料和商标的权利不因本库许可证而改变。具体范围见 [NOTICE.md](NOTICE.md)。

**如有侵权，请联系删除。** 如您认为本仓库内容侵犯您的合法权益，请通过 [Issues](https://github.com/lliooly/witrn-k2-research/issues/new) 提供具体文件 / 行号、权属依据和联系方式。维护者会核查，并对确有侵权或授权不足的相关内容及时删除、修改或下架。涉及不宜公开的信息时，可使用 [GitHub 官方版权投诉入口](https://github.com/contact/dmca)。处理说明见 [TAKEDOWN.md](TAKEDOWN.md)。

联系删除声明是争议处理承诺，不是第三方授权或免除责任的依据。本项目与 WITRN 无隶属关系，也不代表厂商官方支持。

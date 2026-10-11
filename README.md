# WITRN-K2-REVERSE

我在这里整理 WITRN K2 的逆向分析、协议与开发接口，供实现上位机、数据采集器和文件编辑器参考。以 USB HID 命令、JSON 进程接口与 Python 函数契约为开发入口，保留静态证据、文件格式和验证范围供复核。

## 配套 Mac 应用

[维简 Mac · WITRN K2 工具箱](https://github.com/lliooly/witrn-k2-mac) 提供原生 SwiftUI 上位机、曲线记录、固件升级、表盘、开机图和虚拟 E-Mark 管理。安装、使用与应用问题请从应用仓库开始；协议、文件格式与开发接口继续在本仓库查阅。

两边的 Python 实现独立维护，不是自动同步的共享 SDK。跨仓库协议修改应关联具体提交并说明静态、模拟与实机验证范围，详见应用仓库的[联动约定](https://github.com/lliooly/witrn-k2-mac/blob/main/docs/repository-map.md)。

## 开发者入口

| 目标 | 参考 | 内容 |
| --- | --- | --- |
| 自行实现设备通信 | [HID 命令参考](api/device-commands.md) | 命令号、读 / 写 / 控制性质、参数布局、响应与前置条件 |
| 用新 UI 复用后台 | [JSON / NDJSON 接口](api/bridge.md) | 15 个操作、请求字段、结果、实时控制与错误事件 |
| 直接调用 Python | [逐函数参考](api/python-reference.md) | 112 个显式函数 / 方法 / 属性：签名、用途、返回、副作用、异常与源码 |
| 从零接入上位机 | [接入路径](api/integration.md) | 普通读数、身份探测、资源事务与记录流程 |
| 无设备验证集成 | [可运行示例](examples/README.md) | SDK、子进程、记录查询与文件交换 |
| 了解支持与缺口 | [开发覆盖评估](api/coverage.md) | 接口覆盖、证据强度、尚未识别能力 |

## 最小离线验证

Python 3.9 或以上，在根目录运行，不连接 USB：

```sh
python3 examples/sdk_demo.py
python3 examples/bridge_demo.py
python3 examples/recording_demo.py
python3 -m unittest discover -s tests -v
python3 tools/manifest.py --check
```

真实 HID 接入需安装 `requirements.txt`，并按接口文档区分普通模式和 DFU。写入前须完成身份核对、用户明确确认与完整备份；底层写包不是完整升级接口。

## 研究与证据

[研究主线](research/README.md) 按方法恢复、固件 / DFU、表盘图片、E-Mark、遥测组织。每个主题连接结论、原函数、数据布局、操作流程和验证边界。

[函数定位索引](research/functions/README.md) 包含已识别职责与原函数 RID / token / 地址，另有 1269 条恢复方法和 574 组代理元数据。该元数据不代表全部方法已获语义解释；未知厂商内部方法不是可供集成的公开 API。

## 仓库结构

- `api/`：开发接口、逐函数契约与覆盖评估。
- `examples/`：可执行的离线集成示例。
- `research/`：研究主线及原函数定位。
- `reverse/`：静态工具和详细报告；`docs/`：协议、实测与复现资料。
- `k2up/`、`tests/`：Python 实现与合成 / 模拟测试。
- `evidence/`：分析摘要；`archive/application/`：应用背景附录。
- `third_party/`：改编来源；`assets/`：文档图像；`tools/`：文件清单维护。

[逐文件附录](CATALOG.md) 和 [SHA-256 清单](MANIFEST.json) 用于检索材料。输入来源、未公开材料及可复现方式见 [materials.md](docs/materials.md)。厂商程序、固件、完整反编译、恢复 DLL、IDA 数据库和私人设备数据不随库发布。

原研究来源为 [应用仓库](https://github.com/lliooly/witrn-k2-updater-re)，输入版本与哈希见 [复现指南](docs/reproduction.md)。硬件实测只覆盖特定单台 K2，其他型号与恢复流程不能据此推定兼容。

## 许可证与版权联系

原创代码和文档使用标准 [MIT](LICENSE)。第三方代码保留原许可，厂商材料、协议表与商标的权利范围见 [NOTICE.md](NOTICE.md)。MIT 不授予我无权许可的第三方内容。

[![如有侵权，请联系删除；邮箱 1604047731@qq.com](assets/copyright-notice.svg)](mailto:1604047731@qq.com)

**版权联系邮箱：[1604047731@qq.com](mailto:1604047731@qq.com)**。请提供具体文件、权属依据与联系方式；我会核查，并对确有侵权或授权不足的内容及时删除、修改或下架。处理方式见 [TAKEDOWN.md](TAKEDOWN.md)。

本项目为独立研究，与 WITRN 无隶属关系，未获厂商认可或赞助。联系删除声明不替代授权。

# WITRN K2 开发接口

本文面向需要实现上位机、采集器或文件编辑器的开发者。接口分为设备线协议、跨语言进程接口和 Python 参考实现三层。

| 开发方式 | 入口 | 适用语言 / 场景 |
| --- | --- | --- |
| 自行实现设备通信 | [HID 命令契约](device-commands.md) | C、C++、Rust、Swift、C# 等具有 HID 库的环境 |
| 复用后台，开发新的 UI | [JSON / NDJSON 进程接口](bridge.md) | 任何能启动 Python 子进程并读取标准输出的语言 |
| 直接引用 Python 模块 | [逐函数参考](python-reference.md) | Python 工具、实验和数据处理 |
| 从零接入 | [开发接入路径](integration.md) | 最小读取、资源流程、遥测与记录 |
| 无设备验证调用 | [离线示例](../examples/README.md) | 合成固件、模拟传输、记录与文件交换 |

## 接口不是 HTTP

K2 的已分析接口是 USB HID：读 / 写 HID 报告，负载中的命令号决定操作。没有 HTTP URL、GET / POST 方法、Cookie 或网络鉴权。`read_memory` 仍需要向设备发送 HID 读取请求，但不改写 Flash。

JSON 后台是本项目的本地进程接口，不是厂商提供的网络 API。请求用 `operation`，响应是 NDJSON 事件。上层应用可以自建服务，但 HTTP 映射属于该应用的设计，不是本研究恢复的协议。

## 信息可信度与覆盖范围

- 设备命令：结合特定厂商输入的静态分析与单台 K2 实测整理；每项标注模式及副作用。
- JSON / Python 契约：依据公开参考实现逐项核对，可运行离线示例。
- 厂商内部函数：1269 条恢复记录是定位元数据，不能视为全部 1269 个函数已获语义解释。已识别入口见 [研究索引](../research/functions/README.md)，未识别项不建议作为开发 API。
- E-Mark、背景 / 参数真实写入及恢复存在验证缺口；完整范围见 [验证矩阵](../docs/validation.md)。

## 快速选择

读取实时数值：普通模式 → `HidTransport.read` → `decode_report`，不发送 DFU 命令。

读取应用身份：DFU → `Updater.probe`；枚举 VID / PID 本身不足以确认型号。

写入固件或资源：优先复用 JSON 后台的完整校验、身份绑定、双遍备份与读回流程，不把底层写包当作完整升级接口。

离线编辑：`Firmware`、`Resource.validate`、E-Mark 校验和记录文件 API 不访问 USB。GUI 线程应把 USB、统计和导入导出交给工作线程或子进程。

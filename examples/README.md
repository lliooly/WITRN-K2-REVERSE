# 可运行开发示例

在仓库根目录执行 Python 3.9 或以上。三个示例仅使用标准库、合成数据和模拟传输，不连接 USB，不需要厂商程序或固件。

| 示例 | 命令 | 演示能力 |
| --- | --- | --- |
| [sdk_demo.py](sdk_demo.py) | `python3 examples/sdk_demo.py` | 构造帧、校验固件、模拟身份和升级、遥测解析、E-Mark 集合 |
| [bridge_demo.py](bridge_demo.py) | `python3 examples/bridge_demo.py` | 子进程请求、NDJSON 事件、模拟探测和资源读取 |
| [recording_demo.py](recording_demo.py) | `python3 examples/recording_demo.py` | SQLite 写入、区间统计、CSV 导出 / 导入 |

记录和桥接示例在临时目录生成本地文件，完成后删除。示例成功证明调用契约和模拟流程，不代表真实 USB 擦写兼容。真实只读接入代码见 [integration.md](../api/integration.md)。

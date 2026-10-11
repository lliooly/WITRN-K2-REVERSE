# 开发接入路径

## 选择接口层

新的 Swift / C# / Electron 等 UI 可先复用 Python JSON 后台：调用 [bridge.md](bridge.md) 中的操作，读取进度与结果，将 USB 和文件处理与 UI 隔离。需要去除 Python 运行时的应用，可按 [设备契约](device-commands.md) 重写 HID 层，并用合成测试核对帧与失败行为。

原始 C# 的 RID、RVA 和代理不是可直接调用的设备 API。开发应使用命令契约或公开参考实现，研究索引用于追溯依据。

## 普通模式实时读取

安装 `requirements.txt` 的 HIDAPI 后运行以下代码。它只枚举、打开、读取和关闭接口，不写入设备：

```python
import time
from k2up.transport import enumerate_devices, select_device, HidTransport
from k2up.telemetry import decode_report

# 多接口时传入明确的 path_hex，避免选择歧义。
selected = select_device(enumerate_devices())
transport = HidTransport(selected)
started = time.monotonic()
try:
    for _ in range(100):
        raw = transport.read(200)
        if not raw:
            continue
        sample = decode_report(raw, time.monotonic() - started)
        if sample is not None:
            print(sample.voltage, sample.current, sample.power)
finally:
    transport.close()
```

此代码没有记录管理和断连 UI。普通模式没有有效报告时，应提示检查模式 / 接口，不尝试用 DFU 命令“唤醒”。

## DFU 只读身份探测

```python
from k2up.transport import enumerate_devices, select_device, HidTransport
from k2up.protocol import Protocol
from k2up.updater import Updater

transport = HidTransport(select_device(enumerate_devices()))
try:
    identity = Updater(Protocol(transport)).probe()
    print(identity.summary())
finally:
    transport.close()
```

设备须已进入 DFU；该调用发送握手与读取命令，不擦写 Flash。`probe` 返回身份但不保证 `confirmed_k2` 为真，调用者仍须检查。`Updater` 是一次性会话，probe 后不能在同一实例继续 flash；备份与擦写流程应使用后台已有的新连接 / 身份绑定顺序。

## 资源读写事务

资源类型为 `startup`、`background`、`layout`、`emark`、`emark-copy`。推荐流程：

1. JSON `devices` 获取接口与序列号，`probe` 获取身份摘要。
2. `resource-read` 导出有效结构并建立完整扇区双遍备份。
3. 离线编辑有效结构，保留未知字段，验证并计算 SHA-256。
4. 用户明确确认后，调用 `resource-write`，传原身份摘要和编辑文件摘要。
5. 后台再次核对身份，备份当前完整分配区，合并尾部、擦写、完整读回，才返回成功。

底层 `write_resource` 执行擦写和读回；备份与身份校验由上层事务完成。完整调用流程见 [JSON 接口](bridge.md)。

## 文件编辑和记录

- `.k2` 使用 `Firmware.load / parse`；格式校验不认证来源。
- `.pic` 使用 `resource_for('layout').validate`；编辑已识别记录，保留其他字节。
- RGB565 图片数据包含首尾标记，不是 PNG / JPEG；编码见图片专题。
- `.wtemark` 使用 `validate_record`；集合使用 `validate_bank`，不要把 JSON 工程作为二进制集合写入。
- 记录使用 `Recording` 和 `Sample`；查询用 `query_record`，导入导出用 `import_record / export_record`。

[可运行离线示例](../examples/README.md) 演示三种常见开发路径。文件路径由上层应用选择并校验。

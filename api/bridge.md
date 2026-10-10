# JSON / NDJSON 进程接口

这是独立上位机的本地接口。启动 `python3 k2_gui_backend.py`，向 stdin 写一行 UTF-8 JSON，以换行结束；stdout 每行是一个 JSON 事件。普通操作一请求一进程；`monitor` 保持进程和 stdin 开放，以便发送后续控制。

## 公共请求和事件

```json
{"id":"12345678-1234-4234-8234-123456789abc","operation":"devices","simulation":true}
```

| 字段 | 类型 / 默认 | 契约 |
| --- | --- | --- |
| `id` | UUID 字符串，必填 | 关联事件；不是设备协议请求 ID |
| `operation` | 字符串，必填 | 下表操作之一 |
| `simulation` | bool，默认 false | 仅部分操作支持模拟；monitor 不支持 |
| `demo_delay_ms` | int，默认 20 | 0…100；模拟进度延迟 |
| `fault` | null 或字符串 | 模拟故障：`verify`、`disconnect`、`batch-nack`；不要对真实流程依赖此字段 |
| `data_directory` | 路径字符串 | 写日志 / 备份的操作必填；模拟写入在其 `Offline Demo/` 子目录 |

成功事件：`ready` → 零或多个 `progress` / `paths` / `identity` / `monitor` → `result`。所有事件包含 `schema:1`、原 `id`、`operation` 和 `event`。

```json
{"schema":1,"id":"12345678-1234-4234-8234-123456789abc","operation":"devices","event":"result","value":{"devices":[],"simulation_only":false}}
```

结果必须读取 `value`。失败发送 `event:error`，含 `stage`、`message`、`cancelled`，进程通常退出 1，取消退出 130；正常退出 0。请求超过 262144 字符会被拒绝。读取到 `ready` 或 100% progress 不代表操作成功，必须等待 `result` 和退出码。

## 全部操作

除注明默认值的字段外，下表列出的操作字段均必填；公共 `id / operation` 仍需提供。副作用“文件写”不代表设备写。

| operation | 用途 / 副作用 | 操作字段 | result.value 主要字段 |
| --- | --- | --- | --- |
| `devices` | 枚举接口；真实模式访问 HID | 无 | `devices`、`simulation_only`；每项有 `path_hex`、`serial_number`、USB 标识 |
| `inspect` | 离线校验固件；文件读 | `firmware_path` | `firmware`、绝对 `firmware_path`、`demo_firmware` |
| `firmware-extract` | 校验已下载 ZIP 并保存其中固件；文件写 | `firmware_path`、`data_directory`、`firmware_version` | `firmware`、`firmware_path`、`demo_firmware:false`；不负责下载 |
| `demo-firmware` | 生成合成固件；文件写 | `data_directory`、`simulation:true` | `firmware`、`firmware_path`、`simulation_only:true` |
| `probe` | DFU 握手 / 只读身份；日志写 | `data_directory`、真实设备选择字段 | `identity`、`device`、`trace`、`simulation_only` |
| `backup` | DFU 双遍应用备份；日志 / 文件写 | `data_directory`、设备选择字段、`dfu_confirmed:true` | `backup`、`identity`、`trace`、`simulation_only` |
| `upgrade` | 先备份再升级；设备 / 文件写 | backup 字段 + `confirmed:true`、`firmware_path`、`firmware_sha256`、`device_info_sha256` | `identity`、`backup`、`firmware`、`stage:complete`、验证与模拟标记 |
| `resource-read` | 双遍读取资源；完整扇区备份与导出，文件写 | `data_directory`、设备选择字段、`dfu_confirmed:true`、`resource_kind` | `backup`、`resource_path`、`resource_kind`、`resource_valid`、`resource_error`、`identity`、`trace` |
| `resource-write` | 备份、保留尾部、擦写、完整比较 | resource-read 字段 + `confirmed:true`、`device_info_sha256`、`resource_path`、`resource_sha256` | `backup`、`resource_kind`、`verified_sha256`、`stage:complete`、身份 / 日志 |
| `resource-restore` | 验证旧备份，备份当前区，再恢复 | resource-read 字段 + `confirmed:true`、`device_info_sha256`、`restore_manifest`、`restore_manifest_sha256` | 同 resource-write；`verified_sha256` 是完整分配区的摘要 |
| `monitor` | 普通模式被动读取，预览 / 记录文件写 | `data_directory`、`device_path_hex`、`device_serial`；记录采样率由后续 start 控制设置 | 周期 `monitor.value` 状态，断开后最终 `result.value` 采集状态 |
| `monitor-query` | 本地记录查询；文件读 | `record_path`；可选 `range_start`、`range_end`、`include_stats` 默认 true | 记录摘要、`points`、区间；非空且统计开启时含 `statistics` / `full_statistics` |
| `monitor-import` | CSV / SQLite 转本地记录；文件写 | `record_path`、`output_path` | `path`、`count` |
| `monitor-export` | 导出本地记录；文件写 | `record_path`、`output_path`、`export_kind`；可选范围 | `path`；kind = `csv` / `official-sqlite` / `local-sqlite` |
| `monitor-list` | 列举本地记录；文件读 | `data_directory` | `records`；其 `Recordings/` 下最近至多 200 个 SQLite，坏记录跳过 |

`resource_kind` = `startup` / `background` / `layout` / `emark` / `emark-copy`。字段时间单位为电脑经过秒数；路径由调用应用提供，不来自网络 URL。

### 真实设备选择与身份

`probe / backup / upgrade / resource-*` 的真实选择字段为 `device_path_hex` 和 `device_serial`，均从 `devices` 当前结果取得；序列号即使是 null 也应原样传递。probe 不要求 `dfu_confirmed`，但设备必须确实处于 DFU。其他上述操作要求 `dfu_confirmed:true`。模拟操作跳过真实选择；写入的 `confirmed` 与摘要校验仍生效。

`identity` 包含 `boot_strings`、`info_sha256`、`confirmed_k2`、`current_version`、`current_marker_hex`。后台拒绝未确认 K2；写入前将 `info_sha256` 传作 `device_info_sha256`。它是身份一致性摘要，不是加密认证。

`resource-read` 可成功备份尚未初始化 / 无效的结构，此时 `resource_valid:false`；不能把这个 result 误当作结构可供直接编辑。

### 备份结果

应用 `backup` 从 `0x08000000` 读取至 `0x080E3000`（不含），包含 Bootloader / 信息前缀与应用区。元数据含 `identity`、`flash_start`、`flash_end_exclusive`、`flash_size`、`flash_sha256`、`app_sha256`、`bootloader_and_info_sha256`、`two_independent_reads_match`、`recovery_file`、`recovery`、`recovery_flash_hardware_validated:false`、`erase_or_write_commands_sent:false`。精确键见 [backup_device](../k2up/backup.py)。资源 `backup` 包含 `schema:1`、`type:k2-resource-backup`、`kind`、`address`、`allocation`、`data_size`、`sha256`、`identity`、`two_reads_match`、`simulation_only`、`directory`。恢复读取同目录的 `sectors.bin`，不能只保存 manifest。

## 无设备调用示例

```python
import json, subprocess, sys, uuid
request = {'id': str(uuid.uuid4()), 'operation': 'devices', 'simulation': True}
process = subprocess.run(
    [sys.executable, 'k2_gui_backend.py'],
    input=json.dumps(request) + '\n', text=True, capture_output=True, check=True)
events = [json.loads(line) for line in process.stdout.splitlines()]
result = next(e['value'] for e in events if e['event'] == 'result')
print(result['devices'][0]['path_hex'])
```

可运行版本见 [bridge_demo.py](../examples/bridge_demo.py)。真实资源读取的请求模板：

```json
{
  "id":"12345678-1234-4234-8234-123456789abc",
  "operation":"resource-read",
  "data_directory":"/absolute/path/to/app-data",
  "device_path_hex":"<devices 返回的 path_hex>",
  "device_serial":"<devices 返回的 serial_number，或 null>",
  "dfu_confirmed":true,
  "resource_kind":"layout"
}
```

占位值必须换成当前枚举结果；该操作连接设备但不擦写。

## monitor 的长连接控制

首行请求为 `monitor`，保持 stdin 开放。以下行是控制 JSON，不再需要 UUID 或 operation：

| command | 字段 | 主机行为 |
| --- | --- | --- |
| `start` | `rate` = 0 / 1 / 10 / 100；可选 `path`、`auto_kind`、`threshold`、`duration` | 建立新记录；0 保留所有真实报告。已有记录时拒绝 |
| `pause` | 无 | 提交并暂停正式记录；预览继续 |
| `resume` | 无 | 继续记录，创建新 segment；未暂停则拒绝 |
| `stop` | 无 | 完成当前记录，保持实时预览 |
| `disconnect` | 无 | 停止记录、关闭 HID，结束进程 |

自动停止 kind 为 `current`（绝对 A）或 `power`（非负 W），threshold 与 duration 均非负；duration 为秒，0 禁用。低于阈值连续足够时长才停止，不向设备设置电流 / 功率。

`monitor.value` 常见字段：`recording`、`paused`、`record_path`、`record_count`、`latest`、`received`、`invalid`、`unmatched`、`checksum_matches`、`receive_rate`、`elapsed`、`stale`。控制确认含 `control_ack`；部分控制错误以 `notice` 返回，仍须检查状态，不能把 ACK 名称当成功状态。结束时只有采集状态字段，不保证继续包含 latest / 计数诊断。

## 错误处理与部署边界

摘要变化、身份变化、坏帧、备份落盘失败、读回不一致均停止流程。失败后不要自动重新擦写；显示 stage 和 message，保留已有备份路径。stderr 与退出码用于进程诊断，stdout 专用于事件。

JSON schema 当前为 1，无独立语义版本承诺；集成时固定仓库提交并保留回归测试。该后台允许操作本地路径，不适合直接暴露为未鉴权 HTTP 服务。应用负责可信文件选择、用户确认、权限和 USB 独占。

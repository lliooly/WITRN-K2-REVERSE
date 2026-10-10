# Python 逐函数参考

接口分为离线格式处理、设备 transport / Protocol、完整业务流程、记录采集、模拟工具和后台内部实现。参数默认值直接对应源码签名。类型 / 单位由各条职责说明和 [设备契约](device-commands.md) 给出。

本页覆盖所有 `k2up/*.py` 中显式定义的非下划线函数、方法、属性和构造器；下划线私有方法及 dataclass 自动生成构造器不作为手工公开接口。目录完整不意味着所有非下划线内部函数都是稳定 SDK。集成应优先使用下方核心契约或 [JSON 后台](bridge.md)。

## 核心调用契约

| 接口 | 前置条件与输入 | 输出 | 主要异常 / 调用约束 |
| --- | --- | --- | --- |
| `Protocol(transport, timeout_ms=1000)` | transport 提供 write(frame)->64、read(ms)->规范化帧；DFU 调用时设备已在 DFU | 同步协议实例 | ValueError 超时范围；设备相关方法 ProtocolError / OSError；串行、无自动重试 |
| `Firmware.parse(raw)` | bytes，为编码后的 .k2 容器而非解码应用镜像 | Firmware，含 source/app/date/version/model_guid | FirmwareError(ValueError) 格式 / 型号 / 大小 / 标记 / 向量失败 |
| `Updater.probe()` | 新一次性实例，DFU transport | Identity | UpgradeError(stage,message)；probe 后实例不能继续 flash，confirmed_k2 应核查 |
| `Updater.flash(firmware)` | 新一次性实例，可信 Firmware；调用者已落实备份和确认 | Identity，stage=complete | 真实 Flash 写；不自行备份，不得用演示固件写实机 |
| `backup_resource(...)` | 固定 Resource、Identity、新目录、progress 回调 | (完整分配区 bytes, metadata) | 两遍不一致 / 落盘失败中止；后续写入须独立验证 payload |
| `decode_report(raw, elapsed)` | 64/65 字节输入，elapsed 非负电脑秒数 | Sample 或其他命令 None | ValueError 非法遥测，ProtocolError 非法输入长度；不访问 USB |
| `Recording(path, rate=10, extra=None)` | 新路径；rate 仅作元数据，采样由 Sampler/Capture 完成 | Recording | OSError/sqlite3.Error；需 close，单线程使用连接 |
| `query_record(...)` | 本地 schema 1 记录；start/end 为闭区间秒数 | dict(points,统计,摘要...) | ValueError/sqlite3.Error/OSError，取消 InterruptedError；空记录统计 None |

`Sample` 构造器字段与单位见 [遥测输出](device-commands.md#普通遥测输出)。`Packet` 含 command:int、payload:bytes、raw:bytes；`Resource` 含 kind、address、size、sectors、dimension；`Identity` 含 boot_strings、info_sha256、可选当前版本与标记。完整 `Firmware` 建议由 parse/load 产生，避免手动构造绕过验证。

## 逐模块函数

异常列表只列函数源码中显式 `raise` 的异常类；依赖调用还可能传播 OSError、ProtocolError、ValueError、sqlite3.Error 等，不构成完整异常穷举。以 [失败契约](device-commands.md#失败契约与版本范围) 和源码为准。

### transport

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`enumerate_devices()`](../k2up/transport.py#L19) | 枚举指定 VID / PID 的当前 HID 接口 | HIDAPI dict 列表 | USB 枚举 | 依赖调用 / 无显式 raise |
| [`device_summary(device)`](../k2up/transport.py#L23) | 转换设备条目为 JSON 可序列化摘要，路径转十六进制 | dict，含 path_hex | 离线 | 依赖调用 / 无显式 raise |
| [`select_device(devices, path_hex=None)`](../k2up/transport.py#L31) | 按 path_hex 过滤并要求唯一接口，验证 VID / PID | 设备 dict | 离线选择 | OSError |
| [`normalize_input(raw)`](../k2up/transport.py#L48) | 接受 64 字节或零 Report ID + 64 字节；空输入保留为空 | bytes(64) 或 b'' | 离线 | ProtocolError |
| [`HidTransport(selected)`](../k2up/transport.py#L60) | 按 selected['path'] 打开唯一设备，检查 VID / PID | 实例 | 打开 USB | OSError |
| [`HidTransport.write(frame)`](../k2up/transport.py#L71) | 发送 64 字节协议帧，补零 Report ID 并核验写入长度 | 64；异常则未完整发送 | 设备写报告，效果取决于命令 | ProtocolError |
| [`HidTransport.read(timeout_ms)`](../k2up/transport.py#L80) | timeout_ms 毫秒；0 临时非阻塞读取 | 规范化 bytes 或空 bytes | 设备读 | 依赖调用 / 无显式 raise |
| [`HidTransport.close()`](../k2up/transport.py#L91) | 释放 HID 句柄 | None | 关闭 USB | 依赖调用 / 无显式 raise |

### protocol

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`build_frame(command, payload=b'', *, reply=True, tick=None)`](../k2up/protocol.py#L16) | 编码完整 64 字节帧；command 0…255、payload ≤52；reply 决定请求响应位，tick 为毫秒 | bytes(64) | 离线 | ValueError |
| [`parse_frame(raw)`](../k2up/protocol.py#L38) | 核验长度、魔数、负载和双校验 | Packet(command, payload, raw) | 离线 | ProtocolError |
| [`Protocol(transport, timeout_ms=1000)`](../k2up/protocol.py#L53) | 绑定 transport；timeout_ms 1…60000 | Protocol 实例 | 不立即 I/O | ValueError |
| [`Protocol.drain()`](../k2up/protocol.py#L59) | 非阻塞清理日志，拒绝旧 ACK / 错误包 | None | 设备读 | ProtocolError |
| [`Protocol.command(command, payload=b'')`](../k2up/protocol.py#L95) | 发送控制命令并等成功 ACK；不是通用数据查询 | None | 设备控制，取决于 command | 依赖调用 / 无显式 raise |
| [`Protocol.erase_sector(address)`](../k2up/protocol.py#L100) | 发送一个地址的擦除请求；须合法扇区且已开批次 | None；未等单扇区 ACK | 设备擦除 | 依赖调用 / 无显式 raise |
| [`Protocol.write_memory(address, data)`](../k2up/protocol.py#L105) | 地址 + bytes，拆成最多 40 字节包；须已擦除且开批次 | None；未等单包 ACK | 设备写 | 依赖调用 / 无显式 raise |
| [`Protocol.read_memory(address, size)`](../k2up/protocol.py#L112) | address 为字节地址，size 1…1024 | 恰好 size 个 bytes，否则异常 | 设备读请求 | ProtocolError, ValueError |
| [`Protocol.read_marker(address)`](../k2up/protocol.py#L127) | 从指定地址短读 4 字节 | bytes(4) | 设备读请求 | ProtocolError |

### firmware

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`Firmware.parse(raw: bytes)`](../k2up/firmware.py#L36) | 解析 encoded 容器；检查头、日期、型号、大小、校验、未提交标记及向量 | Firmware | 离线 | FirmwareError |
| [`Firmware.load(path)`](../k2up/firmware.py#L77) | 从 path 读取并调用 parse | Firmware | 文件读 | 依赖调用 / 无显式 raise |
| [`Firmware.from_app(app, release=None)`](../k2up/firmware.py#L81) | 从应用 bytes 构造恢复容器，清提交标记、修剪 FF 尾、保留对齐；release 为 date | Firmware；不是厂商发行版 | 离线 | FirmwareError |
| [`Firmware.erase_addresses`](../k2up/firmware.py#L103) | 按整个容器长度计算 2 KiB 擦除地址 | tuple[int]，属性 | 离线 | 依赖调用 / 无显式 raise |
| [`Firmware.chunks(size=1024)`](../k2up/firmware.py#L108) | 按 size 字节分组应用正文；size 应为正，设备流程使用 1024 | 迭代 (address, bytes) | 离线 | 依赖调用 / 无显式 raise |
| [`Firmware.summary()`](../k2up/firmware.py#L112) | 型号、版本、日期、大小、摘要、地址和提交信息 | dict | 离线 | 依赖调用 / 无显式 raise |

### updater

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`UpgradeError(stage, message)`](../k2up/updater.py#L10) | 包装错误 stage 与 message | 异常对象 | 离线 | 依赖调用 / 无显式 raise |
| [`Identity.confirmed_k2`](../k2up/updater.py#L23) | 检查三个名称字符串之一是否匹配已识别 K2 名称 | bool，属性 | 离线 | 依赖调用 / 无显式 raise |
| [`Identity.summary()`](../k2up/updater.py#L26) | 导出名字、信息摘要、当前版本与标记 | dict | 离线 | 依赖调用 / 无显式 raise |
| [`Updater(protocol, progress=None)`](../k2up/updater.py#L34) | 绑定 Protocol 与 progress(stage,current,total)，每实例只执行一次流程 | 实例 | 不立即 I/O | 依赖调用 / 无显式 raise |
| [`Updater.probe()`](../k2up/updater.py#L61) | 握手并读信息、名称、应用版本和标记；未知型号可返回但须检查 confirmed_k2 | Identity | DFU 控制 + 只读，无 Flash 写 | UpgradeError |
| [`Updater.flash(firmware)`](../k2up/updater.py#L77) | 重新校验 Firmware，识别设备、擦写、完整读回、提交、退出；自身不做备份 | Identity；stage 为 complete | 真实 Flash 写，模拟取决于 transport | ProtocolError, UpgradeError, ValueError |

### backup

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`backup_device(updater, directory)`](../k2up/backup.py#L14) | 用新的 updater 身份探测，双遍读取 Bootloader / 信息前缀与完整应用范围，落盘摘要与恢复容器；directory 须不存在 | 备份 manifest dict | 设备只读 + 文件写；不证明恢复已实机验证 | ProtocolError, UpgradeError |

### picture

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`Resource.allocation`](../k2up/picture.py#L23) | sectors × 2048，字节数 | int，属性 | 离线 | 依赖调用 / 无显式 raise |
| [`Resource.addresses`](../k2up/picture.py#L27) | 分配区每个 2 KiB 扇区起点 | range，属性 | 离线 | 依赖调用 / 无显式 raise |
| [`Resource.validate(data)`](../k2up/picture.py#L30) | 核验精确有效长度、标记及类型字段；资源不是原始 PNG / JPEG | 有效结构 bytes | 离线 | ValueError |
| [`resource_for(kind)`](../k2up/picture.py#L63) | 按 startup/background/layout/emark/emark-copy 查固定资源 | Resource | 离线 | ValueError |
| [`sha(data)`](../k2up/picture.py#L70) | 对 bytes 计算 SHA-256 | 64 字符十六进制 str | 离线 | 依赖调用 / 无显式 raise |

### emark

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`validate_record(data)`](../k2up/emark.py#L9) | 66 字节、名字结束符、PD 编码与末尾校验 | bytes(66) | 离线 | ValueError |
| [`validate_bank(data)`](../k2up/emark.py#L21) | 666 字节、有效计数与默认索引，仅校验活动槽 | bytes(666) | 离线 | ValueError |
| [`sample_record(name='K2 configuration')`](../k2up/emark.py#L33) | 生成合成记录；ASCII 名称 ≤18 字节 | bytes(66) | 离线样例，非认证配置 | ValueError |
| [`sample_bank()`](../k2up/emark.py#L47) | 生成单个合成记录的集合，保留其余 FF 槽位 | bytes(666) | 离线样例 | 依赖调用 / 无显式 raise |

### picture_device

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`read_all(protocol, resource, progress, stage)`](../k2up/picture_device.py#L11) | 固定 Resource，按 ≤1024 读取完整 allocation，调用 progress | 完整分配区 bytes | 设备读 | ValueError |
| [`durable_write(path, data)`](../k2up/picture_device.py#L23) | path 为 Path，排他创建、flush、fsync | None | 文件写，不覆盖 | 依赖调用 / 无显式 raise |
| [`backup_resource(protocol, resource, identity, directory, progress, simulation=False)`](../k2up/picture_device.py#L30) | 新目录内保存双遍一致的完整扇区和 identity 元数据；simulation 标记来源 | tuple(完整 bytes, manifest dict) | 设备读 + 文件写 | ProtocolError |
| [`load_backup(path, manifest_data=None)`](../k2up/picture_device.py#L59) | 读取 manifest 与同目录 sectors.bin，验证大小、摘要、范围与 K2 身份字段 | tuple(Resource, bytes, metadata) | 文件读 | ValueError |
| [`write_resource(protocol, resource, image, progress)`](../k2up/picture_device.py#L84) | image 必须覆盖全部 allocation；擦除、写入、比较、退出；不自带备份或身份核验 | None，失败抛异常 | 设备擦写 | ProtocolError, ValueError |
| [`transfer_resource(request, events, protocol, identity, directory)`](../k2up/picture_device.py#L112) | 后台内部完整资源操作；request 含桥接预先验证的私有 payload 字段 | 资源结果 dict | 按 operation 读或擦写 + 文件写 | ValueError |

### telemetry

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`Sample.dictionary()`](../k2up/telemetry.py#L31) | 把 Sample 字段转 dict；单位见设备契约 | dict | 离线 | 依赖调用 / 无显式 raise |
| [`decode_report(raw, elapsed)`](../k2up/telemetry.py#L35) | 解析普通报告；elapsed 为电脑经过秒数，有限且非负；其他命令返回 None | Sample 或 None；坏遥测抛 ValueError | 离线 | ValueError |
| [`dfu_checksum_matches(raw)`](../k2up/telemetry.py#L62) | 规范化报告并检查两个累加和；名字不限制其用于已验证遥测 | bool；非法帧长度可能异常 | 离线 | 依赖调用 / 无显式 raise |
| [`Sampler(rate=10)`](../k2up/telemetry.py#L70) | 主机采样率 0/1/10/100，0 不限速 | 实例 | 离线 | ValueError |
| [`Sampler.accept(time)`](../k2up/telemetry.py#L76) | 经过秒数进入新时间槽则接受，不补造样本 | bool | 主机状态变更 | ValueError |

### recording

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`readonly(path)`](../k2up/recording.py#L16) | path 须存在，打开 mode=ro/query_only 的 SQLite | sqlite3.Connection；调用者关闭 | 文件读 | 依赖调用 / 无显式 raise |
| [`metadata(db)`](../k2up/recording.py#L25) | 读取至多 100 项 metadata，缺表为空 | dict[str,str] | 数据库读 | 依赖调用 / 无显式 raise |
| [`validate_local(db)`](../k2up/recording.py#L32) | 验证 schema 与 samples 表 / 必要字段 | None | 数据库读 | ValueError |
| [`samples(db, start=None, end=None)`](../k2up/recording.py#L42) | 按经过秒数闭区间 start/end 迭代，按 time/id 排序 | 迭代 Sample | 数据库读 | 依赖调用 / 无显式 raise |
| [`Recording(path, rate=10, extra=None)`](../k2up/recording.py#L53) | path 不得存在；rate 记元数据，extra 可补元数据；本类不负责采样限速 | 实例 | 创建 SQLite/WAL | 依赖调用 / 无显式 raise |
| [`Recording.append(sample)`](../k2up/recording.py#L80) | 写一个 Sample，检查必要数值；不会替调用者分段或采样 | None；count 增长 | 数据库写 | ValueError |
| [`Recording.commit()`](../k2up/recording.py#L95) | 提交待写样本并更新时间 | None | 数据库写 | 依赖调用 / 无显式 raise |
| [`Recording.close(complete=True)`](../k2up/recording.py#L98) | complete=True 标记完成，提交并关闭；异常流程用 false | None | 数据库写 / 关闭 | 依赖调用 / 无显式 raise |
| [`summary(path)`](../k2up/recording.py#L110) | 检查本地记录并计算计数、时间范围、元信息 | dict | 文件读 | 依赖调用 / 无显式 raise |

### recording_files

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`elapsed_text(value)`](../k2up/recording_files.py#L20) | 非负经过秒数转 D.hh:mm:ss.mmm 风格文本 | str | 离线 | 依赖调用 / 无显式 raise |
| [`parse_time(text)`](../k2up/recording_files.py#L29) | 解析官方时间 / Excel 风格时间文本 | 经过秒数 float | 离线 | ValueError |
| [`number(text, optional=False)`](../k2up/recording_files.py#L41) | 把数值文本转有限数；optional 允许缺值 | float 或 None | 离线 | ValueError |
| [`row_sample(row)`](../k2up/recording_files.py#L50) | 把官方列字典转样本；派生有符号与非负功率 | Sample | 离线 | ValueError |
| [`csv_source(path, meta)`](../k2up/recording_files.py#L61) | 解析 BOM/元信息/列标题，meta 由调用者传空 dict 并被填充 | 生成器 Sample | 文件读 | ValueError |
| [`sqlite_source(path, meta)`](../k2up/recording_files.py#L85) | 读取官方或本地 SQLite，填充 meta | 生成器 Sample | 文件读 | ValueError |
| [`import_record(source, destination, cancelled=lambda : False)`](../k2up/recording_files.py#L113) | CSV/SQLite 转新本地记录，destination 不得存在；cancelled 返回 bool | dict(path,count) | 文件读 / 新文件写 | InterruptedError, ValueError |
| [`export_record(source, destination, kind, start=None, end=None, cancelled=lambda : False)`](../k2up/recording_files.py#L158) | 本地记录导出 csv/official-sqlite/local-sqlite；范围单位秒；cancelled 可取消 | dict(path) | 文件读 / 原子替换目标，可能覆盖 | InterruptedError, ValueError |

### recording_stats

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`direction_area(a, b, dt)`](../k2up/recording_stats.py#L9) | 对端点 a/b 数值及 dt 秒积分，分离正负面积 | tuple(正面积,负面积) | 离线 | 依赖调用 / 无显式 raise |
| [`interpolate(a, b, t)`](../k2up/recording_stats.py#L18) | 同一时间段内用 a/b Sample 插值至 t 秒 | Sample | 离线 | 依赖调用 / 无显式 raise |
| [`statistics(items, start=None, end=None, gap_limit=2, cancelled=lambda : False)`](../k2up/recording_stats.py#L30) | 有序样本区间统计，跨 segment 或 gap_limit 秒断点不积分 | 统计 dict；Ah/Wh、覆盖秒数和通道统计 | 离线，消耗迭代器 | InterruptedError |
| [`plot_points(items, start, end, budget=6000, cancelled=lambda : False)`](../k2up/recording_stats.py#L78) | 为有序样本保留各时间桶首尾与通道极值，budget 是目标桶预算而非严格输出上限 | list[Sample dict] | 离线，消耗迭代器 | InterruptedError |
| [`query_record(path, start=None, end=None, include_stats=True, cancelled=lambda : False, budget=6000)`](../k2up/recording_stats.py#L103) | 本地文件区间查询；可选统计，默认 budget 6000；桥接用 1200 | 摘要、points、统计等 dict；空记录 statistics=None | 文件读 | ValueError |

### monitor

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`AutoStop(kind='current', threshold=0, duration=0)`](../k2up/monitor.py#L21) | kind current/power，阈值 A/W，duration 秒，0 关闭 | 实例 | 离线 | ValueError |
| [`AutoStop.reset()`](../k2up/monitor.py#L27) | 清除连续低阈值计时 | None | 主机状态变更 | 依赖调用 / 无显式 raise |
| [`AutoStop.accept(sample)`](../k2up/monitor.py#L29) | 判断 Sample 是否已连续低于阈值足够秒数 | bool | 主机状态变更 | 依赖调用 / 无显式 raise |
| [`Capture(directory, rate=10)`](../k2up/monitor.py#L38) | 记录目录与主机采样率；不立即新建记录 | 实例 | 不立即文件写 | 依赖调用 / 无显式 raise |
| [`Capture.control(command)`](../k2up/monitor.py#L51) | start/pause/resume/stop 字典；字段见桥接控制表 | None | 主机状态与记录文件写 | ValueError |
| [`Capture.stop(complete=True)`](../k2up/monitor.py#L71) | 结束当前记录，complete=false 保留异常标记 | None | 文件写 / 关闭 | 依赖调用 / 无显式 raise |
| [`Capture.feed(sample)`](../k2up/monitor.py#L79) | 接收 Sample，分段、采样、记录和自动停止 | tuple(带 segment 的 Sample,自动停止 bool) | 主机状态 / 可能记录写 | 依赖调用 / 无显式 raise |
| [`Capture.state()`](../k2up/monitor.py#L96) | 当前或刚关闭记录状态 | dict(recording,paused,record_path,record_count) | 离线 | 依赖调用 / 无显式 raise |
| [`run_monitor(request, events, input_stream, transport_factory=HidTransport)`](../k2up/monitor.py#L102) | 桥接内部普通模式实时采集，input_stream 提供控制行，transport_factory 可注入 | 最终 Capture.state dict | 设备被动读 + 文件写；只宜在子进程主线程使用 | OSError, ValueError |

### official_firmware

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`import_archive(path, directory, expected_version)`](../k2up/official_firmware.py#L10) | 读本地 ZIP，要求唯一 .k2、大小与 expected_version 匹配，拒绝演示固件 | dict(firmware,firmware_path,demo_firmware) | 文件读 / 新文件写；不下载 | ValueError |

### gui_bridge

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`Events(request, output=None)`](../k2up/gui_bridge.py#L29) | 绑定 request 与输出流，进度起点 preflight | 实例 | 不立即输出 | 依赖调用 / 无显式 raise |
| [`Events.emit(event, **fields)`](../k2up/gui_bridge.py#L36) | 发送带 schema/id/operation 的一行事件 JSON，立即 flush | None | 流写 | 依赖调用 / 无显式 raise |
| [`Events.progress(stage, current=0, total=0)`](../k2up/gui_bridge.py#L42) | 阶段进度去重并发送事件，可能记 trace | None | 流 / 日志写 | 依赖调用 / 无显式 raise |
| [`validate_request(request)`](../k2up/gui_bridge.py#L56) | 检查操作、UUID、模拟字段、确认与模式前置字段 | None | 离线 | ValueError |
| [`selected_device(request)`](../k2up/gui_bridge.py#L84) | 按请求选择真实 / 模拟接口，核对序列号 | 设备 dict | 真实模式枚举 USB | ValueError |
| [`connection(request, events, trace, demo=None)`](../k2up/gui_bridge.py#L94) | 内部上下文管理器，构建 trace transport / updater，退出关句柄 | 上下文 yield (Updater,device) | 开 / 关 USB 或模拟 | 依赖调用 / 无显式 raise |
| [`verify_identity(identity, request)`](../k2up/gui_bridge.py#L104) | 要求 confirmed_k2，若提供预期摘要则比较 | None | 离线 | ValueError |
| [`dispatch(request, events, input_stream=None)`](../k2up/gui_bridge.py#L112) | 已公开 JSON 操作的分派；request 和 Events，monitor 需输入流 | 操作结果 dict | 按 operation 决定 | ValueError |
| [`updater_identity(backup)`](../k2up/gui_bridge.py#L269) | 把备份 identity 字段转模型 | Identity | 离线 | 依赖调用 / 无显式 raise |
| [`main(input_stream=None, output=None)`](../k2up/gui_bridge.py#L276) | 读取一行请求、发 ready/result/error，monitor 继续读控制 | 退出码 0/1/130 | 按 operation 决定 | ValueError |

### demo

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`demo_firmware(version=88)`](../k2up/demo.py#L7) | 生成版本 byte（默认 0x58）的合成应用容器 | Firmware | 离线，禁止真实设备写 | 依赖调用 / 无显式 raise |
| [`is_demo_firmware(firmware)`](../k2up/demo.py#L15) | 识别与合成模板匹配的容器，含恢复版本 | bool | 离线 | 依赖调用 / 无显式 raise |
| [`DemoTransport()`](../k2up/demo.py#L23) | 建立含合成旧应用的模拟 Flash | 实例 | 内存模拟 | 依赖调用 / 无显式 raise |
| [`demo_device()`](../k2up/demo.py#L36) | 生成模拟 HID 枚举条目 | dict | 离线 | 依赖调用 / 无显式 raise |

### simulator

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`SimulatedTransport(*, model='K2', fault=None)`](../k2up/simulator.py#L14) | model 和故障标记构造主机流程模拟器；不是 Bootloader 时序仿真 | 实例 | 内存 | 依赖调用 / 无显式 raise |
| [`SimulatedTransport.write(frame)`](../k2up/simulator.py#L49) | 解析请求并模拟命令与失败响应 | 64 | 内存写，不访问 USB | OSError, ProtocolError |
| [`SimulatedTransport.read(timeout_ms)`](../k2up/simulator.py#L130) | 取模拟队列下一帧，timeout_ms 不模拟真实时序 | bytes 或 b'' | 内存读 | 依赖调用 / 无显式 raise |
| [`SimulatedTransport.close()`](../k2up/simulator.py#L133) | 满足 transport 关闭契约 | None | 内存 | 依赖调用 / 无显式 raise |

### picture_simulator

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`PictureTransport(*, fault=None)`](../k2up/picture_simulator.py#L10) | 构造五类资源的模拟区，支持 fault | 实例 | 内存 | 依赖调用 / 无显式 raise |
| [`PictureTransport.write(frame)`](../k2up/picture_simulator.py#L35) | 扩展资源范围与命令状态模拟 | 64 | 内存，不访问 USB | OSError, ProtocolError |

### cli

| 签名 / 源码 | 用途与输入 | 返回值 | 副作用 | 显式异常 |
| --- | --- | --- | --- | --- |
| [`Trace(path)`](../k2up/cli.py#L18) | 创建新 JSONL 日志 path，不覆盖 | 实例 | 文件写 | 依赖调用 / 无显式 raise |
| [`Trace.event(kind, **fields)`](../k2up/cli.py#L23) | 附 UTC 时间输出日志记录 | None | 文件写 | 依赖调用 / 无显式 raise |
| [`Trace.close()`](../k2up/cli.py#L27) | 关闭日志 | None | 文件关闭 | 依赖调用 / 无显式 raise |
| [`TracedTransport(transport, trace)`](../k2up/cli.py#L32) | 包装 transport 记录通信 | 实例 | 不立即 I/O | 依赖调用 / 无显式 raise |
| [`TracedTransport.write(raw)`](../k2up/cli.py#L36) | 记录发送尝试和结果并转发 | 底层写入计数 | 设备写报告 + 日志写 | 依赖调用 / 无显式 raise |
| [`TracedTransport.read(timeout_ms)`](../k2up/cli.py#L42) | 转发读取并记录非空回包 | bytes | 设备读 + 日志写 | 依赖调用 / 无显式 raise |
| [`Progress(trace=None)`](../k2up/cli.py#L50) | 构造 CLI 进度回调，可带 Trace | 可调用实例 | 不立即输出 | 依赖调用 / 无显式 raise |
| [`record_failure(trace, kind, **fields)`](../k2up/cli.py#L64) | 尽可能记录失败，日志错误输出 stderr 不掩盖原错 | None | 日志 / stderr 写 | 依赖调用 / 无显式 raise |
| [`parser()`](../k2up/cli.py#L72) | 构造 argparse 命令定义 | ArgumentParser | 离线 | 依赖调用 / 无显式 raise |
| [`main(argv=None)`](../k2up/cli.py#L99) | 处理 CLI 参数；设备动作和确认要求见 --help | 退出码 0/1/130；argparse 可 SystemExit | 按子命令决定 | ValueError |

## 完整流程示例

[sdk_demo.py](../examples/sdk_demo.py) 演示帧 / 固件 / 模拟升级和遥测；[recording_demo.py](../examples/recording_demo.py) 演示记录 / 区间统计 / 文件交换；[bridge_demo.py](../examples/bridge_demo.py) 演示跨语言进程入口。真实只读例子见 [接入路径](integration.md)。

底层地址方法没有完整型号 / 备份保护，不能把 `Protocol.write_memory` 的返回当作业务写入成功。`gui_bridge`、`transfer_resource` 等是内部组合实现，应用优先调用已定义 JSON 操作，避免自行填充 request 私有字段。

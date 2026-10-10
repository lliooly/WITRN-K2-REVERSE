# 静态分析与离线复现

## 环境与输入

Python 3.9 或以上；核心测试仅用标准库。`.NET` 分析另需：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-analysis.txt
```

`dnfile`、`dncil`、`pefile`、`pycryptodome` 是研究依赖，尚未固定版本，不承诺任意版本兼容。ILSpy 和 IDA 是独立工具；脚本不安装或调用它们，也不会运行厂商 Windows 程序。使用者需自行取得有权分析的输入。

| 输入 | SHA-256 | 用途 |
| --- | --- | --- |
| `WITRNUP.dll` | `315d274a3c8a1d546174b0f0566089377b278810a20a46bb817f14a75e4c0a37` | UP V30 托管程序集 |
| `uthiducs.dll` | `a5c0287b6a922ce239020a3cfba8be8efe3527d2655829b0fbd35417f38cfff0` | 本地 HID 封装分析 |
| `K2_APP_5.8.k2` | `15d280b385f5899c4c31ea5587ede6e286fecb48783a14764155f7b892c3de9c` | 固件容器样本 |
| `K2Picture_1.1/K2Picture.dll` | `afce3b147aee09187ef4c95b4fe6f9f9dcc62eb2b5d0cec857eb49b173d520af` | 图片与表盘格式 |
| `WITRN_PC_V1.0.4/WITRN.exe` | `1260bf387882900d97a47f06c929222eb8f67db4cdb2b4cc46c2fec4a21c8e6e` | Qt 上位机与交换格式 |

仅第一项用于以下托管恢复流水线。把其放到仓库根目录；原文件被 `.gitignore` 排除。

## UP V30 执行顺序

在根目录按依赖顺序执行：

```sh
.venv/bin/python reverse/inspect_dotnet.py 440 665 1768
.venv/bin/python reverse/unpack_static.py
.venv/bin/python reverse/restore_methods.py
.venv/bin/python reverse/extract_tables.py
.venv/bin/python reverse/extract_delegates.py
.venv/bin/python reverse/parse_vm.py
.venv/bin/python reverse/inspect_firmware.py /path/to/K2_APP_5.8.k2 --output-dir /tmp/k2-firmware-analysis
```

先导出 IL 方法与资源，再静态解释方法资源、重建方法体、导出格式表、恢复代理、解析 VM。最后的固件研究脚本依赖 `reverse/tables/` 的解码表与扇区表；普通离线解析命令 `python3 -m k2up inspect ...` 使用随库保留的小型协议表，不需要这条恢复流水线。

脚本中 RID、资源 RVA、局部变量编号、输入路径和预期记录数对应上述特定 DLL。其他版本需重新定位；失败时检查来源哈希与报错，不应强行取消断言。历史成功摘要见 [evidence](../evidence/README.md)。发布核验只重新执行合成测试及离线输入检查，没有重新运行全部托管恢复流水线。

## K2Picture 与 Qt 上位机

相关静态分析的 RID、地址和字段依据已保存在 [K2Picture 报告](../reverse/K2PICTURE.md)、[E-Mark 报告](../reverse/K2EMARK.md) 和 [上位机调查](k2-monitor-research.md)。K2Picture 资源恢复使用过针对它的 RID / 资源和 local 53 调整；现有 UP V30 脚本尚未参数化以直接支持 K2Picture。Qt 程序的分析记录包含函数地址，但没有完整自动分析脚本。

因此这两部分能复核具体格式依据，尚不能一键复现全部静态分析。这是当前资料的实际缺口，不代表已包含恢复源码或全部 VM 语义。

## 离线与实机区分

`python3 -m unittest discover -s tests -v` 使用合成输入和内存模拟器；`inspect` 和 `dry-run` 不访问 USB。`devices` 会枚举接口；`probe`、`backup` 和研究测速会连接实机；`flash` 会擦写，必须显式声明 DFU 与确认参数。资料核验工作没有执行任何实机操作。

完整命令帮助见 `python3 -m k2up --help`。设备使用范围与未验证事项见 [validation.md](validation.md)。

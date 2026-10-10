# WITRN K2 逆向研究

本库按研究问题组织逆向成果：**分析对象 → 方法恢复 → 协议与格式 → 关键函数证据 → 验证结果**。每个主题解释结论、来源函数、数据布局、操作流程和验证状态；文件清单作为附录。

## 阅读顺序

| 顺序 | 主题 | 内容 |
| --- | --- | --- |
| 0 | [对象与证据](research/README.md) | 区分三个程序及静态、模拟、实机依据 |
| 1 | [方法恢复](research/01-method-recovery.md) | 占位 IL、资源、代理映射、VM 与 C# 导出 |
| 2 | [固件与 DFU](research/02-firmware-dfu.md) | 固件格式、HID 帧、升级事务、地址关系 |
| 3 | [表盘与图片](research/03-picture.md) | .pic、RGB565、资源分配与函数链 |
| 4 | [虚拟 E-Mark](research/04-emark.md) | 单条、集合、电脑工程与备份扇区 |
| 5 | [遥测与文件交换](research/05-monitor-files.md) | 原生函数、报告、采样、CSV / SQLite |
| 6 | [关键函数与 C# 索引](research/functions/README.md) | 职责、RID / token / 地址与方法元数据 |
| 7 | [验证状态](docs/validation.md) | 已验证范围与真实缺口 |

例如研究开机图：先看资源结构，沿 RID 530 → 531 看像素转换，沿写入封装 → RID 400 / 406 → 411 看传输链，再看原报告的实机结果。

## 材料分层

- `research/`：按主题重写的正文；`research/functions/`：关键职责及完整方法 / 代理元数据索引。
- `reverse/`：详细报告和静态工具；`docs/`：完整协议、实测、复现与技术设计。
- `k2up/`、`tests/`：独立参考实现及合成 / 模拟检查。
- `evidence/`：历史分析摘要与发布核验。
- `archive/application/`：原应用 UI 和打包背景附录。
- `third_party/`：代码来源与许可；`tools/`：发布清单工具。

[逐文件附录](CATALOG.md) 按用途分组，[MANIFEST.json](MANIFEST.json) 提供大小和 SHA-256。

## C# 函数整理程度

函数索引包含重点 worker、擦写 / 读取封装、恢复入口、K2Picture 函数组与原生入口。UP V30 的 **1269 条恢复方法与 574 组代理**提供限定名、token 及地址定位，不包含完整 C# 函数体。索引说明各个本地导出文件的用途、复现方式、未重新核验条目和一处 token / RID 关系疑点。

## 离线复现

Python 3.9 或以上，在仓库根目录运行：

```sh
python3 -m unittest discover -s tests -v
python3 tools/manifest.py --check
python3 -m k2up --help
```

这些命令不访问 USB。固件检查与模拟使用自行取得的本地输入：

```sh
python3 -m k2up inspect /path/to/K2_APP.k2
python3 -m k2up dry-run /path/to/K2_APP.k2
```

输入哈希、依赖和步骤见 [复现指南](docs/reproduction.md)。K2Picture 工具尚未参数化，Qt 无完整自动脚本；真实写入和恢复限制见验证状态。

## 来源与公开范围

整理日期为 2026-10-10，原成果来自 [应用仓库](https://github.com/lliooly/witrn-k2-updater-re)，来源提交见 [snapshot.json](evidence/snapshot.json)。原应用设计是历史背景，不替代协议与实测证据。

厂商程序、固件、恢复 DLL、完整反编译、IDA 数据库、设备备份、序列号和原始日志留在本地；公开材料采用报告、必要协议表、函数定位、脚本和合成测试，详见 [材料来源](docs/materials.md)。

## 许可证与侵权联系删除

原创代码和文档使用标准 [MIT](LICENSE)。第三方代码保留原许可；厂商材料、协议表和商标范围见 [NOTICE.md](NOTICE.md)。MIT 不授予我们无权许可的第三方内容。

**如有侵权，请联系删除。** 权利人可通过 [Issues](https://github.com/lliooly/witrn-k2-research/issues/new) 提供具体文件、权属依据和联系方式。维护者会核查，对确有侵权或授权不足的内容及时删除、修改或下架。不宜公开的版权投诉可使用 [GitHub 官方入口](https://github.com/contact/dmca)，详见 [TAKEDOWN.md](TAKEDOWN.md)。

联系删除声明不替代授权。本项目为独立研究，与 WITRN 无隶属关系，未获厂商认可或赞助。

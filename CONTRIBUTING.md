# 贡献说明

提交协议修正时，请注明分析输入版本 / SHA-256、字段偏移、方法 RID 或函数地址、可复核步骤及验证类型。区分静态推断、合成测试、实机读取和实机擦写；不要把模拟成功表述为硬件兼容。

请勿上传厂商安装包、官方固件、恢复 DLL、完整反编译代码、IDA 数据库、真实设备备份、序列号、USB 路径、通信日志或私人图片。新增测试使用合成数据。第三方改编须保留来源、版权和原许可证。

提交前运行：

```sh
python3 -m unittest discover -s tests -v
python3 tools/verify_api.py
python3 examples/sdk_demo.py
python3 examples/bridge_demo.py
python3 examples/recording_demo.py
python3 tools/manifest.py
python3 tools/manifest.py --check
```

原创贡献沿用项目 MIT；第三方和厂商材料按其实际权利状态声明。删除请求见 [TAKEDOWN.md](TAKEDOWN.md)。

接口变化须同步 `api/` 的参数、返回、副作用、错误和示例。逐函数清单与 JSON 操作通过 `tools/verify_api.py` 核对；文档说明接口行为、来源证据、复现步骤和验证范围。

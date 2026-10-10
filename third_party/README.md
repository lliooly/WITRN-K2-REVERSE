# 第三方代码来源

`k2up/telemetry.py` 的遥测字段定义改编自 [didim99/witrn-driver](https://github.com/didim99/witrn-driver)，版本 `2729a02cde172631e36ad5be5a13a8bd1492ce0e`，Copyright (c) 2022 didim99。上游 MIT 全文见 [witrn-driver-LICENSE.txt](witrn-driver-LICENSE.txt)。

修改：使用显式小端解析，增加报告长度、命令、有限数值和双校验检查；保留有符号电流 / 功率；传输使用本项目 HIDAPI，不采用上游 PyUSB 的 USB reset 和接口接管。记录、文件交换、统计和模拟实现来自原应用项目。

厂商协议替换表的来源和许可边界见 [NOTICE.md](../NOTICE.md)。本研究库不包含原应用的 GPL DFU 插图或其他应用图片。

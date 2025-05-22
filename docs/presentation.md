---
marp: true
<!-- theme: default -->

<style>
section {
  font-family: 'Noto Sans SC', sans-serif;
}
</style>

<!-- Load the font from Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap" rel="stylesheet">
---

# 行动不如心动


----
# 项目目标

- 了解 MCP 的边界
- 如何帮助LLM扩展边界
- 深入学习MCP

----

# 项目实现

- 基于BLE HRM的 MCP 服务
- 系统提示词利用MCP产生业务价值

---

# 技术细节

## 蓝牙心率带 or 运动手表

- 通过Python蓝牙的SDK
- 通过BLE HRM Profile 进行资源过滤
- BLE的心率协议仅支持 `订阅` 模式
- 实现的`In Memory TSDB`
	- 时间间隔的采样
	- 固定时间段的平均心率

----
# 技术MCP部分

## 协议映射
- 资源 : `BLE://HRM`，了解List Resource协议
## 工具
- 连接蓝牙手表（如果不用资源协议）
- 获取心率（最近10秒的平均）
- 获取活动心率（最近1分钟的最高心率）

---

![](<sequence.png>)

---
# 使用场景

## 心脏健康程度 = 运动后恢复心率的高低
- 恢复心率 = 最高心率 - 休息两分钟后的心率
## 用大语言模型的系统提示词来完成交互和反馈

---
# 扩展的需求

- 按照不同的间隔获取长时间心率
- 通过心率获取，建立心率图 - 上传Qiniu云并支持下载
- 支持更低的模型支持，并更好支持DeepChat

---
# 后续的价值

蓝牙作为普遍的一个通讯协议，LLM拥有更多操作周边IoT设备的能力
感知外界信息，并与外界交互

----
# 源码地址

https://github.com/linzitao/ble-hrm-server
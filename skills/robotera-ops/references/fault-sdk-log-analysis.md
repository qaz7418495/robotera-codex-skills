<title>SDK log 日志分析释义</title>

<callout emoji="📍">
在终端中查看log信息：`cat 日志文件名`  
主要看红色打印信息，黄色打印信息为辅助查看，其他颜色可忽略
</callout>

# **SDK日志路径**

- **自启动日志保存路径**：`/system_log/log/dynamic_launch`[图片已省略]

  - 注：日志文件名的时间戳，目前需要加8小时才是正确时间

当前路径下的日志目录下，有以年月日命名的日志子目录，子目录下的日志文件为以具体的SDK启动时间：年月日时分秒 命名

- **最新的SDK启动日志保存路径**：`/system_log/log/xbot_control`

[图片已省略]

当前目录下的日志文件，主要看 xbot.log ，该文件中存放有最新的 SDK 日志，包括开机自启动的

# **log 日志下载**

1. ROOT方式获取：ssh 登陆 NUC，从终端拉取`/system_log/log/xbot_control/`
2. 前端页面获取：从XOS上拉取，打开浏览器输入 http://192.168.8.100:1888/

[图片已省略]

# **错误释义**

# SDK 1.0

## **常见错误**

### **Failed to configure controller**[图片已省略]

- 错误原因：重复启动SDK
- 解决方法：重启 ros2_dev docker 容器
- 查看方式：先看红字提示控制器配置失败，再看黄字提示已经加载了控制器

### **UNDER_VOLT**[图片已省略]

- 错误原因：低电压错误
- 解决方式：一般是电量过低，需要充电

### **xxx joint is missing**![图片展示的是SDK log日志分析释义文档中“xxx joint is missing”错误的查看方式示例。画面中显示了多行日志信息，其中红字部分“\[ERROR\] \[9815665999\] \[resource_manager\]: failed to initialize hardware 'l3'”及黄字部分“\[ERROR\] \[9815665999\] \[resource_manager\]: failed to initialize hardware 'l3' from plugin 'obot_hardware_interface/RobotHardwareInterface' failed to initialize hardware configuration.”尤为突出，表明控制器初始化硬件失败，是该错误的查看方式示例。](media-omitted)

- 错误原因：有关节丢失
- 解决方式：排查对应线束接口是否断开或者虚接

### **DRV error**[图片已省略]

- 错误原因：驱动器错误
- 查看方式：中间多行信息中显示了错误name和msg，msg中表述了“Joint module DRV error”

### **ENC_ERROR**[图片已省略]

- 错误原因：电机编码器报错
- 查看方式：电机编码器总共有三级报错信息，一级为ENC_ERROR，二级、三级报错有多种报错

此示例中的一级错误码为0x20，二级为0x80，三级为c0（此处三级错误码全称是0xc0，0x代表十六进制）

### **连续 wkc: -1**![图片展示的是xbot_nuc@xbot-NUC:~$终端界面，显示了大量“\[ERROR\] \[1761806436...1720976840\] \[EthercatBusBase\]: Slave left shoulder pitch_joint is offline, state: 0”等错误信息。这些错误信息表明机器人的左肩pitch关节、左肩roll关节、左肘pitch关节、左肘roll关节、左腕pitch关节、左腕roll关节、右肩pitch关节、右肩roll关节、右肘pitch关节、右肘roll关节、右腕pitch关节、右腕roll关节均处于离线状态，状态为0。该图片与文档中“连续wkc:-1”错误相关，图片直观呈现了该错误在终端的日志表现。](media-omitted)

- 错误原因：机器关节线束中存在破损或者断开问题

### **Error reading SDO**[图片已省略]

- 错误原因：关节 SDO 配置失败
- 解决方式：整机重启SDK，如果仍然报错，需要维修人员排查关节模组问题

### **DRIVE_OVER_TEMP**[图片已省略]

- 错误原因：驱动器温度过高

## **其他错误**

[图片已省略]

可能是背后急停被拍了或是被D了。

# SDK 2.0

- 电源板串口异常[图片已省略]
- EC 状态切换失败：可能是模组固件版本太低；之前固件升级失败；模组没有正常写入名称[图片已省略]
- 关节阶跃：关节收到了≥0.628弧度（36度）[图片已省略]
- ENC 报错，需要根据 ENC 二级报错来确认具体情况[图片已省略]
- 关节模组未上电，急停遥控器D一下[图片已省略]
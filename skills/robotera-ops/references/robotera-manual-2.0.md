<title>ROBOTERA 机器人操作手册 2.0</title>

# **使用注意事项**

- 禁止 XOS 启动 SDK 和脚本启动 SDK 两种方式混用！否则会导致 SDK 启动失败！
- 软件最低适配版本

  | 功能名称 | 最低版本 | 功能名称 | 最低版本 | 功能名称 | 最低版本 | 功能名称 | 最低版本 |
  |-|-|-|-|-|-|-|-|
  | SDK | 2.0.18 | XOS | 2.0.5 | MPC |  | RL |  |
  | 导航 |  | 沙盒服务 | 2.0.1 |  |  |  |  |
- 使用命令行过程中，复制命令可能会导致格式变化，此时建议尝试手动敲命令
- 当前B4机型在非标零情况下，禁止使用PD模式；标零过程中（**PD模式**），需要两人手扶机器左右大臂，先把下肢摆到极限位置锁定抱闸以后，再对上肢安装标零工装
- 更换灵巧手以后，需要重启 ros2_dev 容器（【**仅内部使用**】）或者整机重启（通用操作）

---

# Log 记录

## LOG 拉取

<grid>
<column width-ratio="0.500000">
打开浏览器输入 http://192.168.8.100:1888/，点击 “打包下载当前文件夹”，也可以根据情况点击相应目录，单独下载目标目录
</column>
<column width-ratio="0.500000">
[图片已省略]
</column>
</grid>

## LOG 分析释义【**仅内部使用**】

<cite doc-id="AsP9whAqUiV62EkJaHjc5Ki3n6c" file-type="wiki" title="SDK log 日志分析释义" type="doc"></cite>

# 版本号查看

## 系统版本【**仅内部使用**】

在宿主机下输入 `echo $ROBOTERA_OS_VERSION`

## 软件版本

<grid>
<column width-ratio="0.500000">
打开浏览器输入 http://192.168.8.100:1888/，在“系统升级”页面查看所有软件的版本号
</column>
<column width-ratio="0.500000">
[图片已省略]
</column>
</grid>

---

# **操作说明**

## 整机开机

长按机器底盘（背部）银色开关，直至机器底盘（头部）LED灯带亮起

---

## SDK 启动操作

### 方式一：标准模式（XOS 设置开机自启动）

<grid>
<column width-ratio="0.500000">
打开浏览器输入 http://192.168.8.100:1888/，在“机器人管理”页面，“启动管理”，在“请选择启动模式”中下拉选择框，选择“标准模式”，并点击“设置开机自启动模式”，最后重启整机  
  
当前默认使用 位置模式
</column>
<column width-ratio="0.500000">
[图片已省略]
</column>
</grid>

### 方式二：开发者模式（手动启动）

<grid>
<column width-ratio="0.500000">
打开浏览器输入 http://192.168.8.100:1888/，在“机器人管理”页面，“启动管理”，在“请选择启动模式”中下拉选择框，选择“开发者模式”，并点击“设置开机自启动模式”，最后重启整机
  
当前默认使用 位置模式
</column>
<column width-ratio="0.500000">
[图片已省略]
</column>
</grid>

#### 方式一：远程登录

1. 可通过无线方式或者有线方式登陆

   - 无线方式：连接 WiFi
   
     - WiFi 名称: `*_BOT*_5G`（例如：WR_v1_BOT3_5G，对应 B4-3 机器）
     - WiFi 密码: `xbot123456`
   - 有线方式：使用网线，一端连接机器底盘（背部）的网口，另一端连接笔记本网口
2. 登录 NUC 

   ###### **ROOT 用户登陆【仅内部使用】**

   - 登录命令：`ssh xbot_nuc@192.168.8.100`
   - 初始登录密码：`xbot123456`

   ###### **developer 用户登陆**

   - 登录命令：`ssh developer@192.168.8.100 -p 2222`
   - 初始登录密码：`developer`

#### 方式二：显示器直连 NUC【**仅内部使用**】

- 先使用支持视频传输的 Type-C 线，一端连接机器底盘（背部）的 Type-C 口，另一端连接欧米多（便携式显示器，神器）
- 连接好后，再启动开关按钮
- 系统启动后，会显示输入用户名的字段：输入用户名 `xbot_nuc` ，回车后输入密码 `xbot123456`，进入后输入 `startx`进入图形化界面

#### 总体启动流程

##### ROOT 用户操作【**仅内部使用**】

###### 基础启动

```bash
# 新开一个终端

# ROOT 登陆 NUC 后，进入 docker 中
ssh xbot_nuc@192.168.8.100
# 输入登录密码（第一次登录有可能需要输入 yes）

# 进入docker环境
./go_to_docker.sh
```

###### SDK 启动

<callout emoji="⚠️">
当前默认为 位置模式，如果要使用其他模式，修改 /root/xbot/config.json: "mode" 修改为对应需要的模式
position 对应为 位置模式
pd 对应为 PD模式
velocity 对应为 速度模式
</callout>

```bash
# 启动 SDK
./sdk.sh

# 新开终端，进入 Ready 状态
./ready.sh

# 关节初始化
./initpose_handsdown.sh

# 进入 Activate 模式（可以运行算法相关操作）
./activate.sh
```

##### developer 用户操作

```Bash
# developer 登陆 NUC 后，启动 SDK 
ros2 service call /dynamic_launch xbot_common_interfaces/srv/DynamicLaunch "app_name: ''
sync_control: false
launch_mode: 'pos'"

# 进入 Ready 状态
ros2 service call /ready_service std_srvs/srv/Trigger {}

# 关节初始化
ros2 action send_goal /simple_actions xbot_common_interfaces/action/SimpleActions "{action_name: 'initpose_handsdown', time_cost: 4.0}"

# 进入 Activate 模式（可以运行算法相关操作）
ros2 service call /activate_service std_srvs/srv/Trigger {}
```

# SDK 整机维护操作

## config.json 说明

<table><colgroup><col/><col/></colgroup><thead><tr><th vertical-align="middle"><b>参数名称</b></th><th vertical-align="middle"><b>参数说明</b></th></tr></thead><tbody><tr><td>auto_start</td><td>自启动设置<br/><code>true</code>表示开机自启动<br/><code>false</code>表示关闭开机自启动</td></tr><tr><td>enable_developer</td><td>设置为<code>true</code>后，会取消自动配置机型和手类型，建议仿真环境设置为<code>true</code><br/><code>true</code>表示自动配置整机机型及手类型<br/><code>false</code>表示不自动配置</td></tr><tr><td>l3_mode</td><td>主要针对于 <code>l3.4</code> 真机机型使用，此值会在真机情况下覆盖 <code>mode</code> 参数值，参考值如下<br/><code>pd</code> 力控模式<br/><code>position</code> 位置模式<br/><code>velocity</code> 速度模式</td></tr><tr><td>mode</td><td>SDK 启动类型<br/><code>sim</code> 仿真模式<br/><code>pd</code> 力控模式<br/><code>position</code> 位置模式<br/><code>velocity</code> 速度模式</td></tr><tr><td>robot_type</td><td>整机机型，仿真时，修改该值就可以切换成不同机型<br/><code>l3.4</code> L7 <br/><code>wr1</code> B4/Q5<br/><code>m7</code> M7 数采半身机器<br/><code>m7.1</code>凯龙-固定立柱<br/><code>w7</code> 凯龙-升降立柱<br/><code>l3.4.3</code> 马拉松机型</td></tr><tr><td>hardware_type</td><td>是否有灵巧手，仿真必须为有手<br/><code>hand</code> 有手<br/><code>no_hand</code>无手</td></tr><tr><td>hand_type</td><td>灵巧手类型<br/><code>xhand</code>：可用机型 l3.4，wr1，m7，m7.1，w7<br/><code>lite</code> ：可用机型 wr1，l3.4.3<br/><code>green</code> ：可用机型 l3.4，m7</td></tr><tr><td colspan="2" vertical-align="middle"><b>以下参数一般不改，保持默认</b></td></tr><tr><td>launch_mode</td><td>xos启动模式</td></tr><tr><td>use_mpc_controller</td><td>mpc自启动</td></tr><tr><td>use_rl_controller</td><td>ri自启动</td></tr><tr><td>lift_joint_mode</td><td>立柱模式<br/><code>position</code> 位置模式<br/><code>velocity</code> 速度模式</td></tr></tbody></table>

## 整机/关节基本信息获取

### 查看整机系统及关节总信息【**仅内部使用**】

```Bash
# 基础启动下，运行以下脚本
./system_info_dump.sh
```

### 获取 SDK 版本

```Bash
ros2 service call /get_sdk_version xbot_common_interfaces/srv/GetVersion {}
```

- 命令行查看（仿真情况）【**仅内部使用**】

```Bash
cat /root/xbot/hardware/install/xbot_ros2/share/xbot_ros2/package.xml | grep "<version>"
```

### 自研关节SN码

#### 获取关节 SN 码（包含肢体关节和手关节）

- 一般获取

  ```Bash
  ros2 service call /get_joint_sn xbot_common_interfaces/srv/GetJointState {}
  ```
- 在 `/etc/xbot/xbot_sn.json` 生成 SN 文件【**仅内部使用**】

  - 运行前必须关闭SDK

  ```Shell
  ros2 run xbot_tools read_joints_sn
  ```

#### 设置关节 SN 码（关节下线时使用，包含肢体关节和手关节）【**仅内部使用**】

- 运行前必须关闭SDK
- 修改完 SN 码后需要运行一下，生成关节 SN 文件的命令
- 记得执行下面的命令

```Shell
ros2 run  xbot_tools set_joints_sn
```

### SDK 状态

- 获取状态

```Bash
ros2 service call /query_xbot_state xbot_common_interfaces/srv/QueryState {}

# 反馈值对应关系如下
INIT   = 0
IDLE   = 2
READY  = 3
ACTIVE = 4
ERROR  = -1
```

- 进入 Ready 状态

```Bash
ros2 service call /ready_service std_srvs/srv/Trigger {}
```

- 进入 Activate 状态

```Bash
ros2 service call /activate_service std_srvs/srv/Trigger {}
```

- 退出 Activate 状态，进入 Ready 状态

```Bash
ros2 service call /deactivate_service std_srvs/srv/Trigger {}
```

### 关节列表

<table><colgroup><col/><col/><col/><col/></colgroup><thead><tr><th colspan="4" vertical-align="middle"><b>B4</b></th></tr></thead><tbody><tr><td vertical-align="middle"><b>中文名称</b></td><td vertical-align="middle"><b>英文名称</b></td><td vertical-align="middle"><b>中文名称</b></td><td vertical-align="middle"><b>英文名称</b></td></tr><tr><td vertical-align="middle"><b>左肩pitch</b></td><td>left_shoulder_pitch_joint</td><td vertical-align="middle"><b>右肩pitch</b></td><td>right_shoulder_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左肩roll</b></td><td>left_shoulder_roll_joint</td><td vertical-align="middle"><b>右肩roll</b></td><td>right_shoulder_roll_joint</td></tr><tr><td vertical-align="middle"><b>左大臂yaw</b></td><td>left_arm_yaw_joint</td><td vertical-align="middle"><b>右大臂yaw</b></td><td>right_arm_yaw_joint</td></tr><tr><td vertical-align="middle"><b>左肘pitch</b></td><td>left_elbow_pitch_joint</td><td vertical-align="middle"><b>右肘pitch</b></td><td>right_elbow_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左肘yaw</b></td><td>left_elbow_yaw_joint</td><td vertical-align="middle"><b>右肘yaw</b></td><td>right_elbow_yaw_joint</td></tr><tr><td vertical-align="middle"><b>左腕pitch</b></td><td>left_wrist_pitch_joint</td><td vertical-align="middle"><b>右腕pitch</b></td><td>right_wrist_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左腕roll</b></td><td>left_wrist_roll_joint</td><td vertical-align="middle"><b>右腕roll</b></td><td>right_wrist_roll_joint</td></tr><tr><td vertical-align="middle"><b>踝</b></td><td>ankle_joint</td><td vertical-align="middle"><b>腰yaw</b></td><td>waist_yaw_joint</td></tr><tr><td vertical-align="middle"><b>膝</b></td><td>knee_joint</td><td vertical-align="middle"><b>脖子yaw</b></td><td>neck_yaw_joint</td></tr><tr><td vertical-align="middle"><b>髋</b></td><td>hip_joint</td><td vertical-align="middle"><b>脖子pitch</b></td><td>neck_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左手(掌心板）</b></td><td vertical-align="middle">left_hand_palm</td><td vertical-align="middle"><b>右手（掌心板）</b></td><td vertical-align="middle">right_hand_palm</td></tr><tr><td vertical-align="middle"><b>车轮</b></td><td vertical-align="middle">wheel</td><td vertical-align="middle"></td><td vertical-align="middle"></td></tr></tbody></table>

<table><colgroup><col/><col/><col/><col/></colgroup><thead><tr><th colspan="4" vertical-align="middle"><b>M7</b></th></tr></thead><tbody><tr><td vertical-align="middle"><b>中文名称</b></td><td vertical-align="middle"><b>英文名称</b></td><td vertical-align="middle"><b>中文名称</b></td><td vertical-align="middle"><b>英文名称</b></td></tr><tr><td vertical-align="middle"><b>左肩pitch</b></td><td>left_shoulder_pitch_joint</td><td vertical-align="middle"><b>右肩pitch</b></td><td>right_shoulder_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左肩roll</b></td><td>left_shoulder_roll_joint</td><td vertical-align="middle"><b>右肩roll</b></td><td>right_shoulder_roll_joint</td></tr><tr><td vertical-align="middle"><b>左大臂yaw</b></td><td>left_arm_yaw_joint</td><td vertical-align="middle"><b>右大臂yaw</b></td><td>right_arm_yaw_joint</td></tr><tr><td vertical-align="middle"><b>左肘pitch</b></td><td>left_elbow_pitch_joint</td><td vertical-align="middle"><b>右肘pitch</b></td><td>right_elbow_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左肘yaw</b></td><td>left_elbow_yaw_joint</td><td vertical-align="middle"><b>右肘yaw</b></td><td>right_elbow_yaw_joint</td></tr><tr><td vertical-align="middle"><b>左腕pitch</b></td><td>left_wrist_pitch_joint</td><td vertical-align="middle"><b>右腕pitch</b></td><td>right_wrist_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左腕roll</b></td><td>left_wrist_roll_joint</td><td vertical-align="middle"><b>右腕roll</b></td><td>right_wrist_roll_joint</td></tr><tr><td vertical-align="middle"><b>腰pitch</b></td><td>waist_pitch_joint</td><td vertical-align="middle"><b>腰yaw</b></td><td>waist_yaw_joint</td></tr><tr><td vertical-align="middle"><b>腰roll</b></td><td>waist_roll_joint</td><td vertical-align="middle"></td><td></td></tr><tr><td vertical-align="middle"><b>脖子yaw</b></td><td>neck_yaw_joint</td><td vertical-align="middle"><b>脖子pitch</b></td><td>neck_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左手(掌心板）</b></td><td vertical-align="middle">left_hand_palm</td><td vertical-align="middle"><b>右手（掌心板）</b></td><td vertical-align="middle">right_hand_palm</td></tr></tbody></table>

<table><colgroup><col/><col/><col/><col/></colgroup><thead><tr><th colspan="4" vertical-align="middle"><b>L3</b></th></tr></thead><tbody><tr><td vertical-align="middle"><b>中文名称</b></td><td vertical-align="middle"><b>英文名称</b></td><td vertical-align="middle"><b>中文名称</b></td><td vertical-align="middle"><b>英文名称</b></td></tr><tr><td vertical-align="middle"><b>左肩pitch</b></td><td>left_shoulder_pitch_joint</td><td vertical-align="middle"><b>右肩pitch</b></td><td>right_shoulder_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左肩roll</b></td><td>left_shoulder_roll_joint</td><td vertical-align="middle"><b>右肩roll</b></td><td>right_shoulder_roll_joint</td></tr><tr><td vertical-align="middle"><b>左大臂yaw</b></td><td>left_arm_yaw_joint</td><td vertical-align="middle"><b>右大臂yaw</b></td><td>right_arm_yaw_joint</td></tr><tr><td vertical-align="middle"><b>左肘pitch</b></td><td>left_elbow_pitch_joint</td><td vertical-align="middle"><b>右肘pitch</b></td><td>right_elbow_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左肘yaw</b></td><td>left_elbow_yaw_joint</td><td vertical-align="middle"><b>右肘yaw</b></td><td>right_elbow_yaw_joint</td></tr><tr><td vertical-align="middle"><b>左腕pitch</b></td><td>left_wrist_pitch_joint</td><td vertical-align="middle"><b>右腕pitch</b></td><td>right_wrist_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左腕roll</b></td><td>left_wrist_roll_joint</td><td vertical-align="middle"><b>右腕roll</b></td><td>right_wrist_roll_joint</td></tr><tr><td vertical-align="middle"><b>腰pitch</b></td><td>waist_pitch_joint</td><td vertical-align="middle"><b>腰yaw</b></td><td>waist_yaw_joint</td></tr><tr><td vertical-align="middle"><b>腰roll</b></td><td>waist_roll_joint</td><td vertical-align="middle"></td><td></td></tr><tr><td vertical-align="middle"><b>脖子yaw</b></td><td>neck_yaw_joint</td><td vertical-align="middle"><b>脖子pitch</b></td><td>neck_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左手(掌心板）</b></td><td vertical-align="middle">left_hand_palm</td><td vertical-align="middle"><b>右手（掌心板）</b></td><td vertical-align="middle">right_hand_palm</td></tr><tr><td vertical-align="middle"><b>左腿髋yaw</b></td><td>left_hip_yaw_joint</td><td vertical-align="middle"><b>右腿髋yaw</b></td><td>right_hip_yaw_joint</td></tr><tr><td vertical-align="middle"><b>左腿髋roll</b></td><td>left_hip_roll_joint</td><td vertical-align="middle"><b>右腿髋roll</b></td><td>right_hip_roll_joint</td></tr><tr><td vertical-align="middle"><b>左腿髋pitch</b></td><td>left_hip_pitch_joint</td><td vertical-align="middle"><b>右腿髋pitch</b></td><td>right_hip_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左膝</b></td><td>left_knee_joint</td><td vertical-align="middle"><b>右膝</b></td><td>right_knee_joint</td></tr><tr><td vertical-align="middle"><b>左脚踝pitch</b></td><td>left_ankle_pitch_joint</td><td vertical-align="middle"><b>右脚踝pitch</b></td><td>right_ankle_pitch_joint</td></tr><tr><td vertical-align="middle"><b>左脚踝roll</b></td><td>left_ankle_rollr_joint</td><td vertical-align="middle"><b>右脚踝roll</b></td><td>right_ankle_roll_joint</td></tr></tbody></table>



---

### 保存关节名称【**仅内部使用**】

- 运行前需要先停止 SDK

```Bash
# 关闭 SDK
ros2 service call /stop_launch std_srvs/srv/Trigger {}

# 保存关节名称
./save_joint_names.sh

# SDK ≥ 2.0.56 无需执行以下操作
# 启动 SDK
./sdk.sh
./ready.sh

# 保存参数
ros2 service call /save_param std_srvs/srv/Trigger {}
```

---

### 获取关节模组版本

```Bash
ros2 service call /get_joints_version xbot_common_interfaces/srv/GetVersion {}
```

## 关节配置

### 关节抱闸

<callout emoji="✴️">
目前包含抱闸的机型：B4，M7.1，W7
</callout>

#### 解抱闸

```Shell
# 服务调用：joint_name 填入 需要配置的抱闸名称，填入几个抱闸名称就相应在 param_value 中填入几个 1
ros2 service call /control_brake xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ['ankle_joint']
param_value: [1]"

# 脚本调用，以 open_brake_ 为前缀的脚本【仅内部使用】
```

#### 锁抱闸

```Shell
# 服务调用：joint_name 填入 需要配置的抱闸名称，填入几个抱闸名称就相应在 param_value 中填入几个 0
ros2 service call /control_brake xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ['ankle_joint']
param_value: [0]"

# 脚本调用，以 close_brake_ 为前缀的脚本【仅内部使用】
```

### 固件升级

#### 固件版本号获取

##### 关节版本号

```Bash
ros2 service call /get_joints_version xbot_common_interfaces/srv/GetVersion {}
```

##### 电源板版本号

```Bash
ros2 service call /Battery/GetVersion xbot_common_interfaces/srv/GetVersion {}
```

#### 整机关节升级【**仅内部使用**】

将要升级的固件文件放到 nuc 中的`/opt/xbot/hardware/firmware`目录（宿主机目录，非docker）下面，如果目录不存在就使用下面的命令创建，**注意要将所有.bin文件放在firmware路径下，不能有二级目录或者其他文件，如果firmware文件夹下已经有升级文件，需要删除这些文件**

```Bash
sudo mkdir /opt/xbot/hardware/firmware
```

##### ROS2 服务调用升级

1. 基础启动下，启动sdk
2. 调用升级服务

   1. 所有关节：

   ```Bash
   ros2 service call /update_joints std_srvs/srv/Trigger {}
   ```

   1. 单关节（以车轮为例）：

   ```Bash
   ros2 service call /update_joint xbot_common_interfaces/srv/UpgradeJoint "joint_name: 'wheel'"
   ```
3. 服务返回成功以后重启sdk

##### 单程序调用升级（版本要求：SDK ≥ 2.0.44）

<callout emoji="⚠️">
适用于低于0.1.37.40的关节固件版本升级，需要先停止SDK，关节重新上下一次电
</callout>

```Shell
# 停止 SDK
ros2 service call /stop_launch std_srvs/srv/Trigger {}
# 关节下电
ros2 service call /Battery/SetElectricState xbot_common_interfaces/srv/SetElectricState "electric_type: 1
state: 0"
# 关节上电
ros2 service call /Battery/SetElectricState xbot_common_interfaces/srv/SetElectricState "electric_type: 1
state: 1"
# 升级成功
ros2 run xbot_tools joint_update
```

#### 电源板升级【**仅内部使用**】

- 无需启动 SDK
- 将要升级的电源板固件文件放到 nuc 中的`/opt/xbot/hardware/firmware`目录（宿主机目录，非docker）下面，如果目录不存在就使用下面的命令创建

```Bash
sudo mkdir /opt/xbot/hardware/firmware
```

- 打开电源板输出日志，查看升级过程

```Bash
tail -f /system_log/log/xbot_control/battery_out.log
```

- 进入 ros2_dev 容器，调用电源板升级服务

```Bash
./go_to_docker.sh

ros2 service call /upgrade_battery std_srvs/srv/Trigger {}
```

---

### 整机关节 PID 标定

- 一般用于新关节，或者关节转动过程中有异响

#### 整机设置【**仅内部使用**】

```bash
./send_pid_all.sh
```

#### 单关节设置与获取（以waist_roll_motor_joint 为例，数值是随机值，具体以实际情况为准）

```Bash
# 位置 KP 设置
ros2 service call /set_pos_kp xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ["waist_roll_motor_joint"]
param_value: [42]"
# 位置 KP 获取
ros2 service call /get_pos_kp xbot_common_interfaces/srv/GetJointIntegerParam {}
# 速度 KP 设置
ros2 service call /set_vel_kp xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ["waist_roll_motor_joint"]
param_value: [42]"
# 速度 KP 获取
ros2 service call /get_vel_kp xbot_common_interfaces/srv/GetJointIntegerParam {}

# 位置 KI 设置
ros2 service call /set_pos_ki xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ["waist_roll_motor_joint"]
param_value: [42]"
# 位置 KI 获取
ros2 service call /get_pos_ki xbot_common_interfaces/srv/GetJointIntegerParam {}
# 速度 KI 设置
ros2 service call /set_vel_ki xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ["waist_roll_motor_joint"]
param_value: [42]"
# 速度 KI 获取
ros2 service call /get_vel_ki xbot_common_interfaces/srv/GetJointIntegerParam {}

# 位置 KD 设置
ros2 service call /set_pos_kd xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ["waist_roll_motor_joint"]
param_value: [42]"
# 位置 KD 获取
ros2 service call /get_pos_kd xbot_common_interfaces/srv/GetJointIntegerParam {}
```

- 单关节设置完后，调用保存关节参数

### 保存关节参数

```Bash
ros2 service call /save_param std_srvs/srv/Trigger {}\ 
```

### 关节标零**【仅内部使用】**

<callout emoji="⚠️">
B4机器标零过程中（**PD模式**），需要两人手扶机器左右大臂，先把下肢摆到极限位置并锁定抱闸以后，再对上肢安装标零工装
</callout>

1. 【仅B4使用】将踝、膝、髋、脖子调整到极限位置，如图所示（标定时，以PD模式启动，且需要手扶机器人左右臂）

```Markdown
# 分次解锁踝、膝、髋抱闸，并移动至极限位置
# 移动完之后，依次关闭抱闸
# 开 踝
./open_brake_ankle.sh

# 关 踝
./close_brake_ankle.sh

# 开 膝
./open_brake_knee.sh

# 关 膝
./close_brake_knee.sh

# 开 髋
./open_brake_hip.sh

# 关 髋
./close_brake_hip.sh
```

<grid>
<column width-ratio="0.688692">
[图片已省略]
</column>
<column width-ratio="0.311308">
[图片已省略]
</column>
</grid>

1. 启动SDK，并进入 ready 模式：

   ```Bash
   # 在基础启动下，且 SDK 启动
   ./sdk.sh
   
   # 进入 Ready 状态
   ./ready.sh
   ```
2. 调用标零服务

   #### 方式一：整机标零

   ```Bash
   ros2 service call /set_zero_pos std_srvs/srv/Trigger {}
   ```

   #### 方式二：单关节标零（关节列表点我跳转）

   ```Bash
   ros2 service call /set_joint_zero_pos xbot_common_interfaces/srv/SetJointZeroPosition "joint_name: 'left_shoulder_pitch_joint'"
   ```
3. 踝、膝、髋、脖子极限位置标定，并保存

   ```Bash
   ros2 service call /set_custom_home_position xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['ankle_joint', 'knee_joint', 'hip_joint', 'neck_yaw_joint', 'neck_pitch_joint']
   param_value: [0, 0.526, -0.526, 1.57, 0.70]"
   ```
4. 保存参数

   ```Bash
   # 多运行几次（建议3次），保证位置保存完成
   ros2 service call /save_param std_srvs/srv/Trigger {}
   ```
5. 关节上下电
6. 标定结果验证

   ```Bash
   ros2 topic echo /joint_states
   ```

   - 查看 position 数值，若 position 数值绝对值低于 0.02 ，即表示标定成功；否则，查看关节位置是否到位，确定到位，则多次执行 “调用标零服务” 步骤
   - 标零完成后，处于极限位置的关节可适当在无力情况下往回掰一下，防止关节卡住

---

### 关节掩码

- 设置

<callout emoji="✨">
掩码设置的时候需要转为十进制，常见掩码写入：80 对应 128，30 对应 48
</callout>

```bash
# 在基础启动下，且 SDK 启动并进入 Ready 模式后

# 查看关节掩码
ros2 service call /get_error_mask xbot_common_interfaces/srv/GetJointIntegerParam {}

# 设置关节掩码，如下为示例命令，对三个关节设置掩码，关节列表点我跳转
ros2 service call /set_error_mask xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ['ankle_joint','knee_joint','hip_joint']
param_value: [0,0,0]" 

# ！！设置完后，需要保存参数！！多保存几次
ros2 service call /save_param std_srvs/srv/Trigger {}

# 重启
```

- 获取

```Bash
ros2 service call /get_error_mask xbot_common_interfaces/srv/GetJointIntegerParam {}
```

---

### 关节扭矩系数

启动机器到 **ready** 状态

- 扭矩系数获取

  ```Bash
  ros2 service call /get_torque_factor xbot_common_interfaces/srv/GetJointFloat32Param {}
  ```
- 扭矩系数设置

  ```Bash
  ros2 service call /set_torque_factor xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['left_shoulder_pitch_joint']
  param_value: [0.075]"
  ```

### 关节摩擦补偿

```bash
# SDK 启动并进入 Ready 模式后

# 查看摩擦补偿打开状态
ros2 service call /get_friction_enable xbot_common_interfaces/srv/GetJointIntegerParam {}

# 打开摩擦补偿状态
ros2 service call /set_friction_enable xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ['left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_arm_yaw_joint', 'left_elbow_pitch_joint', 'left_elbow_yaw_joint', 'left_wrist_pitch_joint', 'left_wrist_roll_joint']
param_value: [1,1,1,1,1,1,1]"

# 查看库伦摩擦
ros2 service call /get_columb_friction xbot_common_interfaces/srv/GetJointFloat32Param {}

# 查看黏性摩擦
ros2 service call /get_viscous_friction xbot_common_interfaces/srv/GetJointFloat32Param {}

# 设置库伦摩擦
ros2 service call /set_columb_friction xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['ankle_joint']
param_value: [10]"

#设置粘性摩擦
ros2 service call /set_viscous_friction xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['ankle_joint']
param_value: [10]"

# ！！设置完后，需要保存参数！！
ros2 service call /save_param std_srvs/srv/Trigger {}
```

### 关节前馈**【仅内部使用】(测试阶段）**

1. 速度反馈滤波频率

   1. 设置：系数参考范围：(50, 500)

   ```Bash
   ros2 service call /set_speed_feedback_hz xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ['neck_pitch_joint']
   param_value: [100]"
   ```

   - 获取

   ```Bash
   ros2 service call /get_speed_feedback_hz xbot_common_interfaces/srv/GetJointIntegerParam {}
   ```
2. 前馈使能开启状态

   1. 设置：系数：0 - 关闭，1 - 开启

   ```Bash
   ros2 service call /set_speed_feedforward_enable xbot_common_interfaces/srv/SetJointIntegerParam "joint_name: ['ankle_joint']
   param_value: [1]"
   ```

   - 获取

   ```Bash
   ros2 service call /get_speed_feedforward_enable xbot_common_interfaces/srv/GetJointIntegerParam {}
   ```
3. 速度前馈系数

   1. 设置：系数参考范围：(0 1)

   ```Bash
   ros2 service call /set_speed_feedforward_coef xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['neck_pitch_joint']
   param_value: [0.8]"
   ```

   - 获取

   ```Bash
   ros2 service call /get_speed_feedforward_coef xbot_common_interfaces/srv/GetJointFloat32Param {}
   ```
4. 速度前馈滤波频率

   1. 设置：系数参考范围：(5, 50)

   ```Bash
   ros2 service call /set_speed_feedforward_coef_hz xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['neck_pitch_joint']
   param_value: [5.0]"
   ```

   - 获取

   ```Bash
   ros2 service call /get_speed_feedforward_coef_hz xbot_common_interfaces/srv/GetJointFloat32Param {}
   ```
5. 加速度前馈系数

   1. 设置：系数参考范围：(0, 1)

   ```Bash
   ros2 service call /set_acc_feedforward_coef xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['neck_pitch_joint']
   param_value: [0.5]"
   ```

   - 获取

   ```Bash
   ros2 service call /get_acc_feedforward_coef xbot_common_interfaces/srv/GetJointFloat32Param {}
   ```
6. 加速度前馈滤波频率

   1. 设置：系数参考范围：(50, 500)

   ```Bash
   ros2 service call /set_acc_feedforward_coef_hz xbot_common_interfaces/srv/SetJointFloat32Param "joint_name: ['neck_pitch_joint']
   param_value: [100]"
   ```

   - 获取

   ```Bash
   ros2 service call /get_acc_feedforward_coef_hz xbot_common_interfaces/srv/GetJointFloat32Param {}
   ```



## 传感器、外设

#### 电池信息

##### 查看所有电池信息

```Bash
ros2 service call /get_battery_param std_srvs/srv/Trigger {}

# 然后查看log日志
cat /system_log/log/xbot_control/battery_out.log
```

##### 查看基本电池信息

```Bash
ros2 topic echo /battery_state 
```

##### 查看电源板固件编译日期

```Shell
ros2 service call /Battery/GetCompileDate xbot_common_interfaces/srv/GetVersion {}
```

##### 查看电源板固件名称

```Shell
ros2 service call /Battery/GetFirmwareName xbot_common_interfaces/srv/GetVersion {}
```

##### 用电状态查看

```Bash
# electric_type： 0：NUC电， 1：关节电， 2：急停电，
# NUC电 和 关节电 的返回值为 1 表示上电，0 表示下电
# 急停电 的返回值为 1 表示急停触发，0未触发
ros2 service call /Battery/ElectricState xbot_common_interfaces/srv/ElectricState "electric_type: 0"
```

##### 用电状态设置

```Bash
# electric_type：  0：NUC电， 1：关节电
# state： 0：下电， 1： 上电
ros2 service call /Battery/SetElectricState xbot_common_interfaces/srv/SetElectricState "electric_type: 0
state: 0"
```

#### 灯带信息

```Plain Text
ros2 topic echo /led_control
```

#### 关节温度信息

```Plain Text
ros2 topic echo /temperature
```

#### IMU原生数据（仅适配于 L3 / M7 ）

```Bash
ros2 topic echo /imu_broadcaster/imu 
```

#### 航模遥控器数据（仅适配于 L3 / M7 ）

```Bash
# 如果遇到航模遥控器不可识别，需要删除 BRLTTY（盲人点字终端服务）
sudo apt remove --purge brltty

ros2 topic echo /loco/remoteControl/radio
```

#### 游戏手柄（冰原狼）数据

```Bash
ros2 topic echo /joy
```

<callout emoji="❗">
运动前需要保证周围无人靠近，且急停控制器在身边，有飞车预兆及时断电！
</callout>

#### 遥控器使用说明

<cite doc-id="Pzt1dovSuoCO3Zx55gJct5Lhnrb" file-type="docx" title="B4遥控器使用说明" type="doc"></cite>

<cite doc-id="IunWwwAHdi6DiwkbBbvcCxMfnuc" file-type="wiki" title="L3遥控器使用说明" type="doc"></cite>

---

## 固定动作运动

#### 获取关节状态

```Plain Text
ros2 topic echo /joint_states 
```

#### 单关节运动

##### **脚本发布【仅内部使用】**

- 在本地笔记本连接单个关节模组，或者多个关节模组，启动SDK，并ready
- 读取关节位置：在控制单关节旋转前运行 `./get_joint_position.sh 关节名称`，先读取关节模组对应的位
- 发布控制关节位置：在读取到的基础上运行 `./set_joint_position.sh 关节名称 关节位置 `
- 如下示例发布（以踝关节为例，注意：所发布的关节位置，不可多于当前位置 ±36° 或者 ±0.628 弧度）

[图片已省略]

##### 命令行发布

```Bash
# 关节命令
ros2 topic pub /wr1_controller/commands xbot_common_interfaces/msg/HybridJointCommand "header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: ''
joint_name: ['right_elbow_pitch_joint']
position: [1.6]
velocity: [0.0]
feedforward: [1.0]
kp: [500.0]
kd: [5.0]"

# 车轮命令
ros2 topic pub /wr1_base_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{
  header: {stamp: {sec: 0, nanosec: 0}, frame_id: ''},
  twist: {linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.1}}
}"
```

#### 全身固定轨迹运动（**关节动作** 只能在 **ready** 状态下使用）**【仅内部使用】**

| **关节动作名** | **功能描述** | **适配机型** | **灵巧手动作名** | **功能描述** | **适配机型** |
|-|-|-|-|-|-|
| zero | 归零 | L3.4/B4/M7 | hand_open | 手张开 | L3.4/B4/M7 |
| lift_up | 抬小臂 | L3.4/B4/M7 | hand_close | 手闭合 | L3.4/B4/M7 |
| mpc_init | MPC 初始化 | L3.4/B4/M7 |  |  |  |
| boxing | 装箱 | B4 |  |  |  |
| reset | 复位 | B4 |  |  |  |
| initpose_elbow90 | 初始化-手臂抬起 | L3.4/B4/M7 |  |  |  |
| initpose_handsdown | 初始化-手臂放下 | L3.4/B4/M7 |  |  |  |

##### 脚本运行

- 使用对应动作名称+.sh，如 `zero` 对应的是 `zero.sh`

##### Action服务运行

```Bash
ros2 action send_goal /simple_actions xbot_common_interfaces/action/SimpleActions "{action_name: 'zero', time_cost: 2.0}"
```

#### 手掰关节（主要是带抱闸电机）

- 解开抱闸，手动掰抱闸关节

```bash
# 在基础启动下，修改 /root/xbot/config.json: "mode" 修改为 “pd”
./sdk.sh

# 启动 Ready 模式
./ready.sh

# ！！解开抱闸前，必须有人手扶机器，否则机器会倒地！！
# 解除相应抱闸，具体看需要解开哪一个关节
# ！！解开全部抱闸！！
./open_brake_all.sh
# ！！解开 髋关节 抱闸！！
./open_brake_hip.sh
# ！！解开 膝关节 抱闸！！
./open_brake_knee.sh
# ！！解开 踝关节 抱闸！！
./open_brake_ankle.sh

# ！！关闭全部抱闸！！
./close_brake_all.sh
# ！！关闭 髋关节 抱闸！！
./close_brake_hip.sh
# ！！关闭 膝关节 抱闸！！
./close_brake_knee.sh
# ！！关闭 踝关节 抱闸！！
./close_brake_ankle.sh
```

# ===以下运动控制在非遥操作时，MPC相关的操作需要关闭===

## 运控功能总列表

<table><colgroup><col/><col/><col/></colgroup><thead><tr><th vertical-align="middle"><b>机器状态</b></th><th vertical-align="middle"><b>可用运控</b></th><th vertical-align="middle"><b>备注</b></th></tr></thead><tbody><tr><td vertical-align="middle"><b>ready</b></td><td>zero，lift_up，boxing，mpc_init，reset，hand_open， 底盘移动</td><td><ul><li>若在 activate 状态，需先运行deactivate.sh 退回至 ready 状态</li></ul></td></tr><tr><td vertical-align="middle"><b>activate</b></td><td>遥操作，老化动作（全身，单上臂，单腿，单脖子和腰），跳舞，底盘移动</td><td></td></tr></tbody></table>

---

## 关节老化测试（关节运动）

```bash
# 在基础启动下，且 SDK 启动并进入 Activate 模式后，启动老化测试

# 全身运动
./loop_all.sh

# 双臂运动
./loop_arm.sh

# 腰头运动
./loop_waist.sh

# 下肢运动
./loop_brake.sh
```

## 遥操作流程

#### 运行

- ！！以下操作要依次按顺序执行！！

```Shell
# 启动六个终端，在终端都连接到机器后使用脚本进入到容器内 
./go_to_docker.sh
第一个终端运行
# 在基础启动下，启动 SDK
./sdk.sh

# 在基础启动下，之后代码可以在同一终端下依次执行
# 在第二个终端进入 Ready 模式
./ready.sh

# 初始化位姿
./initpose_elbow90.sh

# 进入 Activate 模式
./activate.sh

# 第三个终端打开Webxr 
cd /root/xbot/algorithm/teleopx/webxr
conda activate teleop
python main.py --publisher zmq --camera-type stereo --fps 30 --width 640 --height 480

# 此时quest佩戴人员开始操作：
# 和机器人连接同一个wifi （连接显示网络连接受限是正常的），webxr 启动后，打开浏览器，访问下面网址：https://192.168.8.100:8010
# 访问成功后，当左下角显示data channel open 后，点击START AR,此时可以摘下挂在脖子上(也可以不摘)；人与机器人动作相似后长按meta键3s
# 此操作运行后佩戴人员不可移动和转身，下面过程中不可再执行此操作

# 第四个终端启动MPC
cd /root/xbot/algorithm/mpc/install/scripts
bash b4_mpc.bash

# 第五个终端启动灵巧手控制
cd /root/xbot/algorithm/teleopx/retargetx
conda activate teleop
python tele_node.py #此时手指可以运动

# 第六个终端启动整机控制
cd /root/xbot/algorithm/teleopx/retargetx
conda activate teleop
ros2 service call /Start_EE_Retarget std_srvs/srv/Trigger #在终端中输入该指令即可发送手臂数据
```

#### 录制

```Shell
ros2 bag record /wr1_base_drive_controller/cmd_vel /hand_controller/commands /servo_poses -o quest_mpc
```

#### 播放

```Shell
# 只启动 MPC， tele_node.py 关闭
ros2 bag play quest_mpc
```

## 跳舞播放 - 离线数据回播（注意和mpc不能同时使用 会冲突）

```bash
# 在基础启动下，且 SDK 启动并进入 Activate 模式后，启动跳舞
# 以下启动方式二选一

# 方式一：脚本启动
./start_dance.sh

# 方式二：launch 启动
cd /root/xbot/algorithm/offline_dance
source install/setup.bash
ros2 launch offline_xsense_data_process read_data_ctrl_rob_node.launch.py
```

修改舞蹈类型

```Plain Text
cd /root/xbot/algorithm/offline_dance/install/offline_xsense_data_process/share/offline_xsense_data_process/config/motion_database.json
vim motion_database.json
```

- 在motion_database.json中添加想要播放的舞蹈动作，如下

[图片已省略]

- 也可以添加多个舞蹈动作如下

[图片已省略]



- 也可以调节如下相关系数：

  - 每个动作的播放速率，`speed_scale`，范围为 `0.2~1.0`，推荐`0.5`
  - 每个动作的滤波系数，`filter_factor`，范围为 `0.0~1.0`，推荐`0.1`
  - 舞蹈动作列表，用户可以根据需要有选择的添加到`/root/xbot/algorithm/offline_dance/install/offline_xsense_data_process/share/offline_xsense_data_process/config/motion_database_full.json` 文件中进行播放。

## 导航流程

### 导航主控节点启动



### 本地启动导航GUI程序

### 建图、建点、建路径、建任务点



### 地图拷贝到客户端本机



### 上传地图到xos地图管理页面



---

# **FAQ**

<callout emoji="✨">
有问题直接在下面链接中填入
</callout>

<cite doc-id="RifCdPAJxoAuRFxPFSdcH6SznYg" file-type="docx" title="B4 FAQ" type="doc"></cite>

# ===以下为开发者操作，非演示操作==

## <cite doc-id="JzvRwLRDFiB2WRkGe7Xc5iWVnnf" file-type="wiki" title="本地 SDK 部署及注意事项" type="doc"></cite>

## <cite doc-id="UgJUdwvjBoIhUgxMiD4cxttknUf" file-type="docx" title="B4 开发者手册" type="doc"></cite>

## <cite doc-id="G4B0dhB0woQvRpxrmmJcyy6Jnzh" file-type="docx" title="ROBOTERA NUC 加密" type="doc"></cite>
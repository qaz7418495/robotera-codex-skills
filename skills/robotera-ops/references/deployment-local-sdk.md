<title>本地 SDK 部署及注意事项</title>

<callout emoji="✴️">
当前文档是在原生Ubuntu系统中使用，建议使用 Ubuntu 系统
</callout>

# 部署流程

1. 安装 `docker`：运行以下命令进行安装，运行后，等待输出结束，输入 `8`（已经安装的话可以跳过）

```Bash
source <(wget -qO- http://fishros.com/install)
```

1. 设置 `docker`：配置环境，依次运行以下命令

```Shell
#添加docker用户组（一般此步可省略，docker会自动创建，） 
sudo groupadd docker 

#将用户加入到docker用户组，$USER为用户名。 
sudo usermod -aG docker $USER
sudo gpasswd -a $USER docker 

#更新用户组
newgrp docker

# 设置地址
sudo nano /etc/docker/daemon.json
# 输入以下字段
{
  "insecure-registries": ["10.128.114.9:5000", "reg.robotera.com:5000"]
}

# 重启 docker 
sudo systemctl restart docker

# 拉取镜像
# 拉取稳定版本镜像
docker pull 10.128.114.9:5000/ros-humble-nuc:latest
# 变换镜像名称
docker tag 10.128.114.9:5000/ros-humble-nuc:latest ros-humble-nuc:latest
```

1. 获取 `SDK` ：从 `jenkins` 上获取最新的压缩包：http://je.robotera.com:8080/job/robot_sdk/
2. 创建目录，并解压缩文件至指定目录：

```Shell
sudo mkdir -p /opt/xbot /system_log/log/xbot_control

tar -xzf xbot_robot_sdk_dev_*.tar -C /opt/xbot
```

<callout emoji="‼️">
在 `SDK ≥ 2.0.110` 后，需要先部署 RL 算法，才能使用双足机器人的仿真环境
</callout>

1. 创建 `docker` 容器：执行以下命令

- 本机无显卡

```Bash
docker run \
-d \
--name ros2_dev \
--privileged \
-v /opt/xbot:/root/xbot \
-v /opt/xbot/hardware/supervisor_config:/etc/supervisor/conf.d \
-v /system_log/:/system_log \
-v /dev:/dev \
-e AUDIO_GID=$(getent group audio | cut -d: -f3) \
-e PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native \
-v /run/user/$(id -u)/pulse:/run/user/$(id -u)/pulse \
-v $HOME/.config/pulse/cookie:/root/.config/pulse/cookie \
--restart=always \
-e DISPLAY=$DISPLAY \
--network=host \
--cap-add=sys_nice \
ros-humble-nuc:latest
```

- 本机有显卡并已安装显卡驱动

```Bash
docker run \
-d \
--name ros2_dev \
--privileged \
-v /opt/xbot:/root/xbot \
-v /opt/xbot/hardware/supervisor_config:/etc/supervisor/conf.d \
-v /system_log/:/system_log \
-v /dev:/dev \
-e AUDIO_GID=$(getent group audio | cut -d: -f3) \
-e PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native \
-v /run/user/$(id -u)/pulse:/run/user/$(id -u)/pulse \
-v $HOME/.config/pulse/cookie:/root/.config/pulse/cookie \
--restart=always \
-e DISPLAY=$DISPLAY \
--network=host \
--cap-add=sys_nice \
-d --security-opt seccomp=unconfined --gpus 'all,"capabilities=compute,utility,graphics"' \
ros-humble-nuc:latest
```

1. 创建进入 docker 容器的脚本

```Shell
echo -e '#!/bin/bash\ndocker exec -it ros2_dev /bin/bash' > go_to_docker.sh && chmod +x go_to_docker.sh
```

1. 进入容器修改 `ROS_DOMAIN_ID`为`1~255`的值，禁止使用`211`

```Bash
./go_to_docker.sh

export ROS_DOMAIN_ID=写非211值

grep -q "^export ROS_DOMAIN_ID=" ~/.bashrc \
&& sed -i "s/^export ROS_DOMAIN_ID=.*/export ROS_DOMAIN_ID=${NEW_DOMAIN_ID}/" ~/.bashrc \
|| echo "export ROS_DOMAIN_ID=${NEW_DOMAIN_ID}" >> ~/.bashrc

sed -i "s/ROS_DOMAIN_ID=\"[^\"]*\"/ROS_DOMAIN_ID=\"${NEW_DOMAIN_ID}\"/" \
/root/xbot/hardware/supervisor_config/supervisord.conf

source ~/.bashrc
```

1. 配置docker环境

```Bash
# 进入docker
./go_to_docker.sh

# 进入脚本目录
cd /root/xbot/hardware/install/scripts

# 运行环境部署脚本
./setup_env.sh

# 需改配置文件
vim /root/xbot/config.json
# 将 mode 值改为 sim ，修改 robot_type 为对应想仿真的机型：如 wr1, l3.4.3, m7
```

<callout emoji="✴️">
执行`plotjugger`或者运行`仿真环境`前，需要先在宿主机中运行`xhost +`
仿真环境中，必须设置`mode`为`sim`，`hardware_type`为`hand`
</callout>

# config.json 说明

<table><colgroup><col/><col/></colgroup><thead><tr><th vertical-align="middle"><b>参数名称</b></th><th vertical-align="middle"><b>参数说明</b></th></tr></thead><tbody><tr><td>auto_start</td><td>自启动设置<br/><code>true</code>表示开机自启动<br/><code>false</code>表示关闭开机自启动</td></tr><tr><td>enable_developer</td><td>设置为<code>true</code>后，会取消自动配置机型和手类型，建议仿真环境设置为<code>true</code><br/><code>true</code>表示自动配置整机机型及手类型<br/><code>false</code>表示不自动配置</td></tr><tr><td>l3_mode</td><td>主要针对于 <code>l3.4</code> 真机机型使用，此值会在真机情况下覆盖 <code>mode</code> 参数值，参考值如下<br/><code>pd</code> 力控模式<br/><code>position</code> 位置模式<br/><code>velocity</code> 速度模式</td></tr><tr><td>mode</td><td>SDK 启动类型<br/><code>sim</code> 仿真模式<br/><code>pd</code> 力控模式<br/><code>position</code> 位置模式<br/><code>velocity</code> 速度模式</td></tr><tr><td>robot_type</td><td>整机机型，仿真时，修改该值就可以切换成不同机型<br/><code>l3.4</code> L7 <br/><code>wr1</code> B4/Q5<br/><code>m7</code> M7 数采半身机器<br/><code>m7.1</code>凯龙-固定立柱<br/><code>w7</code> 凯龙-升降立柱<br/><code>l3.4.3</code> 马拉松机型</td></tr><tr><td>hardware_type</td><td>是否有灵巧手，仿真必须为有手<br/><code>hand</code> 有手<br/><code>no_hand</code>无手</td></tr><tr><td>hand_type</td><td>灵巧手类型<br/><code>xhand</code>：可用机型 l3.4，wr1，m7，m7.1，w7<br/><code>lite</code> ：可用机型 wr1，l3.4.3<br/><code>green</code> ：可用机型 l3.4，m7</td></tr><tr><td colspan="2" vertical-align="middle"><b>以下参数一般不改，保持默认</b></td></tr><tr><td>launch_mode</td><td>xos启动模式</td></tr><tr><td>use_mpc_controller</td><td>mpc自启动</td></tr><tr><td>use_rl_controller</td><td>ri自启动</td></tr><tr><td>lift_joint_mode</td><td>立柱模式<br/><code>position</code> 位置模式<br/><code>velocity</code> 速度模式</td></tr></tbody></table>

仿真环境的`config.json`示例（l3.4 为例）

```JSON
{
    "auto_start": false,
    "enable_developer": true,
    "hand_type": "xhand",
    "hardware_type": "hand",
    "l3_mode": "pd",
    "launch_mode": "sim",
    "lift_joint_mode": "position",
    "mode": "sim",
    "robot_type": "l3.4",
    "use_mpc_controller": false,
    "use_rl_controller": false
}
```
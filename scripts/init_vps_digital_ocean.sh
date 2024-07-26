#!/bin/bash

umount /mnt/volume_sgp1_01

# 更新包索引
apt-get update
# 安装必要的包
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 的官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# 添加 Docker APT 源
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
# 安装 Docker CE
apt-get install -y docker-ce

# 启动 Docker 并设置开机自启
# systemctl start docker
# systemctl enable docker

# 验证 Docker 是否安装成功
# docker run hello-world


# 创建 Swap 文件
fallocate -l 2G /swapfile
# 设置 Swap 文件权限
chmod 600 /swapfile
# 将文件设置为 Swap 空间
mkswap /swapfile
# 启用 Swap 空间
swapon /swapfile
# 确保 Swap 空间在重启后仍然有效
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab

# 设置docker目录挂载点
mkdir -p /var/lib/docker
mount /dev/sda /var/lib/docker

echo '/dev/sda /var/lib/docker xfs defaults 0 0' | tee -a /etc/fstab
df

# dockerd --storage-driver overlay2

#启动dockerd
systemctl start docker
systemctl enable docker
# sudo systemctl stop docker

# 安装cog
curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
chmod +x /usr/local/bin/cog
![[Pasted image 20260212175735.png]]
切换用户 : su 用户名 
切换root :  sudo su root
查看用户： whoami
回到主目录 ：cd ~

### 文件类型与权限

```bash
# 文件类型识别
ls -la                     # 详细列出文件信息
file filename              # 查看文件类型
stat filename              # 查看文件详细状态

# 权限管理
chmod 755 filename         # 修改文件权限
chmod u+x filename         # 给所有者添加执行权限
chown user:group filename  # 修改文件所有者
chgrp group filename       # 修改文件所属组

# 权限含义
# r(4) - 读权限
# w(2) - 写权限  
# x(1) - 执行权限
# 755 = rwxr-xr-x (所有者读写执行，组和其他用户读执行)
```
### 打开应用
打开claude code ：claude 

### 基础命令操作

##### 文件与目录操作

```bash
# 导航命令
pwd                        # 显示当前目录
cd /path/to/directory      # 切换目录
cd ~                       # 切换到用户主目录
cd -                       # 切换到上一个目录

# 文件操作
ls -la                     # 列出文件详细信息
cp source destination      # 复制文件
mv source destination      # 移动/重命名文件
rm filename               # 删除文件
rm -rf directory          # 强制删除目录
mkdir -p /path/to/dir     # 创建目录（包括父目录）
rmdir directory           # 删除空目录

# 文件查看
cat filename              # 显示文件内容
less filename             # 分页查看文件
head -n 10 filename       # 查看文件前10行
tail -f filename          # 实时查看文件末尾
grep "pattern" filename   # 搜索文件内容
```

##### 文本处理工具

```bash
# 基础文本处理
grep -r "pattern" /path   # 递归搜索
grep -i "pattern" file    # 忽略大小写搜索
grep -v "pattern" file    # 反向搜索（不包含pattern的行）

# 文本统计
wc -l filename            # 统计行数
wc -w filename            # 统计单词数
wc -c filename            # 统计字符数

# 文本排序和去重
sort filename             # 排序文件内容
sort -n filename          # 按数字排序
uniq filename             # 去除重复行
sort filename | uniq      # 排序后去重
```

###  进程与系统监控

##### 进程管理

```bash
# 查看进程
ps aux                    # 查看所有进程
ps -ef                    # 另一种格式查看进程
top                       # 实时查看进程
htop                      # 增强版top（需要安装）
pgrep process_name        # 根据名称查找进程ID

# 进程控制
kill PID                  # 终止进程
kill -9 PID              # 强制终止进程
killall process_name      # 根据名称终止进程
nohup command &           # 后台运行命令
jobs                      # 查看后台任务
fg %1                     # 将后台任务调到前台
```

##### 系统资源监控

```bash
# 系统资源查看
free -h                   # 查看内存使用情况
df -h                     # 查看磁盘使用情况
du -sh /path              # 查看目录大小
lscpu                     # 查看CPU信息
lsblk                     # 查看块设备信息
lsusb                     # 查看USB设备
lspci                     # 查看PCI设备
```

## 第二阶段：系统管理基础

### 2.1 用户与权限管理

##### 用户管理

```bash
# 用户操作
sudo useradd -m username          # 创建用户并创建主目录
sudo passwd username              # 设置用户密码
sudo usermod -aG sudo username    # 将用户添加到sudo组
sudo userdel -r username          # 删除用户及其主目录
id username                       # 查看用户信息
whoami                           # 查看当前用户
who                              # 查看登录用户
w                                # 查看用户活动

# 组管理
sudo groupadd groupname          # 创建组
sudo groupdel groupname          # 删除组
groups username                  # 查看用户所属组
sudo usermod -G group1,group2 username  # 修改用户所属组
```

##### 高级权限管理

```bash
# 特殊权限
chmod +s filename               # 设置SUID权限
chmod +t directory             # 设置粘滞位
chmod 4755 filename            # SUID权限（4000）
chmod 2755 directory           # SGID权限（2000）
chmod 1755 directory           # 粘滞位权限（1000）

# ACL权限（访问控制列表）
setfacl -m u:username:rwx filename    # 设置用户ACL权限
setfacl -m g:groupname:rx filename    # 设置组ACL权限
getfacl filename                      # 查看ACL权限
setfacl -x u:username filename        # 删除用户ACL权限
```

###  软件包管理

##### Debian/Ubuntu系统（APT）

```bash
# 软件包管理
sudo apt update                 # 更新软件包列表
sudo apt upgrade                # 升级已安装软件包
sudo apt install package_name  # 安装软件包
sudo apt remove package_name   # 卸载软件包
sudo apt purge package_name    # 完全卸载软件包（包括配置文件）
sudo apt autoremove            # 清理不需要的依赖包

# 软件包查询
apt search keyword             # 搜索软件包
apt show package_name          # 显示软件包信息
apt list --installed           # 列出已安装软件包
dpkg -l                        # 查看已安装软件包
dpkg -L package_name           # 查看软件包安装的文件
```
## wsl安装
wsl --list --online 查看可安装版本（可能要挂梯子）
wsl --install Ubuntu-20.04 --web-download  下载ubuntu
wsl --list -v 检查当前的子系统
wsl --set-default xxx  设置默认系统
wsl --unregister xxx 卸载

指定位置安装
wsl --install Ubuntu-24.04 --location E:\WSL\Ubuntu

系统迁移
保存系统 wsl --export kali-linux E:\wsl-backup\kali.tar    导出kali-linux到E盘文件夹里
wsl --unregister kali-linux 注销原来的系统
导入系统 wsl --import kali-linux E:\WSL\Kali E:\wsl-backup\kali.tar --version 2导入新位置


配置文件位置 %USERPROFILE%\.wslconfig
## Kali

命令下载工具
### **curl (Client URL)**

最全能、最常用的工具，支持**数十种协议**。

```bash
# 基本用法
curl https://example.com/file.zip -O  # 下载并保存原名
curl https://example.com/file.zip -o newname.zip  # 指定保存名

# 常见用途
curl -I https://example.com  # 只看HTTP头信息
curl -X POST https://api.com -d '{"data":"value"}'  # 发送POST请求
curl -L https://short.url  # 跟随重定向
curl -s -o /dev/null https://example.com  # 静默下载（不显示进度）

# 特点：
# 1. 默认输出到标准输出（屏幕），需要参数保存到文件
# 2. 支持HTTPS、FTP、SFTP、SCP、SMTP等
# 3. 常用于API测试、网页抓取
```
安装工具要在usr目录下，配置文件在各个用户目录中配置

# 网络配置
## 🔧 代理配置详解

### 在 WSL2 中设置代理

如果您在 Windows 上运行代理软件（如 Clash、V2Ray 等），要在 WSL2 的 Linux 环境中使用代理：
### 统一使用 HTTP 代理（推荐）

如果您的代理软件（如 Clash）同时支持 HTTP 和 SOCKS5 代理：
1.在windows的代理软件设置中，找到局域网连接，打开局域网连接。
![[Pasted image 20260227021531.png]]

2.查看wsl虚拟网卡ip和端口号
![[Pasted image 20260227022601.png]]
![[Pasted image 20260227021704.png]]
![[Pasted image 20260227021648.png]]
修改为自己的ip，在终端中输入。即可在wsl中使用网络代理。
（临时参数，只在当前终端有效）
``` bash
# 设置 HTTP/HTTPS 代理
#export http_proxy="ip地址:当前代理端口"
export http_proxy="http://172.19.128.1:7897" 
export https_proxy="http://172.19.128.1:7897"
```

添加到~/.bashrc 或 ~/.zshrc文件中，永久生效。
#### 方案一：每次启动端口自动打开代理
```bash
# 添加到 ~/.bashrc 永久生效
echo 'export http_proxy="http://172.19.128.1:7890"' >> ~/.bashrc
echo 'export https_proxy="http://172.19.128.1:7890"' >> ~/.bashrc
source ~/.bashrc
```
#### 方案二：默认不开启代理，需要时通过命令开启。
（命令只对当前终端生效）
```bash
# 编辑 ~/.bashrc 或 ~/.zshrc（如果你用的是zsh）
# 代理快捷命令 (默认不启用，需要时运行 proxy-on 开启)
#开启代理
alias proxy-on='export http_proxy=http://172.19.128.1:7897 && export https_proxy=172.19.128.1:7897 && echo "代理已启用: >"'
# 关闭代理
alias proxy-off='unset http_proxy https_proxy  && echo "代理已关闭"'
# 查看代理
alias proxy-status='echo "HTTP代理: $http_proxy"'
```
保存后
```bash
# 使配置生效
source ~/.bashrc  #source ~/.zshrc
```
命令执行效果。
![[Pasted image 20260227024022.png]]
### 问题总结
1.注意方案二开启代理只对当前终端有效。打开新的终端是没开启代理的。

2.Linux终端里开启网络代理后，若windows中代理软件退出了，Linux内浏览器无法上网，方案二可以通过proxy-off命令关闭代理，浏览器就恢复正常。
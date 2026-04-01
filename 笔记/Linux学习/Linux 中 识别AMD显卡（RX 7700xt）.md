# 1.安装rcom
要在 WSL2 中调用您的 AMD Radeon RX 7700 XT 显卡，核心是安装 **AMD ROCm**​ 软件平台，它能让 WSL2 中的 Linux 系统识别并使用 Windows 主机透传的 GPU 硬件。以下是完整的步骤指南。

### 第一步：确保 Windows 主机满足前提条件

1. **系统要求**：Windows 11 22H2 或更高版本，并已启用 WSL2 。
    
2. **安装 AMD 显卡驱动**：从 AMD 官网下载并安装 **最新版 Adrenalin Edition 驱动程序**（专为 WSL2 设计）。这是 GPU 能在 WSL2 中被识别的基础。
    
3. **更新 WSL2**：在 Windows PowerShell（管理员）中运行：
    
    ```powershell
    wsl --update
    ```
    

### 第二步：在 Kali Linux 中安装 ROCm

由于 Kali 基于 Debian，安装步骤与 Ubuntu 类似，但需注意兼容性。

1. **更新系统并安装必要工具**：
    
    ```bash
    sudo apt update
    sudo apt upgrade -y
    sudo apt install wget -y
    ```
    
2. **下载并安装 ROCm 统一安装包**：
    
    - 目前对 WSL2 支持较好的版本是 **ROCm 6.4**​ 。
        
    - 执行以下命令（注意：Kali 的代号可能不同，如果 `noble`不适用，请尝试 `jammy`或查阅 Kali 对应代号）：
        
    
    ```bash
    # 下载安装包
    wget https://repo.radeon.com/amdgpu-install/6.4/ubuntu/noble/amdgpu-install_6.4.60400-1_all.deb
    # 安装该包
    sudo apt install ./amdgpu-install_6.4.60400-1_all.deb
    ```
    
3. **执行 ROCm 安装（关键步骤）**：
    
    ```bash
    sudo amdgpu-install -y --usecase=wsl,rocm --no-dkms
    ```
    
    - `--usecase=wsl,rocm`：指定为 WSL 环境安装 ROCm 组件。
        
    - `--no-dkms`：**必须添加**，因为 WSL2 使用 Windows 主机的 GPU 驱动，无需在 Linux 内安装内核模块 。
        
    
4. **重启 WSL2**：
    
    在 Windows PowerShell 中执行 `wsl --shutdown`，然后重新启动 Kali，使驱动加载生效。
    

### 第三步：验证 GPU 是否被成功调用

在 Kali 终端中运行以下命令：

1. **检查 ROCm 环境**：
    
    ```bash
    /opt/rocm/bin/rocminfo
    ```
    
    如果安装成功，此命令将输出详细的 GPU 信息，包括您的 **AMD Radeon RX 7700 XT**​ 的型号、计算单元数量、内存大小等 。
    
2. **查看 GPU 状态**：
    
    ```bash
    /opt/rocm/bin/rocm-smi #或者amd-smi 
    ```
    
    此命令类似于 NVIDIA 的 `nvidia-smi`，会显示 GPU 的利用率、温度、功耗和内存使用情况 。
    
3. **验证 OpenGL 渲染器（检查是否告别 llvmpipe）**：
    
    ```bash
    glxinfo -B | grep "OpenGL renderer"
    ```
    
    **成功标志**：输出应显示为 **AMD Radeon Graphics**​ 或类似字符串（例如 `AMD Radeon™ Graphics (gfx1103)`），而**不再是**​ `llvmpipe`。这表明图形渲染已由您的物理显卡接管。
### 故障排除与注意事项

- **Kali 兼容性**：ROCm 官方主要支持 Ubuntu。如果在 Kali 上安装失败，可尝试：
    
    - 查找 Kali 专用的 ROCm 安装指南或社区解决方案。
        
    - 考虑在 WSL2 中安装 **Ubuntu 22.04/24.04**​ 作为 ROCm 环境，然后通过 `kex`连接其桌面，或直接在 Ubuntu 中运行计算任务。
# 故障1 连接不到window的硬件
  rocm已经安装好，但显示无支持的设备。

![[Pasted image 20260226014813.png]]
### 解决方式 

您遇到的 `hsa_init Failed`错误是 WSL2 环境下使用 AMD GPU 运行 ROCm 的**常见问题**。根本原因是 ROCm 在 WSL2 中无法直接访问传统的 Linux GPU 设备节点（如 `/dev/kfd`），而必须通过 WSL 特有的 **`/dev/dxg`桥接设备**。解决此问题的核心是安装 **`librocdxg`补丁**。

### 🔧 解决方案（按步骤操作）

#### 第一步：确认 Windows 主机环境

1. **安装最新的 AMD 显卡驱动**（专为 WSL2 优化）：
    
    - 访问 AMD 官网驱动下载页面，选择您的显卡型号（如 Radeon RX 7700 XT）和 Windows 11 系统。
        
    - 下载并运行 **“AMD Software: Adrenalin Edition”**​ 安装程序，选择 **“完整安装”**​ 以确保包含 WSL2 支持组件。
        
    - 安装完成后**重启 Windows**。
        
    
2. **安装 Windows SDK**（如果尚未安装）：
    
    - 下载 Windows SDK并安装到默认路径（如 `C:\Program Files (x86)\Windows Kits\10`）。
        
    

#### 第二步：在 WSL2 的 Ubuntu 中编译安装 `librocdxg`

1. **安装编译依赖**：
    
    ```bash
    sudo apt update && sudo apt install -y git cmake build-essential
    ```
    
2. **克隆 `librocdxg`仓库并编译**：
    
    ```bash
    git clone https://github.com/ROCm/librocdxg.git
    cd librocdxg
    mkdir build && cd build
    # 设置 Windows SDK 路径（根据您的实际安装版本调整）
    export win_sdk='/mnt/c/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0/'
    cmake .. -DWIN_SDK="${win_sdk}/shared"
    make
    sudo make install
    ```
    
    _编译过程可能需要几分钟。_
    

#### 第三步：启用 DXG 检测并验证

1. **设置环境变量**（临时生效，仅当前终端）：
    
    ```bash
    export HSA_ENABLE_DXG_DETECTION=1
    rocminfo
    ```
    
    如果成功，您将看到详细的 GPU 信息输出，而不再是错误提示。
    
2. **永久生效配置**（推荐）：
    
    将环境变量添加到 `~/.bashrc`或 `~/.profile`中：
    
    ```bash
    echo 'export HSA_ENABLE_DXG_DETECTION=1' >> ~/.bashrc
    source ~/.bashrc
    ```
    
    之后每次打开终端，`rocminfo`都能正常识别 GPU。
    

### ⚠️ 注意事项

1. **`rocm-smi`工具在 WSL2 中不受支持**：这是 AMD 官方确认的架构限制。您可以通过 Windows 任务管理器或第三方工具（如 GPU-Z）监控 GPU 负载。
    
2. **用户组权限**：虽然 WSL2 环境下通常不需要，但为确保无误，可将当前用户加入 `video`和 `render`组：
    
    ```bash
    sudo usermod -aG video,render $USER
    ```
    
    _执行后需要完全退出并重新启动 WSL（`wsl --shutdown`再重新打开终端）才能生效。_
    
3. **驱动版本警告**：如果 `rocminfo`成功运行但显示 `Warning: Windows driver is old, please update it`，请返回第一步更新 Windows 主机驱动。
4. 故障  无法加载 `librocdxg.so`文件（没有找到该共享库文件）。
    ![[Pasted image 20260226021543.png]]
		解决方法
		这是一个典型的**库链接问题**，表明 `librocdxg`虽然已安装，但系统无法找到它，导致 ROCm 运行时库找不到所需函数。您已接近成功，只需解决库路径配置问题。

### 🔍 错误分析

1. **`Cannot load librocdxg.so`**：系统找不到 `librocdxg.so`共享库文件。
    
2. **`undefined symbol: hsaKmtOpenKFD`**：ROCm 的 `libhsa-runtime64.so`需要一个关键函数 `hsaKmtOpenKFD`，这个函数本应由 `librocdxg.so`提供，但找不到。
    
3. **`Segmentation fault`**：由于上述依赖关系失败，程序崩溃。
    

### ✅ 解决方案

请按顺序执行以下步骤，重点是**确保系统能找到并正确加载 `librocdxg.so`**。

#### 第一步：验证 `librocdxg.so`是否已安装

首先确认库文件是否真的存在：

```bash
sudo find / -name "librocdxg.so*" 2>/dev/null
```

预期输出应该类似：

```markdown
/usr/local/lib/librocdxg.so
/usr/local/lib/librocdxg.so.1.0
```

#### 第二步：添加库路径到系统（关键步骤）

如果库文件在 `/usr/local/lib/`中，则需要让系统知道这个位置：

1. **创建配置文件**，将库路径加入系统搜索路径：
    
    ```bash
    echo '/usr/local/lib' | sudo tee /etc/ld.so.conf.d/librocdxg.conf
    ```
    提示：我这里显示路径为/opt/rocm/lib，所以要将/usr/local/lib改为/opt/rocm/lib
    ![[Pasted image 20260226022231.png]]
1. **刷新动态链接器缓存**：
    
    ```bash
    sudo ldconfig
    ```
    
2. **验证库是否可被找到**：
    
    ```bash
    ldconfig -p | grep librocdxg
    ```
    
    如果成功，应该能看到 `librocdxg.so`的条目。
    

#### 第三步：设置环境变量并重新测试

现在重新设置环境变量并测试：

```bash
export HSA_ENABLE_DXG_DETECTION=1
export LD_DEBUG=libs  # 用于调试库加载过程，可选
rocminfo
```

#### 第四步：如果问题依旧，手动指定库路径

如果上述步骤无效，可以手动指定库路径：

```bash
export HSA_ENABLE_DXG_DETECTION=1
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
rocminfo
```

如果这次成功，将此行添加到 `~/.bashrc`中使其永久生效：

```bash
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
```

### ✅ 验证成功

运行以下命令，确认 GPU 已被正确识别：

```bash
rocminfo | grep -A5 "Name.*AMD"
```

输出应显示您的 AMD 显卡型号（如 “AMD Radeon RX 7700 XT”）。
![[Pasted image 20260226022545.png]]![[Pasted image 20260226024903.png]]

即使安装了 ROCm，GPU 仍显示为 “llvmpipe” 是完全正常的现象。这涉及到 **GPU 计算加速**​ 与 **图形渲染**​ 两个不同的概念。
![[Pasted image 20260226025941.png]]
## 🔍 原因分析

### 1. **计算加速 vs. 图形渲染是两套独立系统**

- **ROCm**​ 是 AMD 的**GPU 计算平台**，为 PyTorch、TensorFlow 等 AI/科学计算框架提供 GPU 加速。
    
- **llvmpipe**​ 是 **CPU 软件渲染器**，用于 Xfce 桌面环境、窗口管理器等**2D/3D 图形界面渲染**。
    

在 WSL2 中，这两个系统可以独立工作：

- 计算（ROCm）走 **`/dev/dxg`设备**（通过 `librocdxg`桥接）
    
- 图形渲染（桌面）走 **WSLg 图形子系统**
    

### 2. **WSL2 图形架构限制**

WSL2 默认的图形系统（WSLg）通过以下方式工作：

- Windows 主机上的 **Direct3D 12 驱动**​ → 映射到 WSL2 中的 **OpenGL/Vulkan**
    
- 这个映射层目前**优先使用 Microsoft 的 DirectX 12 兼容层**，而不是原生的 AMD OpenGL 驱动
    
- 所以系统信息中显示的是软件渲染器（llvmpipe）
- 计算验证
![[Pasted image 20260226041755.png]]
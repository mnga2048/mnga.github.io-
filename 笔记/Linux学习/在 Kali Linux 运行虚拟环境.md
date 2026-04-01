Kali Linux 为保护系统 Python 环境，默认禁止直接通过 pip 安装包。以下是解决方案
**以后每次使用时**，只需要先激活虚拟环境：

```bash
source ~/pytorch-rocm-env/bin/activate
# 然后运行您的 Python 程序
python your_script.py
# 完成后
deactivate
```

## 📁 虚拟环境管理技巧

### 1. 常用命令

```bash
# 创建虚拟环境
python3 -m venv 环境名称

# 激活
source 环境名称/bin/activate

# 停用
deactivate

# 删除虚拟环境
rm -rf 环境名称
```

### 2. 将虚拟环境添加到 Jupyter Notebook

```bash
# 在虚拟环境中
source ~/pytorch-rocm-env/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=pytorch-rocm-env
# 然后在 Jupyter 中就可以选择这个内核了
```

### 3. 创建快捷脚本

在 `~/.bashrc`中添加别名：

```bash
echo "alias pytorch-env='source ~/pytorch-rocm-env/bin/activate'" >> ~/.bashrc
source ~/.bashrc
```

之后只需输入 `pytorch-env`即可激活环境。
## 💡 重要提示

1. **虚拟环境是独立的**：每个虚拟环境有独立的 Python 包，不会影响系统或其他环境。
    
2. **每次新终端会话都需要激活**：打开新终端后，需要重新运行 `source ~/pytorch-rocm-env/bin/activate`。
    
3. **PyTorch 版本匹配**：确保 PyTorch 的 ROCm 版本与您系统安装的 ROCm 版本匹配。
## 验证 GPU 是否可用

激活虚拟环境后，运行以下测试：

```bash
source ~/pytorch-rocm-env/bin/activate

python -c "
import torch
print(f'PyTorch 版本: {torch.__version__}')
print(f'ROCm/CUDA 可用: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'GPU 设备: {torch.cuda.get_device_name(0)}')
    print(f'GPU 内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB')
    
    # 简单计算测试
    a = torch.randn(1000, 1000).cuda()
    b = torch.randn(1000, 1000).cuda()
    c = torch.matmul(a, b)
    print(f'GPU 计算测试通过! 结果形状: {c.shape}')
else:
    print('警告: GPU 不可用，请检查 ROCm 安装')
"
```
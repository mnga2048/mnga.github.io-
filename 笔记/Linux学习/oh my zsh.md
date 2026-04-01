[Home · ohmyzsh/ohmyzsh Wiki](https://github.com/ohmyzsh/ohmyzsh/wiki)

zsh是sh的进阶版，一般linux系统自带的是bash，切换成zsh后，可以用oh my zsh来美化zsh配置。

![[Pasted image 20260210233917.png]]
![[Pasted image 20260210234327.png]]
下载方式

| Method    | Command                                          |
| :-------- | :----------------------------------------------- |
| **curl**  | `sh -c "$(curl -fsSL https://install.ohmyz.sh)"` |
| **wget**  | `sh -c "$(wget -O- https://install.ohmyz.sh)"`   |
| **fetch** | `sh -c "$(fetch -o - https://install.ohmyz.sh)"` |
![[Pasted image 20260210232225.png]]

#### **核心配置：编辑 `~/.zshrc`**

所有魔法都发生在这个配置文件里。

```bash
# 使用你喜欢的编辑器打开配置文件
nano ~/.zshrc
# 或
code ~/.zshrc
```

**关键配置项**：

- **`ZSH_THEME`**：设置主题。例如 `ZSH_THEME="agnoster"`（经典）或 `ZSH_THEME="robbyrussell"`（默认）。你可以在官网主题库预览所有主题。
    
- **`plugins=(...)`**：启用插件。按需添加，用空格分隔。例如：
    
    ```bash
    plugins=(
      git          # Git命令别名和提示（必装）
      z            # 目录智能跳转（输入 `z 目录名` 快速进入）
      autojump     # 类似z的目录跳转
      zsh-autosuggestions   # 根据历史输入命令提示（需额外安装）
      zsh-syntax-highlighting # 命令语法高亮（需额外安装）
      docker       # Docker补全和别名
      kubectl      # Kubernetes补全
    )
    ```
    
    对于标注“需额外安装”的插件，通常需要在 `~/.zshrc`配置前先通过Git克隆到插件目录：
    
    ```bash
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    ```
    

配置完成后，保存文件并**重启终端**，或运行 `source ~/.zshrc`使配置立即生效。

---

### 💎 **必知必会技巧**

- **更新**：定期运行 `omz update`来更新Oh My Zsh本身、主题和插件。
    
- **重载配置**：修改 `.zshrc`后，无需重启终端，只需运行 `source ~/.zshrc`或 `omz reload`。
    
- **探索新主题/插件**：在 Oh My Zsh Wiki上浏览丰富的资源。
    
- **自定义配置**：你可以在 `~/.oh-my-zsh/custom/`目录下创建自己的主题或插件，它们不会被更新覆盖。
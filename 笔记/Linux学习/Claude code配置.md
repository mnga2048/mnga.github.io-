
全局安装Coding Tool Helper

该方式适合频繁使用 Coding Tool Helper 的用户，通过全局安装后可运行 `coding-helper` 或 `chelper` 命令启动工具。

若您执行 `npm install` 后报错提示权限不足 `permission denied`，请尝试在命令前加上 sudo（MacOS / Linux），或以管理员身份运行命令行（Windows）。  
如: `sudo npm install -g @z_ai/coding-helper`  
或推荐使用 npx 方式直接启动 `npx @z_ai/coding-helper`

```
## 进入命令行界面，先全局安装 @z_ai/coding-helper
npm install -g @z_ai/coding-helper
## 然后运行 coding-helper 或 chelper
coding-helper
```

### 命令列表

> 除了支持交互式向导外，Coding Tool Helper 还支持通过命令行 `coding-helper` 或 `chelper` 加参数直接执行各项功能：

```
# 运行初始化向导
coding-helper init

# 语言管理
coding-helper lang show              # 显示当前语言
coding-helper lang set zh_CN         # 设置为中文
coding-helper lang --help            # 查看语言命令帮助

# API 密钥管理
coding-helper auth                   # 交互式设置密钥
coding-helper auth glm_coding_plan_china <token>     # 直接选择 China 套餐并设置密钥
coding-helper auth revoke            # 删除已保存的密钥
coding-helper auth reload claude     # 将最新套餐信息加载至Claude Code工具
coding-helper auth --help            # 查看认证命令帮助

coding-helper doctor                 # 检查系统配置和工具状态
coding-helper --help                 # 显示帮助信息
coding-helper --version              # 显示版本
```

## 其他安装方式

**方式一：自动化助手**Coding Tool Helper 是一个编码工具助手，快速将您的**GLM编码套餐**加载到您喜爱的**编码工具**中。安装并运行它，按照界面提示操作即可自动完成工具安装，套餐配置，MCP服务器管理等。

```
# 进入命令行界面，执行如下运行 Coding Tool Helper
npx @z_ai/coding-helper
```

详细说明请参考 [Coding Tool Helper 文档](https://docs.bigmodel.cn/cn/coding-plan/extension/coding-tool-helper)。

*方式二：手动设置环境变量*

你也可以手动将密钥添加到你的Shell配置文件中（如 `~/.bashrc`或 `~/.zshrc`）。

```bash
echo 'export ANTHROPIC_API_KEY="你的API_KEY"' >> ~/.bashrc
source ~/.bashrc
[2](@ref)
```
 **验证安装**
    
    关闭终端重新打开，然后运行以下命令。如果成功显示版本号，则表明安装成功。
      claude -v

    
- **开始使用**
    
    进入你的项目目录，输入 `claude`命令就可以启动交互界面，开始你的AI编程之旅了！
    
    ```bash
    cd /path/to/your/project
    claude
    ```


模型设置 nano ~/.claude/settings.json里给env添加
"ANTHROPIC_MODEL": "glm-4.7"
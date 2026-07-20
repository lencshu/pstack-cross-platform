# pstack 跨平台适配

这个仓库以 Cursor 版 pstack 为唯一上游源，同时产出可直接安装的 Codex 和 Claude Code 插件。适配不是三份手工副本：根目录的 `skills/`、`agents/`、`automations/`、`.cursor-plugin/` 保持 Cursor 上游结构，其他平台包由脚本生成。

## 安装

### Cursor

```text
/add-plugin pstack
```

### Codex

从本地仓库安装：

```powershell
codex plugin marketplace add .
codex plugin add pstack@pstack-cross-platform
```

从 GitHub 安装：

```powershell
codex plugin marketplace add lencshu/pstack-cross-platform
codex plugin add pstack@pstack-cross-platform
```

新任务中先运行 `$pstack:setup-pstack`，再用 `$pstack:poteto-mode`。

### Claude Code

从本地仓库安装：

```powershell
claude plugin marketplace add .
claude plugin install pstack@pstack-cross-platform
```

从 GitHub 安装：

```powershell
claude plugin marketplace add lencshu/pstack-cross-platform
claude plugin install pstack@pstack-cross-platform
```

新会话中先运行 `/pstack:setup-pstack`，再用 `/pstack:poteto-mode`。

## 桌面端 App 集成

当前适配包不创建独立侧边栏、Webview 或设置页面。pstack 在桌面端表现为可安装插件，以及插件提供的技能和子代理。安装后从聊天输入框调用技能即可。下面的界面路径按 2026-07-20 的客户端文档整理。

### Cursor 桌面端

Cursor 直接使用仓库根目录的上游版本，不经过 `adapters/` 生成。日常使用建议安装 Cursor Marketplace 中的官方 pstack：

1. 打开 Cursor，在 Agent 输入框运行 `/add-plugin pstack`。也可以打开 [Cursor Marketplace](https://cursor.com/marketplace)，搜索 `pstack` 后安装。
2. 安装完成后新建一个 Agent 对话。
3. 首次运行 `/setup-pstack`，选择不同工作角色使用的模型。
4. 处理非简单任务时运行 `/poteto-mode <任务描述>`。其他技能也使用 `/<skill>` 形式调用。
5. 在 Cursor 的 Customize 或插件管理页面中停用、更新或卸载插件。

开发本仓库时，可以把仓库根目录作为本地插件挂到 Cursor：

```text
~/.cursor/plugins/local/pstack/
```

该目录中的 `.cursor-plugin/plugin.json` 必须直接位于插件根目录下。建议创建指向本仓库的目录链接，而不是复制一份源码。修改后执行 `Developer: Reload Window`，或完全退出再打开 Cursor。这样本地验证始终读取 Cursor 上游目录，生成的 Codex 和 Claude Code 包不会参与 Cursor 运行。

Cursor 官方说明见 [Plugins](https://cursor.com/docs/plugins)。

### Codex 桌面端

Codex 桌面端从 `.agents/plugins/marketplace.json` 读取本仓库的 Marketplace。首次使用需要先注册仓库，之后可以在 App 内安装和管理插件。

1. 在系统终端注册 Marketplace：

   ```powershell
   codex plugin marketplace add lencshu/pstack-cross-platform
   ```

   开发本地改动时，把 GitHub 地址换成仓库根目录：

   ```powershell
   codex plugin marketplace add .
   ```

2. 完全退出并重新打开 ChatGPT/Codex 桌面端。仅关闭窗口可能不会刷新 Marketplace。
3. 在桌面端选择 `Codex`，打开 `Plugins`。
4. 在 Marketplace 来源中选择 `pstack cross-platform`，打开 `pstack`，点击加号安装。若已经运行过 `codex plugin add pstack@pstack-cross-platform`，这一步只需确认它出现在 `Installed` 中并已启用。
5. 新建任务。运行 `$pstack:setup-pstack` 完成一次模型配置，再用 `$pstack:poteto-mode` 或其他 `$pstack:<skill>` 技能。

命令行完整安装与排错：

```powershell
codex plugin add pstack@pstack-cross-platform
codex plugin marketplace list
codex plugin list
```

更新 GitHub Marketplace 后运行 `codex plugin marketplace upgrade pstack-cross-platform`，重新安装插件，并新建任务。开发期若修改了生成包，按 Codex 的缓存刷新流程更新版本后重新安装，不能依赖旧任务热加载新的技能文件。

Codex 桌面端会把这个包显示为技能插件。当前包没有 `.app.json` 或 MCP 服务，因此不会出现自定义界面或外部账号授权流程。官方流程见 [Plugins](https://learn.chatgpt.com/docs/plugins) 和 [Build plugins](https://learn.chatgpt.com/docs/build-plugins#build-your-own-curated-plugin-list)。

### Claude Desktop 的 Code 标签页

Claude Desktop 与 Claude Code CLI 共用插件配置。先注册 Marketplace，再在 Code 标签页的插件管理器中安装：

1. 在系统终端注册 Marketplace：

   ```powershell
   claude plugin marketplace add lencshu/pstack-cross-platform
   ```

   本地开发时可改用：

   ```powershell
   claude plugin marketplace add .
   ```

2. 打开 Claude Desktop，进入 `Code` 标签页并创建 `Local` 会话。SSH 会话也支持插件。
3. 点击输入框旁的 `+`，依次选择 `Plugins`、`Add plugin`。
4. 在 `pstack-cross-platform` Marketplace 中选择 `pstack`。个人使用选择 User scope；需要把启用配置写入仓库时选择 Project scope；只在当前仓库个人使用时选择 Local scope。
5. 安装后运行 `/reload-plugins`，或新建一个 Code 会话。
6. 首次运行 `/pstack:setup-pstack`，之后使用 `/pstack:poteto-mode <任务描述>`。点击 `+`、`Slash commands` 也可以浏览所有 pstack 技能。
7. 通过 `+`、`Plugins`、`Manage plugins` 启用、停用或卸载插件。

也可以完全使用命令行安装：

```powershell
claude plugin install pstack@pstack-cross-platform
claude plugin marketplace list
```

团队仓库或 Claude Desktop 云会话不能依赖某台电脑上的本地安装。把下面的配置加入仓库的 `.claude/settings.json`，让受信任的仓库在会话启动时安装并启用插件：

```json
{
  "extraKnownMarketplaces": {
    "pstack-cross-platform": {
      "source": {
        "source": "github",
        "repo": "lencshu/pstack-cross-platform"
      }
    }
  },
  "enabledPlugins": {
    "pstack@pstack-cross-platform": true
  }
}
```

Claude Desktop 当前只在 Local 和 SSH 会话中提供插件浏览器。本机安装的插件不会自动进入 Cloud 会话，Cloud 会话需要上面的仓库配置；WSL 会话当前不支持插件。桌面端也不支持 Agent Teams，但 pstack 使用的是普通插件技能和子代理，不要求 Agent Teams。

官方说明见 [Claude Desktop](https://code.claude.com/docs/en/desktop)、[插件发现与安装](https://code.claude.com/docs/en/discover-plugins) 和 [Marketplace 配置](https://code.claude.com/docs/en/plugin-marketplaces)。

### 安装后的统一检查

三个桌面端都应满足以下结果：

1. 插件管理页能看到 `pstack`，状态为已安装并启用。
2. 新任务或新会话中能搜索到平台对应的 `setup-pstack` 与 `poteto-mode`。
3. 首次配置后生成 `~/.pstack/<platform>-models.md`。
4. 运行 mode 技能时，客户端能读取项目文件、调用终端，并按权限设置启动子代理。

如果第 1 项失败，先检查 Marketplace 是否已注册；第 2 项失败时重启 App 并新建任务；第 3 项失败时检查用户目录写权限；第 4 项失败时检查当前项目的终端、文件和子代理权限。

## 实现原理

pstack 没有常驻进程或传统运行时代码。它的执行主体是 `SKILL.md`：客户端先读取 frontmatter 中的名称和描述，需要时再加载正文，并由模型依照正文调用文件、终端、MCP 和子代理工具。因此“能识别清单”只解决安装问题；要真正兼容，还必须翻译正文中的平台语义。

适配层处理五类差异：

1. 插件清单。Cursor 使用 `.cursor-plugin/plugin.json`，Codex 使用 `.codex-plugin/plugin.json`，Claude Code 使用 `.claude-plugin/plugin.json`。
2. 市场清单。Codex 从 `.agents/plugins/marketplace.json` 发现 `plugins/pstack`；Claude Code 从 `.claude-plugin/marketplace.json` 发现 `platforms/claude/pstack`。
3. 技能调用名。Codex 生成 `$pstack:<skill>`，Claude Code 生成 `/pstack:<skill>`。
4. 子代理协议。Cursor 的 `Task`、`subagent_type`、`readonly` 和模型 slug 被翻译成 Codex 的子代理/推理强度语义，或 Claude Code 的 `Agent`、模型 alias 和显式只读提示。
5. 客户端能力。Cursor 专有的 `/loop`、`babysit`、`cursor-team-kit` 控制技能、规则目录和 transcript 路径会被替换成目标平台当前可用的等待、GitHub、浏览器、终端、配置与任务历史能力。

生成器会在每个目标 `SKILL.md` 中注入一小段平台契约。模型选择由 `$pstack:setup-pstack` 或 `/pstack:setup-pstack` 写入 `~/.pstack/<platform>-models.md`，不会污染 Codex 或 Claude Code 的全局规则。

## 目录边界

```text
skills/                              Cursor 上游技能，唯一业务源
agents/                              Cursor 上游 agent
automations/                         Cursor 专属 Benny 自动化
adapters/codex.json                  Codex 声明式替换和约束
adapters/claude.json                 Claude Code 声明式替换和约束
adapters/*/overrides/                无法安全通用替换的少量文件
scripts/build_adapters.py            构建两个目标包和市场清单
scripts/sync_cursor_upstream.py      检查或同步 Cursor 上游子目录
plugins/pstack/                      生成的 Codex 插件，不手改
platforms/claude/pstack/             生成的 Claude Code 插件，不手改
```

Claude Code 可以直接打包 `agents/poteto-agent.md`。当前 Codex 插件清单不分发自定义 agent 文件，因此 Codex 版把它降解为“启动 worker，并在任务消息中要求先读取 poteto-mode”的适配协议。核心工作流仍然保留。

Benny 依赖 Cursor Automations 和 Cursor Slack 动作，目前只在 Cursor 源中保留，不会伪装成已兼容组件。要迁移它，需要分别映射到 Codex Automations 与 Claude Code monitors/agent teams，这是独立功能项目。

## 同步 Cursor 上游

默认命令只比较，不写文件：

```powershell
python scripts/sync_cursor_upstream.py
```

确认差异后再同步：

```powershell
python scripts/sync_cursor_upstream.py --apply
```

`--apply` 只镜像 `.cursor-plugin/`、`agents/`、`automations/`、`skills/`、`LICENSE` 和 `README.md`，不会覆盖 `adapters/`、`scripts/`、测试或生成市场。完成后会自动重建两个目标包，并记录上游 commit。

上游新增一种稳定的平台耦合表达时，优先把规则加到 `adapters/<platform>.json`。只有单个文件的语义无法可靠转换时，才放进 `overrides/`。这能把后续同步冲突保持在适配层，而不是扩散到整套技能。

## 构建与验证

```powershell
python scripts/build_adapters.py
python scripts/build_adapters.py --check
python -m unittest discover -s tests -v
claude plugin validate platforms/claude/pstack --strict
claude plugin validate .claude-plugin/marketplace.json --strict
```

Codex 包使用 Codex `plugin-creator` 提供的校验器验证。CI 环境可以调用同一校验器，或使用当前 Codex 客户端提供的插件校验入口。

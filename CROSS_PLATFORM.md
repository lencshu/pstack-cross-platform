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

从 GitHub 安装时，把 `<owner>/<repo>` 换成这个仓库发布后的地址：

```powershell
codex plugin marketplace add <owner>/<repo>
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
claude plugin marketplace add <owner>/<repo>
claude plugin install pstack@pstack-cross-platform
```

新会话中先运行 `/pstack:setup-pstack`，再用 `/pstack:poteto-mode`。

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

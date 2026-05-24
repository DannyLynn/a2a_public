# Claude Code 接入任务

请阅读本文件中的 A2A 配置，并把当前 agent 项目接入 A2A 平台。

## 要求

1. 不要把真实 API Key 写入源码；
2. 使用环境变量读取 `A2A_SERVER_URL`、`A2A_AGENT_ID`、`A2A_API_KEY`；
3. 优先做最小可运行接入，不要重构无关代码；
4. 接入后运行本地启动命令，确认没有语法错误；
5. 如果找不到当前 agent 的处理函数，请先询问用户。

## 配置

```yaml
a2a:
  server_url: "{{SERVER_URL}}"
  agent_id: "{{AGENT_ID}}"
  api_key: "{{A2A_API_KEY}}"
```

## SDK

```bash
pip install "git+https://github.com/DannyLynn/a2a_public.git#subdirectory=sdk/python"
```

# Bot Monitor 🤖

**Universal process monitoring with LLM-powered analysis and Telegram notifications**

Monitor long-running processes on remote servers, get intelligent alerts when things go wrong. Perfect for ML training jobs, batch processing, deployments, or any long-running tasks where you need real-time failure notifications.

## Features

✅ **Universal Monitoring**
- 📄 Log files (with keyword filtering)
- 🔢 Process monitoring by PID
- 📋 Systemd journal tracking

✅ **LLM-Powered Analysis**
- Intelligent error detection
- Root cause analysis
- Actionable suggestions
- Context-aware event correlation

✅ **Multi-Provider Support**
- OpenAI (GPT-4o-mini)
- Anthropic (Claude)
- Groq (Llama 3.3 - Fast & Free)
- Ollama (Local/Private)

✅ **Smart Notifications**
- Rate limiting (avoid spam)
- Severity-based filtering
- Formatted Telegram messages
- Emoji indicators 🔴🟡🟢

## 🚀 Quick Start

### One-Command Setup

Run the interactive setup wizard - it will guide you through everything:

```bash
bot-monitor setup
```

**The wizard will:**
1. ✅ Collect and validate Telegram credentials (sends test message!)
2. ✅ Choose LLM provider and test API key
3. ✅ Configure monitors (files, PIDs, systemd services)
4. ✅ Validate file permissions and process access
5. ✅ Save complete working configuration
6. ✅ Offer to start monitoring immediately

**Example Session:**
```
🤖 Bot Monitor Setup Wizard
========================================

[1/5] Telegram Bot Configuration
----------------------------------------
To create a Telegram bot:
  1. Open Telegram and search for @BotFather
  2. Send: /newbot
  3. Follow instructions to create bot
  4. Copy the bot token

Enter Telegram Bot Token: 123456:ABC-DEF...
Enter your Telegram Chat ID: 987654321
✓ Validating Telegram setup...
✓ Success! Test message sent to Telegram!

[2/5] LLM Provider Configuration
----------------------------------------
Choose your LLM provider:
  1) OpenAI (Recommended, ~$0.15/1M tokens)
  2) Anthropic (High quality, ~$0.25/1M tokens)
  3) Groq (FREE tier, fast)
  4) Ollama (Local, private, FREE)

Choice [1-4]: 3
✓ Testing API key...
✓ API key validated! Model: llama-3.3-70b-versatile

[3/5] Monitor Configuration
----------------------------------------
Monitor log files? [Y/n]: y
  File path: /var/log/myapp.log
  ✓ File found and readable
  Keywords to watch (comma-separated) [ERROR,FATAL,Exception]: 
  Monitor name [myapp.log]: 
  ✓ File monitor configured: myapp.log

[4/5] Notification Settings
----------------------------------------
Max notifications per hour [10]: 15
✓ Rate limit: 15/hour

[5/5] Save Configuration
----------------------------------------
Configuration Summary:
  • Telegram: ✓ Bot configured
  • LLM: ✓ Groq (llama-3.3-70b-versatile)
  • Monitors: 1 configured
  • Rate limit: 15/hour

Save to ~/.config/bot-monitor/config.yaml? [Y/n]: y
✓ Configuration saved!

🚀 Setup complete! What next?
  1) Start monitoring now
  2) Exit (start manually later)

Choice [1-2]: 1

Starting bot-monitor...
✓ File monitor: myapp.log
✓ Monitoring active. Press Ctrl+C to stop.
```

### Configuration

Edit `~/.config/bot-monitor/config.yaml`:

```yaml
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  chat_id: "${TELEGRAM_CHAT_ID}"

llm:
  provider: "openai"  # openai, anthropic, groq, ollama
  api_key: "${LLM_API_KEY}"
  model: "gpt-4o-mini"

notification:
  debounce_seconds: 300
  rate_limit_per_hour: 10
  severity_levels: [critical, warning, info]

monitors:
  # Monitor a log file
  - type: file
    name: "Training Logs"
    path: "/var/log/training.log"
    keywords: ["ERROR", "FATAL", "Exception"]
  
  # Monitor a process
  - type: pid
    name: "ML Training"
    pid: 12345
    check_interval: 30
  
  # Monitor systemd service
  - type: journal
    name: "Web Server"
    unit: "nginx.service"
```

### Run

```bash
# Start monitoring
bot-monitor start

# Test notifications
bot-monitor test-notification

# Use custom config
bot-monitor -c /path/to/config.yaml start
```

## Use Cases

### ML Training Jobs
```yaml
monitors:
  - type: file
    name: "Training Logs"
    path: "/home/user/training/output.log"
    keywords: ["loss", "ERROR", "NaN", "diverged"]
  
  - type: pid
    name: "Training Process"
    pid: 98765
    check_interval: 60
```

### Web Deployments
```yaml
monitors:
  - type: journal
    name: "Application Server"
    unit: "myapp.service"
  
  - type: file
    name: "Nginx Error Log"
    path: "/var/log/nginx/error.log"
    keywords: ["error", "critical", "upstream"]
```

### Data Processing
```yaml
monitors:
  - type: file
    name: "ETL Pipeline"
    path: "/var/log/pipeline.log"
    keywords: ["FAILED", "TIMEOUT", "Exception"]
```

## LLM Provider Setup

### OpenAI (Recommended)
1. Get API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. Set environment variable: `export LLM_API_KEY=sk-...`
3. Configure provider: `openai` with model `gpt-4o-mini`

### Groq (Fast & Free)
1. Get free API key from [console.groq.com](https://console.groq.com)
2. Set environment variable: `export LLM_API_KEY=gsk_...`
3. Configure provider: `groq` with model `llama-3.3-70b-versatile`

### Anthropic
1. Get API key from [console.anthropic.com](https://console.anthropic.com)
2. Set environment variable: `export LLM_API_KEY=sk-ant-...`
3. Configure provider: `anthropic` with model `claude-3-5-haiku-20241022`

### Ollama (Local)
1. Install [Ollama](https://ollama.ai)
2. Pull model: `ollama pull llama3.2`
3. Configure provider: `ollama` with model `llama3.2`
4. No API key needed!

## Environment Variables

Use environment variables for sensitive data:

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
export TELEGRAM_CHAT_ID="987654321"
export LLM_API_KEY="sk-..."
```

Then reference in config:
```yaml
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  chat_id: "${TELEGRAM_CHAT_ID}"
```

## Systemd Service

Run as a system service:

```bash
# Create service file
sudo nano /etc/systemd/system/bot-monitor.service
```

```ini
[Unit]
Description=Bot Monitor
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/bot-monitor
Environment="TELEGRAM_BOT_TOKEN=..."
Environment="LLM_API_KEY=..."
ExecStart=/path/to/venv/bin/bot-monitor start
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable bot-monitor
sudo systemctl start bot-monitor
sudo systemctl status bot-monitor
```

## Troubleshooting

### "No configuration file found"
Run `bot-monitor setup` or create config at `~/.config/bot-monitor/config.yaml`

### "File not found" for log monitoring
Check file path exists and bot-monitor has read permissions

### "Process with PID X does not exist"
Update PID in config before starting

### Telegram messages not received
1. Check bot token is correct
2. Verify you've started a chat with the bot
3. Run `bot-monitor test-notification`
4. Check chat ID is your user ID, not group ID

### LLM API errors
1. Verify API key is set correctly
2. Check API quota/credits
3. Test with `bot-monitor test-notification`

## Architecture

```
┌─────────────────────────────────────────┐
│         Configuration (YAML)            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Monitor Manager                 │
└─┬───────────┬──────────────┬────────────┘
  │           │              │
  ▼           ▼              ▼
┌──────┐  ┌──────┐      ┌──────────┐
│File  │  │ PID  │      │ Journal  │
│Watch │  │Track │      │ Reader   │
└──┬───┘  └──┬───┘      └────┬─────┘
   │         │                │
   └────────┬┴────────────────┘
            ▼
    ┌───────────────┐
    │ Event Queue   │
    └───────┬───────┘
            ▼
    ┌───────────────┐
    │ LLM Analyzer  │
    └───────┬───────┘
            ▼
    ┌───────────────┐
    │   Telegram    │
    │   Notifier    │
    └───────────────┘
```

## Contributing

Contributions welcome! Please feel free to submit pull requests.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Project Issues](https://github.com/DevCrewX/TelegramRemoteProgressBot/issues)
- Telegram: Create an issue for support

---

Built with ❤️ for developers who need to monitor long-running processes without constant manual checking.

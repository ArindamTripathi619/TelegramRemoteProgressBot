# Telegram Remote Progress Bot - Brainstorming Session

## Project Intent (Stage 1)

### Goal Statement
Create a universal monitoring service that watches long-running processes on remote VMs/VPS, analyzes logs/journals/files using LLM, and sends intelligent notifications via Telegram when errors, crashes, or significant updates occur.

### Success Metrics
- ✅ Service can monitor any arbitrary process by PID, log files, or journal units
- ✅ LLM successfully detects and analyzes errors/crashes with context
- ✅ Telegram notifications are timely and actionable
- ✅ Installation takes < 5 minutes
- ✅ Configuration is intuitive and flexible

### Architecture Decision
**Modular Python Service** with:
- Lightweight daemon/background process
- Plugin-based monitoring (files, PIDs, journals)
- Asynchronous I/O for efficiency
- Simple YAML/JSON configuration

## Environment & Inputs (Stage 2)

### Hardware Considerations
- **Target Environment:** Remote Linux VMs/VPS (likely lower specs than dev machine)
- **Resource Constraints:** Must be lightweight (< 50MB RAM idle)
- **Dev Machine:** Can leverage 16-thread Ryzen 7 for testing/static analysis

### Dependencies
1. **Python 3.8+** (universal availability)
2. **python-telegram-bot** (Telegram Bot API)
3. **LLM API** (suggest OpenAI/Anthropic/local LLaMA)
4. **watchdog** (file monitoring)
5. **systemd** (service management)

### Data Sources
- Log files (arbitrary paths)
- systemd journal entries
- Process status via `/proc/[pid]`
- Custom file paths specified by user

## Technical Decisions (Stage 3)

### RAG Pipeline Assessment
**Decision: NO full RAG pipeline needed for Phase 1**
- Reasoning: Log snippets are already focused/relevant; no need for vector DB
- Instead: Use sliding window + recent context aggregation
- Future: Could add embeddings for pattern detection across sessions

### LLM Strategy
**Recommendation: Provider-agnostic design**
- Support OpenAI, Anthropic, Groq, Ollama (local)
- User configures via env vars
- Default: OpenAI (most accessible)

### Monitoring Approach
1. **File Watching:** `watchdog` library for real-time monitoring
2. **Journal Reading:** `journalctl` subprocess with `--follow`
3. **PID Tracking:** Poll `/proc/[pid]/status` and `/proc/[pid]/fd/*`

## Safety & Git Protocol (Stage 4)

### Git Setup
- **Permission Requested:** Will initialize repo after approval
- **Structure:**
  ```
  TelegramRemoteProgressBot/
  ├── src/
  │   ├── monitors/     # Monitoring modules
  │   ├── analyzers/    # LLM integration
  │   └── notifiers/    # Telegram bot
  ├── config/           # Example configs
  ├── install.sh        # Quick setup script
  └── README.md
  ```

### File Access
- No `.gitignore` conflicts expected for new project
- Will create comprehensive `.gitignore` for Python

## Execution Planning (Stage 5)

### Installation Flow
```bash
# One-liner install (goal)
curl -sSL https://raw.githubusercontent.com/.../install.sh | bash

# Interactive setup
bot-monitor setup
# Asks for:
# - Telegram Bot Token
# - Telegram Chat ID
# - LLM API key + provider
# - What to monitor
```

### Configuration Format (YAML)
```yaml
telegram:
  bot_token: "..."
  chat_id: "..."

llm:
  provider: "openai"  # openai, anthropic, groq, ollama
  api_key: "..."
  model: "gpt-4o-mini"

monitors:
  - type: file
    path: "/var/log/myapp.log"
    pattern: "ERROR|FATAL|Exception"
  
  - type: pid
    pid: 12345
    check_interval: 30
  
  - type: journal
    unit: "myservice.service"
```

### Notification Strategy
- **Debouncing:** Group similar errors within 5-minute window
- **Severity Levels:** 
  - 🔴 Critical (process crash, fatal errors)
  - 🟡 Warning (errors, unusual patterns)
  - 🟢 Info (milestones, completions)
- **Rate Limiting:** Max 10 messages/hour (configurable)

## Open Questions for User

1. **GitHub Repository:** Shall I create a public repo under your account?
2. **LLM Provider Preference:** OpenAI, Anthropic, Groq, or local Ollama?
3. **Service Name:** `bot-monitor`, `progress-watch`, or other preference?
4. **Installation Scope:** System-wide (`/usr/local`) or user-local (`~/.local`)?

## Next Steps

1. Get user approval on architecture
2. Initialize Git repository
3. Create project structure
4. Implement core monitoring engine
5. Integrate Telegram + LLM
6. Build setup wizard
7. Create installation script
8. Test with real use cases

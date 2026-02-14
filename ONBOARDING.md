# TeleWatch Onboarding Guide 🚀

Welcome to **TeleWatch**! This guide will help you go from "Just Installed" to "Mastering Remote Monitoring" in 10 minutes.

---

## 🏗️ 1. Initial Setup (The "Wizard" Way)

The fastest way to get started is the interactive setup wizard. It validates your credentials in real-time so you don't have to worry about typos.

```bash
bot-monitor setup
```

**What you'll need ready:**
1.  **Telegram Bot Token**: Create one via [@BotFather](https://t.me/botfather).
2.  **Chat ID**: Get yours via [@userinfobot](https://t.me/userinfobot) (it's usually a 9 or 10 digit number).
3.  **LLM API Key**: OpenAI, Anthropic, or Groq (Groq is highly recommended for its speed and free tier).

---

## 🕹️ 2. Mastering Interactive Commands

Once your bot is running, you don't need to touch your terminal. Just message your bot directly:

*   **`/status`**: "How is my job doing?" — Returns a weighted progress bar and a 1-sentence LLM summary of recent activity.
*   **`/logs`**: "Show me what's happening." — Dumps the last 15 lines of the monitored log.
*   **`/pause`**: "Wait, something's weird." — Suspends analysis if you need to manually intervene in your process without getting spam alerts.
*   **`/resume`**: "Carry on." — Re-activates monitoring.

---

## 🧬 3. Understanding Behavioral Sentinels

TeleWatch doesn't just look for "ERROR". It understands how your process *behaves*:

### 📈 Anomaly Detection
If your log suddenly starts spitting out 100 lines per second (when usually it's 1), TeleWatch will alert you of a **Log Frequency Spike**.

### 🧬 Structural Novelty
If a new *type* of log line appears that looks like an error but doesn't match known patterns, TeleWatch uses its **Skeleton Hashing** to identify it as a "Structural Novelty" and analyzes it via LLM.

### 🛑 Stall Detection
If your process is supposed to be logging but hasn't said a word in 10 minutes, you'll get a **Stall Alert**.

---

## 🏁 4. Advanced: Multi-Stage Tracking

Don't just track 0-100%. Track the *phases* of your work. Update your `config.yaml`:

```yaml
process:
  name: "Deep Learning Training"
  stages:
    - name: "Data Loading"
      weight: 1           # 10% of total time
      start_pattern: "Loading dataset"
    - name: "Training"
      weight: 8           # 80% of total time
      start_pattern: "Epoch 1"
    - name: "Evaluation"
      weight: 1           # 10% of total time
      start_pattern: "Starting Eval"
```

TeleWatch will calculate your total progress across all phases and notify you when each 🚩 **Stage Transition** occurs.

---

## 🧠 5. Historical Duration Learning

TeleWatch remembers. Every time your process completes, it saves the duration to `~/.telewatch/history.json`.

**The Magic:** If you don't know how long your process will take, leave `expected_duration_minutes` blank. TeleWatch will automatically use the average of your last few runs to calculate completion time.

---

## ⚡ 6. Efficiency Tips

1.  **Use Groq**: It's incredibly fast and fits perfectly with TeleWatch's lightweight philosophy.
2.  **Fuzzy Caching**: TeleWatch automatically caches similar logs. You only pay for LLM analysis *once* for structurally identical error patterns.
3.  **Daemon Mode**: Use `bot-monitor start --daemon` to run in the background.

---

## 🆘 Need Help?
- Run `bot-monitor --help` for a list of all commands.
- Check the [README.md](./README.md) for detailed architecture and configuration options.

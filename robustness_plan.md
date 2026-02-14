### A. Automatic Schema Discovery (Phase 1)
Instead of asking the user for patterns, the bot will implement a **Profiling Phase** during the first 60 seconds of monitoring:
- **Structure Mapping:** Identify field delimiters (spaces, pipes, brackets) to extract timestamps, log levels, and message components.
- **Baseline Generation:** Create a "Frequency Baseline" of common log lines (noise reduction).
- **Format Inference:** Automatically detect if the log is JSON, CSV, or standard Syslog format.

### B. LLM-Generated Pattern Library (Phase 2)
The LLM should transition from a "Passive Analyzer" to an "Active Teacher":
1. **Bootstrap Mode:** When an unknown error occurs, the LLM analyzes it and *generates a regex* that matches similar future errors.
2. **Local Pattern Injection:** These generated regexes are added to the local `pattern_matcher.py` dynamically, reducing subsequent LLM costs.
3. **Similarity Clustering:** Use fuzzy matching (Levenshtein distance) for the analysis cache signature instead of exact strings.

### C. Structural Resilience
- **Windowed Buffering:** Instead of processing one line at a time, use a sliding window (e.g., 5 lines) to capture context. This allows the bot to "see" a stack trace following an error.
- **Adaptive Progress Extraction:**
    * If regex fails, the `ProgressTracker` will send a sample of the last 10 lines to the LLM with a prompt: *"Identify the progress indicator in these lines and return a JSON mapping for extraction."*
    * The bot then updates its internal extraction logic for that session.

### D. Anomaly-Based Triggering
Move beyond "keyword-only" monitoring:
- **Temporal Anomalies:** Trigger alerts if the log frequency suddenly drops (process stalled) or spikes (log spam/crash loop).
- **Novelty Detection:** Trigger the LLM only for line structures that have not been seen in the last 1,000 lines, regardless of keywords.

### "Dirty Log" Testing Suite
Create a new series of tests using:
- **Unstructured Logs:** Actual logs from common tools (Nginx, Docker, Kubernetes, Jenkins).
- **Corrupted Logs:** Logs with missing fields or interleaved output from multiple threads.
- **The "Chaos Monkey" for Logs:** A script that randomly alters log formats mid-stream to verify the bot's ability to re-profile.

### Manual Verification
- Deploy the bot on a live, high-traffic server (e.g., a web crawler or a busy CI/CD runner) and measure:
    * **LLM Fallback Rate:** Percentage of events that required LLM vs. were handled by adaptive local patterns.
    * **False Negative Rate:** Critical errors missed because they didn't match the *initial* profile.

---

> [!IMPORTANT]
> The goal of this plan is to minimize manual configuration. A truly robust bot should only require a `File Path` and a `Telegram Token` to start providing value.

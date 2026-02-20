# LLM API Rotator: API Endpoints & Programmatic Access Report

This report provides a detailed guide on how to integrate and use your local LLM API rotation service.

## 1. Connection Details

The service runs locally and mimics the OpenAI API standard, making it compatible with almost any LLM client.

- **Base URL:** `http://localhost:8000/v1`
- **Default Port:** `8000`
- **Auth Key:** Not required (you can pass any dummy string like `sk-xxxx`).

## 2. Available Models

I have grouped your 13 API keys (11 Groq, 5 Gemini) into three virtual models. The service automatically rotates through the underlying keys whenever one hits a rate limit.

| Model Name | Provider | Best Used For | Features |
| :--- | :--- | :--- | :--- |
| `groq-llama` | Groq | Lightning-fast Chat / Coding | 11 Keys, Round-robin rotation |
| `gemini-flash` | Gemini | Vision (Image Analysis) / Long Context | 5 Keys, Free-tier rotation |
| `gemini-image` | Gemini | Image Generation (Imagen 3) | 5 Keys, *Requires daily quota reset* |

## 3. Programmatic Access Examples

### Python (using OpenAI library)
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="anything"
)

# Chat with Groq (Fast)
response = client.chat.completions.create(
    model="groq-llama",
    messages=[{"role": "user", "content": "Write a quick python script for a timer."}]
)
print(response.choices[0].message.content)

# Image Analysis with Gemini
# Note: You can pass image URLs or base64 data here as per standard OpenAI Vision format.
```

### JavaScript / Node.js
```javascript
const response = await fetch("http://localhost:8000/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer local-rotator"
  },
  body: JSON.stringify({
    model: "groq-llama",
    messages: [{ role: "user", content: "Tell me a joke." }]
  })
});
const data = await response.json();
console.log(data.choices[0].message.content);
```

### Curl (CLI)
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "groq-llama",
    "messages": [{"role": "user", "content": "How does key rotation work?"}]
  }'
```

## 4. Advanced Features

*   **Automatic Key Rotation:** If one key fails with a `429 Too Many Requests` error, the service automatically retries with the next available key in the list.
*   **Cooldown Period:** Keys that hit their limit are moved to a "cooldown" state for 60 seconds before being put back into rotation.
*   **System Persistence:** The service starts automatically with your laptop (`llm-rotator.service`).
*   **Stats & Debugging:** You can view the live status of the LiteLLM proxy by visiting `http://localhost:8000/` in your browser (includes a Swagger UI for testing).

---
*Report Generated: 2026-02-20*

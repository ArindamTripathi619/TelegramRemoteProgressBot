"""Multi-provider LLM client."""

import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMError(Exception):
    """LLM error."""
    pass


class BaseLLMClient(ABC):
    """Base LLM client interface."""
    
    @abstractmethod
    def analyze(self, prompt: str) -> str:
        """Analyze with LLM.
        
        Args:
            prompt: Analysis prompt.
            
        Returns:
            LLM response.
        """
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize client.
        
        Args:
            api_key: OpenAI API key.
            model: Model name.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise LLMError("openai package not installed. Run: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def analyze(self, prompt: str) -> str:
        """Analyze with OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a log analysis expert helping monitor system processes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMError(f"OpenAI API error: {e}")


class AnthropicClient(BaseLLMClient):
    """Anthropic client."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        """Initialize client.
        
        Args:
            api_key: Anthropic API key.
            model: Model name.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise LLMError("anthropic package not installed. Run: pip install anthropic")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def analyze(self, prompt: str) -> str:
        """Analyze with Anthropic."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            return response.content[0].text
        except Exception as e:
            raise LLMError(f"Anthropic API error: {e}")


class GroqClient(BaseLLMClient):
    """Groq client."""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """Initialize client.
        
        Args:
            api_key: Groq API key.
            model: Model name.
        """
        try:
            from groq import Groq
        except ImportError:
            raise LLMError("groq package not installed. Run: pip install groq")
        
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def analyze(self, prompt: str) -> str:
        """Analyze with Groq."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a log analysis expert helping monitor system processes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMError(f"Groq API error: {e}")


class OllamaClient(BaseLLMClient):
    """Ollama (local) client."""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        """Initialize client.
        
        Args:
            model: Model name.
            base_url: Ollama API URL.
        """
        import requests
        self.requests = requests
        self.model = model
        self.base_url = base_url.rstrip("/")
    
    def analyze(self, prompt: str) -> str:
        """Analyze with Ollama."""
        try:
            response = self.requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a log analysis expert helping monitor system processes."},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            raise LLMError(f"Ollama API error: {e}")


def create_llm_client(config: Dict[str, Any]) -> BaseLLMClient:
    """Create LLM client from configuration.
    
    Args:
        config: LLM configuration.
        
    Returns:
        LLM client instance.
    """
    provider = config["provider"].lower()
    
    if provider == "openai":
        return OpenAIClient(
            api_key=config["api_key"],
            model=config.get("model", "gpt-4o-mini")
        )
    elif provider == "anthropic":
        return AnthropicClient(
            api_key=config["api_key"],
            model=config.get("model", "claude-3-5-haiku-20241022")
        )
    elif provider == "groq":
        return GroqClient(
            api_key=config["api_key"],
            model=config.get("model", "llama-3.3-70b-versatile")
        )
    elif provider == "ollama":
        return OllamaClient(
            model=config.get("model", "llama3.2"),
            base_url=config.get("base_url", "http://localhost:11434")
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

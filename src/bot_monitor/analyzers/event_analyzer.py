"""Event analysis logic."""

import json
from typing import Dict, Any, List
from dataclasses import dataclass

from ..monitors.base import MonitorEvent, Severity
from .llm_client import BaseLLMClient, LLMError


@dataclass
class Analysis:
    """Analysis result."""
    severity: Severity
    summary: str
    root_cause: str
    suggested_action: str
    original_event: MonitorEvent


class EventAnalyzer:
    """Analyzes events using LLM."""
    
    def __init__(self, llm_client: BaseLLMClient, context_size: int = 10):
        """Initialize analyzer.
        
        Args:
            llm_client: LLM client.
            context_size: Number of previous events to include for context.
        """
        self.llm_client = llm_client
        self.context_size = context_size
        self.event_history: List[MonitorEvent] = []
    
    def analyze_event(self, event: MonitorEvent) -> Analysis:
        """Analyze an event with LLM.
        
        Args:
            event: Event to analyze.
            
        Returns:
            Analysis result.
        """
        # Build context from history
        context_events = self.event_history[-self.context_size:] if self.event_history else []
        
        # Create prompt
        prompt = self._build_prompt(event, context_events)
        
        try:
            # Get LLM analysis
            response = self.llm_client.analyze(prompt)
            
            # Parse response
            analysis = self._parse_response(response, event)
            
            # Add to history
            self.event_history.append(event)
            
            return analysis
        
        except LLMError as e:
            # Fallback to basic analysis if LLM fails
            return Analysis(
                severity=event.severity,
                summary=event.content[:100],
                root_cause=f"LLM analysis failed: {e}",
                suggested_action="Manual investigation required",
                original_event=event
            )
    
    def _build_prompt(self, event: MonitorEvent, context: List[MonitorEvent]) -> str:
        """Build analysis prompt.
        
        Args:
            event: Current event.
            context: Previous events for context.
            
        Returns:
            Formatted prompt.
        """
        prompt = """You are analyzing logs from a monitoring system. Based on the information below, provide a structured analysis.

**Your task:**
1. Assess the severity (CRITICAL, WARNING, or INFO)
2. Identify the root cause if it's an error
3. Suggest a specific action to take
4. Provide a one-line summary

**Recent Context (previous events):**
"""
        
        if context:
            for ctx_event in context:
                prompt += f"[{ctx_event.timestamp.strftime('%H:%M:%S')}] {ctx_event.source}: {ctx_event.content[:200]}\n"
        else:
            prompt += "(No previous context)\n"
        
        prompt += f"""
**Current Event:**
Source: {event.source}
Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Content:
{event.content}

**Required Response Format (JSON):**
{{
  "severity": "CRITICAL|WARNING|INFO",
  "summary": "One-line description",
  "root_cause": "What caused this (if error)",
  "suggested_action": "What to do next"
}}

Respond ONLY with valid JSON.
"""
        
        return prompt
    
    def _parse_response(self, response: str, event: MonitorEvent) -> Analysis:
        """Parse LLM response.
        
        Args:
            response: LLM response text.
            event: Original event.
            
        Returns:
            Parsed analysis.
        """
        try:
            # Try to parse as JSON
            # Extract JSON from markdown code blocks if present
            response = response.strip()
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            data = json.loads(response)
            
            # Map severity
            severity_map = {
                "CRITICAL": Severity.CRITICAL,
                "WARNING": Severity.WARNING,
                "INFO": Severity.INFO,
            }
            severity = severity_map.get(data.get("severity", "INFO").upper(), Severity.INFO)
            
            return Analysis(
                severity=severity,
                summary=data.get("summary", "Event detected")[:200],
                root_cause=data.get("root_cause", "Unknown")[:300],
                suggested_action=data.get("suggested_action", "Monitor")[:300],
                original_event=event
            )
        
        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback parsing if JSON fails
            return Analysis(
                severity=event.severity,
                summary=response[:100] if response else event.content[:100],
                root_cause="Unable to parse LLM response",
                suggested_action="Review original event",
                original_event=event
            )

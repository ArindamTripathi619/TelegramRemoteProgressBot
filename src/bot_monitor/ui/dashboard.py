from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.live import Live
from datetime import datetime

class Dashboard:
    def __init__(self, title="TeleWatch Monitor"):
        self.console = Console()
        self.title = title
        self.layout = Layout()
        self.setup_layout()
        
    def setup_layout(self):
        """Define the dashboard layout."""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
    def generate_header(self, process_name: str, status: str, profiler_progress: float = 0.0):
        """Generate the header panel."""
        status_color = "green" if status == "running" else "red"
        
        # If profiling is active (e.g., < 100% and we are in learning phase)
        # For simplicity, we'll use a special status if profiling
        status_text = status.upper()
        if 0 < profiler_progress < 1.0:
            status_text = f"PROFILING {int(profiler_progress * 100)}%"
            status_color = "yellow"

        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"[b cyan]{self.title}[/b cyan] | Monitoring: [b white]{process_name}[/b white]",
            f"Status: [{status_color}]{status_text}[/{status_color}] | {datetime.now().strftime('%H:%M:%S')}"
        )
        return Panel(grid, style="blue")

    def generate_progress(self, progress: float, message: str, profiler_progress: float = 0.0):
        """Generate the main progress display."""
        # This is a static rendering for layout; actual progress bar needs rich.Progress integration
        # For layout purposes, creating a visual representation
        
        is_profiling = 0 < profiler_progress < 1.0
        
        if is_profiling:
            completed = int(profiler_progress * 50)
            bar = "█" * completed + "░" * (50 - completed)
            main_msg = "LEARNING LOG STRUCTURE..."
            pct = profiler_progress * 100
            bar_color = "yellow"
        else:
            completed = int(progress / 2)  # 50 chars width
            bar = "█" * completed + "░" * (50 - completed)
            main_msg = message
            pct = progress
            bar_color = "cyan"
        
        text = Text()
        text.append(f"\n{main_msg}\n\n", style="bold white")
        text.append(f"{bar} ", style=bar_color)
        text.append(f"{pct:.1f}%\n", style="bold green")
        
        return Panel(
            Align.center(text),
            title="Monitoring Status" if not is_profiling else "Initialization",
            border_style="green" if not is_profiling else "yellow"
        )
        
    def generate_stats(self, token_stats: dict):
        """Generate statistics panel."""
        table = Table(show_header=False, expand=True, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        # Calculate uptime
        uptime_sec = token_stats.get("uptime_seconds", 0)
        hours = uptime_sec // 3600
        minutes = (uptime_sec % 3600) // 60
        seconds = uptime_sec % 60
        if hours > 0:
            uptime_str = f"{hours}h {minutes}m"
        elif minutes > 0:
            uptime_str = f"{minutes}m {seconds}s"
        else:
            uptime_str = f"{seconds}s"
            
        table.add_row("⏱️  Uptime", uptime_str)
        table.add_row("🧠 LLM Calls", str(token_stats.get("llm_calls", 0)))
        table.add_row("🎟️  Tokens", str(token_stats.get("total_tokens", 0)))
        table.add_row("💾 Cache Hits", f"{token_stats.get('cached_calls', 0)} ({token_stats.get('cache_hit_rate', 0)}%)")
        table.add_row("🎯 Patterns", f"{token_stats.get('pattern_matched', 0)} (+{token_stats.get('dynamic_patterns', 0)} dynamic)")
        
        # Add anomaly stats
        anomaly_stats = token_stats.get("anomaly_stats", {})
        table.add_row("📈 Frequency", f"{anomaly_stats.get('frequency', 0.0):.1f} L/min")
        table.add_row("🔍 Structures", str(anomaly_stats.get("known_structures", 0)))
        
        return Panel(
            table,
            title="Statistics",
            border_style="yellow"
        )
        
    def generate_logs(self, recent_logs: list):
        """Generate log tail panel."""
        log_text = Text()
        for log in recent_logs[-10:]:
            log_text.append(f"{log}\n")
            
        return Panel(
            log_text,
            title="Recent Activity",
            border_style="white",
            style="dim"
        )
        
    def generate_footer(self):
        """Generate footer with controls info."""
        return Panel(
            Align.center("[dim]Press [b]Ctrl+C[/b] to stop monitoring | [b]telewatch status[/b] to check remotely[/dim]"),
            style="blue"
        )

    def render(self, state, token_stats, recent_logs):
        """Update the entire layout."""
        # Calculate profiler progress
        # Assuming state might have profiler_progress or we pass it via token_stats for now
        profiler_progress = token_stats.get("profiler_progress", 0.0)
        
        self.layout["header"].update(self.generate_header(state.process_name, state.status, profiler_progress))
        self.layout["left"].update(self.generate_progress(state.progress, state.message, profiler_progress))
        self.layout["right"].update(self.generate_stats(token_stats)) 
        self.layout["footer"].update(self.generate_footer())
        
        return self.layout

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
        
    def generate_header(self, process_name: str, status: str):
        """Generate the header panel."""
        status_color = "green" if status == "running" else "red"
        
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"[b cyan]{self.title}[/b cyan] | Monitoring: [b white]{process_name}[/b white]",
            f"Status: [{status_color}]{status.upper()}[/{status_color}] | {datetime.now().strftime('%H:%M:%S')}"
        )
        return Panel(grid, style="blue")

    def generate_progress(self, progress: float, message: str):
        """Generate the main progress display."""
        # This is a static rendering for layout; actual progress bar needs rich.Progress integration
        # For layout purposes, creating a visual representation
        
        completed = int(progress / 2)  # 50 chars width
        bar = "█" * completed + "░" * (50 - completed)
        
        text = Text()
        text.append(f"\n{message}\n\n", style="bold white")
        text.append(f"{bar} ", style="cyan")
        text.append(f"{progress:.1f}%\n", style="bold green")
        
        return Panel(
            Align.center(text),
            title="Current Progress",
            border_style="green"
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
        table.add_row("🎯 Patterns", str(token_stats.get("pattern_matched", 0)))
        
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
        self.layout["header"].update(self.generate_header(state.process_name, state.status))
        self.layout["left"].update(self.generate_progress(state.progress, state.message))
        self.layout["right"].update(self.generate_stats(token_stats)) 
        # self.layout["main"]["bottom"].update(self.generate_logs(recent_logs)) # If we split left further
        self.layout["footer"].update(self.generate_footer())
        
        return self.layout

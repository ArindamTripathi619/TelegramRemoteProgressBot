import typer
import sys
import os
import signal
import time
from pathlib import Path
from rich.console import Console
from rich.live import Live

from bot_monitor.config import Config
from bot_monitor.cli import MonitorManager  # We will keep the manager logic but wrap it
from bot_monitor.core.state import StateManager, BotState
from bot_monitor.ui.wizard import SetupWizard
from bot_monitor.ui.dashboard import Dashboard

app = typer.Typer(help="TeleWatch - Remote Process Sentinel")
console = Console()
state_manager = StateManager()

def get_config_path() -> Path:
    return Path.home() / ".config" / "bot-monitor" / "config.yaml"

@app.command()
def setup():
    """Run interactive setup wizard."""
    wizard = SetupWizard()
    wizard.run()

@app.command()
def start(
    daemon: bool = typer.Option(False, "--daemon", "-d", help="Run in background mode"),
    config: Path = typer.Option(None, "--config", "-c", help="Path to config file")
):
    """Start the monitoring process."""
    if not config:
        config = get_config_path()
    
    if not config.exists():
        console.print("[red]❌ Config not found![/red] Run [bold]telewatch setup[/bold] first.")
        raise typer.Exit(1)
        
    if state_manager.is_running():
        console.print("[yellow]⚠️  TeleWatch is already running![/yellow]")
        raise typer.Exit(1)

    if daemon:
        _start_daemon(config)
    else:
        _run_monitor(config, daemon=False)

@app.command()
def status():
    """Check status of the running daemon."""
    state = state_manager.load_state()
    pid = state_manager.get_daemon_pid()
    
    if not pid:
        console.print("[red]❌ TeleWatch is NOT running.[/red]")
        if state.last_update > 0:
            console.print(f"[dim]Last status: {state.status} (Update: {state.last_update})[/dim]")
        raise typer.Exit(1)
    
    # Render one-shot dashboard
    dashboard = Dashboard()
    # Dummy stats for now, real stats would come from shared state/file
    token_stats = {"calls": 0, "total_tokens": 0} 
    
    console.print(dashboard.render(state, token_stats, []))

@app.command()
def stop():
    """Stop the background daemon."""
    pid = state_manager.get_daemon_pid()
    if not pid:
        console.print("[yellow]⚠️  No daemon running.[/yellow]")
        return

    try:
        os.kill(pid, signal.SIGTERM)
        console.print(f"[green]✅ Sent stop signal to PID {pid}[/green]")
        state_manager.remove_pid()
        state_manager.set_stopped()
    except ProcessLookupError:
        console.print("[red]❌ Process not found (stale lockfile removed).[/red]")
        state_manager.remove_pid()
    except Exception as e:
        console.print(f"[red]❌ Error stopping process: {e}[/red]")

def _start_daemon(config_path: Path):
    """Fork and start background process."""
    console.print("[bold green]🚀 Starting TeleWatch in background...[/bold green]")
    
    pid = os.fork()
    if pid > 0:
        # Parent exits
        sys.exit(0)
    
    # Child continues
    os.setsid()
    
    # Redirect standard file descriptors
    sys.stdin.close()
    sys.stdout = open(state_manager.log_file, 'a+')
    sys.stderr = open(state_manager.log_file, 'a+')
    
    _run_monitor(config_path, daemon=True)

def _run_monitor(config_path: Path, daemon: bool):
    """Main monitoring loop."""
    try:
        conf = Config(config_path)
        manager = MonitorManager(conf)
        
        # Write PID and initial state
        state_manager.set_running(conf.data.get("process", {}).get("name", "Unknown"))
        
        manager.setup_monitors()
        
        # If interactive (not daemon), use rich live display
        if not daemon:
            dashboard = Dashboard()
            with Live(refresh_per_second=4) as live:
                # Monkey patch/hook into manager to update UI
                # For now, simplistic approach: Run manager in thread or modify manager to callback
                # Since Manager has its own loop, we need to adapt it.
                # EASIEST PATH: We subclass/modify MonitorManager to update StateManager
                
                # Update manager to update state
                def on_progress(p, msg):
                    # Get behavioral stats
                    a_stats = manager.analyzer.anomaly_detector.get_stats() if hasattr(manager.analyzer, 'anomaly_detector') else {}
                    
                    state_manager.update_status(
                        p, msg, "running",
                        frequency=a_stats.get('frequency', 0.0),
                        structures=a_stats.get('known_structures', 0),
                        stalled=(p == 0.0 and msg.startswith("⚠️")) # Simple heuristic if manager doesn't pass it
                    )
                    
                    if not daemon:
                        # Fetch latest state to render
                        current_state = state_manager.load_state()
                        # Get token stats if available
                        t_stats = manager.analyzer.get_token_stats() if hasattr(manager, 'analyzer') else {}
                        live.update(dashboard.render(current_state, t_stats, []))
                
                # Inject callback (we need to modify MonitorManager to support this or wrapper)
                # For this implementation plan, we assume MonitorManager is robust enough or we wrap it.
                # Actually, best to just run it and let it update the file, and Live reads the file?
                # No, that's inefficient.
                
                # Let's modify MonitorManager to accept a callback for UI updates
                manager.set_ui_callback(on_progress)
                manager.start() # This blocks in original CLI. We need it to be non-blocking or managed.
                
        else:
            # Daemon mode - just run
            def on_progress(p, msg):
                # Get behavioral stats
                a_stats = manager.analyzer.anomaly_detector.get_stats() if hasattr(manager.analyzer, 'anomaly_detector') else {}
                
                state_manager.update_status(
                    p, msg, "running",
                    frequency=a_stats.get('frequency', 0.0),
                    structures=a_stats.get('known_structures', 0),
                    stalled=(p == 0.0 and msg.startswith("⚠️"))
                )
                
            manager.set_ui_callback(on_progress)
            manager.start()

    except Exception as e:
        state_manager.update_status(0, f"Error: {e}", "error")
        if not daemon:
            console.print(f"[red]Fatal Error: {e}[/red]")
        sys.exit(1)
    finally:
        state_manager.set_stopped()

if __name__ == "__main__":
    app()

"""Main CLI interface for bot-monitor."""

import argparse
import sys
import time
import signal
import os
from pathlib import Path
from typing import Optional, List

from .config import Config, ConfigError, create_example_config
from .monitors import FileMonitor, PIDMonitor, JournalMonitor, BaseMonitor
from .analyzers import create_llm_client, EventAnalyzer
from .notifiers import TelegramNotifier


class MonitorManager:
    """Manages all monitors and orchestrates the monitoring loop."""
    
    def __init__(self, config: Config):
        """Initialize manager.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        self.monitors: List[BaseMonitor] = []
        self.running = False
        
        # Initialize LLM and notifier
        llm_config = config.get_llm_config()
        self.llm_client = create_llm_client(llm_config)
        self.analyzer = EventAnalyzer(self.llm_client)
        
        telegram_config = config.get_telegram_config()
        notification_config = config.get_notification_config()
        self.notifier = TelegramNotifier(
            bot_token=telegram_config["bot_token"],
            chat_id=telegram_config["chat_id"],
            rate_limit_per_hour=notification_config["rate_limit_per_hour"]
        )
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\nShutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def setup_monitors(self):
        """Create and configure monitors from config."""
        monitor_configs = self.config.get_monitors()
        
        for mon_config in monitor_configs:
            mon_type = mon_config["type"]
            name = mon_config.get("name", f"{mon_type}_monitor")
            
            try:
                if mon_type == "file":
                    monitor = FileMonitor(name, mon_config)
                elif mon_type == "pid":
                    monitor = PIDMonitor(name, mon_config)
                elif mon_type == "journal":
                    monitor = JournalMonitor(name, mon_config)
                else:
                    print(f"Warning: Unknown monitor type '{mon_type}', skipping")
                    continue
                
                self.monitors.append(monitor)
                print(f"✓ Configured {mon_type} monitor: {name}")
            
            except Exception as e:
                print(f"✗ Failed to setup {mon_type} monitor '{name}': {e}")
    
    def start(self):
        """Start all monitors and main loop."""
        if not self.monitors:
            print("No monitors configured!")
            return
        
        print(f"\n🚀 Starting {len(self.monitors)} monitor(s)...")
        
        # Start all monitors
        for monitor in self.monitors:
            try:
                monitor.start()
                print(f"  ▶ {monitor.name}")
            except Exception as e:
                print(f"  ✗ Failed to start {monitor.name}: {e}")
        
        self.running = True
        print("\n✓ Monitoring active. Press Ctrl+C to stop.\n")
        
        # Main event loop
        self._event_loop()
    
    def _event_loop(self):
        """Main event processing loop."""
        while self.running:
            # Collect events from all monitors
            for monitor in self.monitors:
                if not monitor.is_running():
                    continue
                
                events = monitor.get_events()
                
                for event in events:
                    try:
                        # Analyze event
                        analysis = self.analyzer.analyze_event(event)
                        
                        # Send notification
                        success = self.notifier.send_analysis(analysis)
                        
                        if success:
                            print(f"📤 Sent: {analysis.summary}")
                        else:
                            print(f"⏸️  Skipped: {analysis.summary} (rate limit)")
                    
                    except Exception as e:
                        print(f"Error processing event: {e}")
            
            # Sleep briefly
            time.sleep(1)
    
    def stop(self):
        """Stop all monitors."""
        self.running = False
        
        print("Stopping monitors...")
        for monitor in self.monitors:
            try:
                monitor.stop()
            except Exception as e:
                print(f"Error stopping {monitor.name}: {e}")


def cmd_setup(args):
    """Interactive setup wizard."""
    print("🤖 Bot Monitor Setup Wizard")
    print("=" * 40)
    print()
    
    config_data = {
        "telegram": {},
        "llm": {},
        "notification": {
            "debounce_seconds": 300,
            "rate_limit_per_hour": 10,
            "severity_levels": ["critical", "warning", "info"]
        },
        "monitors": []
    }
    
    # Step 1: Telegram Configuration
    print("[1/5] Telegram Bot Configuration")
    print("-" * 40)
    print("To create a Telegram bot:")
    print("  1. Open Telegram and search for @BotFather")
    print("  2. Send: /newbot")
    print("  3. Follow instructions to create bot")
    print("  4. Copy the bot token")
    print()
    
    # Get and validate Telegram credentials
    while True:
        bot_token = input("Enter Telegram Bot Token: ").strip()
        if not bot_token:
            print("❌ Bot token cannot be empty")
            continue
        
        chat_id = input("Enter your Telegram Chat ID: ").strip()
        print("  (Don't know? Send /start to @userinfobot)")
        if not chat_id:
            print("❌ Chat ID cannot be empty")
            continue
        
        # Validate Telegram setup
        print("✓ Validating Telegram setup...")
        try:
            notifier = TelegramNotifier(bot_token, chat_id)
            if notifier.send_test_message():
                print("✓ Success! Test message sent to Telegram!")
                config_data["telegram"]["bot_token"] = bot_token
                config_data["telegram"]["chat_id"] = chat_id
                break
            else:
                print("❌ Failed to send test message. Check your bot token and chat ID.")
        except Exception as e:
            print(f"❌ Telegram validation failed: {e}")
            retry = input("Try again? [Y/n]: ").strip().lower()
            if retry == 'n':
                print("Setup cancelled.")
                sys.exit(1)
    
    # Step 2: LLM Provider Configuration
    print()
    print("[2/5] LLM Provider Configuration")
    print("-" * 40)
    print("Choose your LLM provider:")
    print("  1) OpenAI (Recommended, ~$0.15/1M tokens)")
    print("  2) Anthropic (High quality, ~$0.25/1M tokens)")
    print("  3) Groq (FREE tier, fast)")
    print("  4) Ollama (Local, private, FREE)")
    print()
    
    provider_map = {"1": "openai", "2": "anthropic", "3": "groq", "4": "ollama"}
    model_map = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022",
        "groq": "llama-3.3-70b-versatile",
        "ollama": "llama3.2"
    }
    
    while True:
        choice = input("Choice [1-4]: ").strip()
        provider = provider_map.get(choice)
        if provider:
            break
        print("❌ Invalid choice. Please enter 1, 2, 3, or 4")
    
    config_data["llm"]["provider"] = provider
    config_data["llm"]["model"] = model_map[provider]
    
    # Get API key for non-local providers
    if provider != "ollama":
        print(f"\nSetting up {provider.capitalize()}...")
        if provider == "groq":
            print("Get FREE API key: https://console.groq.com/keys")
        elif provider == "openai":
            print("Get API key: https://platform.openai.com/api-keys")
        elif provider == "anthropic":
            print("Get API key: https://console.anthropic.com/")
        print()
        
        while True:
            api_key = input(f"Enter {provider.capitalize()} API Key: ").strip()
            if not api_key:
                print("❌ API key cannot be empty")
                continue
            
            # Validate LLM setup
            print("✓ Testing API key...")
            try:
                from .analyzers import create_llm_client
                test_config = {
                    "provider": provider,
                    "api_key": api_key,
                    "model": config_data["llm"]["model"]
                }
                client = create_llm_client(test_config)
                # Make a simple test call
                response = client.analyze("Respond with 'OK' if you can read this.")
                print(f"✓ API key validated! Model: {config_data['llm']['model']}")
                config_data["llm"]["api_key"] = api_key
                break
            except Exception as e:
                print(f"❌ API validation failed: {e}")
                retry = input("Try again? [Y/n]: ").strip().lower()
                if retry == 'n':
                    print("Setup cancelled.")
                    sys.exit(1)
    else:
        print("\n✓ Using Ollama (local)")
        config_data["llm"]["base_url"] = "http://localhost:11434"
        print(f"  Model: {config_data['llm']['model']}")
    
    # Step 3: Monitor Configuration
    print()
    print("[3/5] Monitor Configuration")
    print("-" * 40)
    print("What would you like to monitor?")
    print()
    
    # File monitor
    add_file = input("Monitor log files? [Y/n]: ").strip().lower()
    if add_file != 'n':
        while True:
            file_path = input("  File path: ").strip()
            if not file_path:
                break
            
            # Validate file exists and is readable
            path_obj = Path(file_path).expanduser()
            if not path_obj.exists():
                print(f"  ❌ File not found: {file_path}")
                continue
            if not path_obj.is_file():
                print(f"  ❌ Not a file: {file_path}")
                continue
            if not os.access(path_obj, os.R_OK):
                print(f"  ❌ File not readable: {file_path}")
                continue
            
            print(f"  ✓ File found and readable")
            
            keywords_input = input("  Keywords to watch (comma-separated) [ERROR,FATAL,Exception]: ").strip()
            keywords = [k.strip() for k in keywords_input.split(",")] if keywords_input else ["ERROR", "FATAL", "Exception"]
            
            name = input(f"  Monitor name [{path_obj.name}]: ").strip() or path_obj.name
            
            config_data["monitors"].append({
                "type": "file",
                "name": name,
                "path": str(path_obj),
                "keywords": keywords
            })
            print(f"  ✓ File monitor configured: {name}")
            
            another = input("\n  Add another file? [y/N]: ").strip().lower()
            if another != 'y':
                break
    
    # PID monitor
    print()
    add_pid = input("Monitor process by PID? [y/N]: ").strip().lower()
    if add_pid == 'y':
        while True:
            try:
                pid_input = input("  PID: ").strip()
                if not pid_input:
                    break
                
                pid = int(pid_input)
                
                # Validate PID exists
                import psutil
                if not psutil.pid_exists(pid):
                    print(f"  ❌ Process {pid} not found")
                    continue
                
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                    print(f"  ✓ Found process: {proc_name} (PID {pid})")
                except:
                    print(f"  ❌ Cannot access process {pid}")
                    continue
                
                interval = input("  Check interval in seconds [30]: ").strip()
                interval = int(interval) if interval else 30
                
                name = input(f"  Monitor name [{proc_name}]: ").strip() or proc_name
                
                config_data["monitors"].append({
                    "type": "pid",
                    "name": name,
                    "pid": pid,
                    "check_interval": interval
                })
                print(f"  ✓ PID monitor configured: {name}")
                
                another = input("\n  Add another PID? [y/N]: ").strip().lower()
                if another != 'y':
                    break
            except ValueError:
                print("  ❌ Invalid PID")
    
    # Journal monitor
    print()
    add_journal = input("Monitor systemd service? [y/N]: ").strip().lower()
    if add_journal == 'y':
        # Check if journalctl is available
        import subprocess
        try:
            subprocess.run(["journalctl", "--version"], capture_output=True, check=True)
        except:
            print("  ❌ journalctl not available on this system")
        else:
            while True:
                unit = input("  Service unit (e.g., nginx.service): ").strip()
                if not unit:
                    break
                
                name = input(f"  Monitor name [{unit}]: ").strip() or unit
                
                config_data["monitors"].append({
                    "type": "journal",
                    "name": name,
                    "unit": unit,
                    "since": "now"
                })
                print(f"  ✓ Journal monitor configured: {name}")
                
                another = input("\n  Add another service? [y/N]: ").strip().lower()
                if another != 'y':
                    break
    
    if not config_data["monitors"]:
        print("\n⚠️  No monitors configured! You can add them later in the config file.")
    
    # Step 4: Notification Settings
    print()
    print("[4/5] Notification Settings")
    print("-" * 40)
    
    rate_input = input(f"Max notifications per hour [10]: ").strip()
    if rate_input:
        try:
            config_data["notification"]["rate_limit_per_hour"] = int(rate_input)
        except ValueError:
            pass
    
    print(f"✓ Rate limit: {config_data['notification']['rate_limit_per_hour']}/hour")
    
    # Step 5: Save Configuration
    print()
    print("[5/5] Save Configuration")
    print("-" * 40)
    
    # Display summary
    print("\nConfiguration Summary:")
    print(f"  • Telegram: ✓ Bot configured")
    print(f"  • LLM: ✓ {provider.capitalize()} ({config_data['llm']['model']})")
    print(f"  • Monitors: {len(config_data['monitors'])} configured")
    print(f"  • Rate limit: {config_data['notification']['rate_limit_per_hour']}/hour")
    print()
    
    # Create config directory
    config_dir = Path.home() / ".config" / "bot-monitor"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.yaml"
    
    save = input(f"Save to {config_path}? [Y/n]: ").strip().lower()
    if save == 'n':
        print("Setup cancelled.")
        sys.exit(0)
    
    # Write config file
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✓ Configuration saved to: {config_path}")
    print()
    
    # Offer to start
    print("🚀 Setup complete! What next?")
    print("  1) Start monitoring now")
    print("  2) Exit (start manually later)")
    print()
    
    next_choice = input("Choice [1-2]: ").strip()
    if next_choice == "1":
        print("\nStarting bot-monitor...\n")
        # Load config and start
        args.config = config_path
        cmd_start(args)
    else:
        print("\n✓ All done! Start monitoring with:")
        print(f"   bot-monitor start")
        print()



def cmd_test_notification(args):
    """Send a test notification."""
    try:
        config = Config(args.config)
        telegram_config = config.get_telegram_config()
        
        notifier = TelegramNotifier(
            bot_token=telegram_config["bot_token"],
            chat_id=telegram_config["chat_id"]
        )
        
        if notifier.send_test_message():
            print("✓ Test message sent successfully!")
        else:
            print("✗ Failed to send test message")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_start(args):
    """Start monitoring."""
    try:
        config = Config(args.config)
        manager = MonitorManager(config)
        manager.setup_monitors()
        manager.start()
    
    except ConfigError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Bot Monitor - Universal process monitoring with LLM analysis"
    )
    
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to configuration file"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Interactive setup wizard")
    
    # Start command
    subparsers.add_parser("start", help="Start monitoring")
    
    # Test notification command
    subparsers.add_parser("test-notification", help="Send test notification")
    
    args = parser.parse_args()
    
    # Default to start if no command
    if not args.command:
        args.command = "start"
    
    # Route to command handlers
    if args.command == "setup":
        cmd_setup(args)
    elif args.command == "start":
        cmd_start(args)
    elif args.command == "test-notification":
        cmd_test_notification(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

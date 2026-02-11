"""Main CLI interface for bot-monitor."""

import argparse
import sys
import time
import signal
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
    print("🤖 Bot Monitor Setup Wizard\n")
    
    # Telegram configuration
    print("=== Telegram Configuration ===")
    print("1. Create a bot via @BotFather on Telegram")
    print("2. Save the bot token")
    print("3. Start a chat with your bot")
    print("4. Get your chat ID from @userinfobot\n")
    
    bot_token = input("Enter your Telegram bot token: ").strip()
    chat_id = input("Enter your Telegram chat ID: ").strip()
    
    # LLM configuration
    print("\n=== LLM Provider ===")
    print("Choose provider:")
    print("  1) OpenAI (recommended, paid)")
    print("  2) Anthropic (high quality, paid)")
    print("  3) Groq (fast, free tier)")
    print("  4) Ollama (local, free)")
    
    provider_choice = input("Enter choice [1-4]: ").strip()
    provider_map = {"1": "openai", "2": "anthropic", "3": "groq", "4": "ollama"}
    provider = provider_map.get(provider_choice, "openai")
    
    if provider != "ollama":
        api_key = input(f"Enter {provider} API key: ").strip()
    else:
        api_key = ""
    
    # Create config directory
    config_dir = Path.home() / ".config" / "bot-monitor"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.yaml"
    
    # Generate config file
    create_example_config(config_path)
    print(f"\n✓ Created config template at: {config_path}")
    print("\n⚠️  Please edit the config file to add your monitoring targets!")
    print(f"   nano {config_path}")


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

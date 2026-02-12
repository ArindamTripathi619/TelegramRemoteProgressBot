"""Telegram message listener for two-way communication."""

import time
import logging
from typing import Optional, Callable
from telegram import Bot, Update
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramListener:
    """Listens for user messages on Telegram and triggers callbacks."""
    
    def __init__(self, bot_token: str, chat_id: str):
        """Initialize listener.
        
        Args:
            bot_token: Telegram bot token.
            chat_id: Chat ID to listen to.
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.last_update_id: Optional[int] = None
        self.running = False
        self.on_message_callback: Optional[Callable[[str], None]] = None
        
        logger.info(f"TelegramListener initialized for chat {chat_id}")
    
    def set_message_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback function to call when message is received.
        
        Args:
            callback: Function to call with message text.
        """
        self.on_message_callback = callback
    
    def poll_once(self) -> bool:
        """Poll for new messages once.
        
        Returns:
            True if a message was received.
        """
        import asyncio
        try:
            async def _get_updates():
                return await self.bot.get_updates(
                    offset=self.last_update_id + 1 if self.last_update_id else None,
                    timeout=2,
                    allowed_updates=["message"]
                )

            # Get updates
            updates = asyncio.run(_get_updates())
            
            message_received = False
            
            for update in updates:
                self.last_update_id = update.update_id
                
                # Check if it's a message from our chat
                if update.message and str(update.message.chat.id) == str(self.chat_id):
                    message_text = update.message.text or ""
                    
                    logger.info(f"Received message: {message_text[:50]}...")
                    
                    # Trigger callback
                    if self.on_message_callback:
                        self.on_message_callback(message_text)
                    
                    message_received = True
            
            return message_received
        
        except TelegramError as e:
            logger.error(f"Telegram polling error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in polling: {e}")
            return False
    
    def start_polling(self, interval: float = 2.0) -> None:
        """Start continuous polling (blocking).
        
        Args:
            interval: Seconds between polls.
        """
        self.running = True
        logger.info("Started message polling")
        
        while self.running:
            try:
                self.poll_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Polling stopped by user")
                break
            except Exception as e:
                logger.error(f"Polling loop error: {e}")
                time.sleep(interval)
    
    def stop_polling(self) -> None:
        """Stop polling."""
        self.running = False
        logger.info("Polling stopped")

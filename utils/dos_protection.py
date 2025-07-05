"""
DoS Protection Utilities for Discord Bot
Prevents various types of denial of service attacks
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
import config

# Global rate limit storage
rate_limit_storage: Dict[str, Dict[int, List[float]]] = {}

# Spam detection storage
spam_storage: Dict[int, List[Tuple[float, str]]] = {}

class DoSProtection:
    """Comprehensive DoS protection for Discord bot"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def is_rate_limited(self, user_id: int, rate_limit_type: str) -> bool:
        """
        Check if user is rate limited for a specific action type
        
        Args:
            user_id: Discord user ID
            rate_limit_type: Type of rate limit (e.g., 'city_selection', 'commands', 'role_updates')
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        if rate_limit_type not in config.DOS_PROTECTION:
            self.logger.warning(f"Unknown rate limit type: {rate_limit_type}")
            return False
            
        current_time = time.time()
        
        # Initialize storage for this rate limit type
        if rate_limit_type not in rate_limit_storage:
            rate_limit_storage[rate_limit_type] = {}
            
        user_data = rate_limit_storage[rate_limit_type]
        
        # Clean old timestamps
        if user_id in user_data:
            window_key = f"{rate_limit_type.upper()}_RATE_LIMIT_WINDOW"
            window = config.DOS_PROTECTION.get(window_key, 60)
            user_data[user_id] = [
                ts for ts in user_data[user_id] 
                if current_time - ts < window
            ]
        else:
            user_data[user_id] = []
        
        # Check if user has exceeded limit
        max_key = f"MAX_{rate_limit_type.upper()}_PER_WINDOW"
        max_requests = config.DOS_PROTECTION.get(max_key, 5)
        
        if len(user_data[user_id]) >= max_requests:
            self.logger.warning(f"Rate limited {rate_limit_type} for user {user_id}")
            return True
        
        # Add current request
        user_data[user_id].append(current_time)
        return False
    
    def is_spam_detected(self, user_id: int, message_content: str) -> bool:
        """
        Detect spam based on repeated similar messages
        
        Args:
            user_id: Discord user ID
            message_content: Content of the message
            
        Returns:
            bool: True if spam detected, False otherwise
        """
        current_time = time.time()
        
        # Clean old messages
        if user_id in spam_storage:
            spam_storage[user_id] = [
                (ts, content) for ts, content in spam_storage[user_id]
                if current_time - ts < config.DOS_PROTECTION.get("SPAM_WINDOW", 60)
            ]
        else:
            spam_storage[user_id] = []
        
        # Check for repeated messages
        recent_messages = [content for _, content in spam_storage[user_id]]
        if recent_messages.count(message_content) >= config.DOS_PROTECTION.get("MAX_REPEATED_MESSAGES", 3):
            self.logger.warning(f"Spam detected for user {user_id}: repeated message '{message_content[:50]}...'")
            return True
        
        # Check for rapid message sending
        max_messages = config.DOS_PROTECTION.get("MAX_MESSAGES_PER_MINUTE", 10)
        if len(spam_storage[user_id]) >= max_messages:
            self.logger.warning(f"Spam detected for user {user_id}: too many messages per minute")
            return True
        
        # Add current message
        spam_storage[user_id].append((current_time, message_content))
        return False
    
    def get_rate_limit_message(self, rate_limit_type: str) -> str:
        """Get user-friendly rate limit message"""
        window_key = f"{rate_limit_type.upper()}_RATE_LIMIT_WINDOW"
        max_key = f"MAX_{rate_limit_type.upper()}_PER_WINDOW"
        
        window = config.DOS_PROTECTION.get(window_key, 60)
        max_requests = config.DOS_PROTECTION.get(max_key, 5)
        
        return f"⏰ Please wait before making another request. Rate limit: {max_requests} requests per {window} seconds."
    
    def get_spam_message(self) -> str:
        """Get user-friendly spam detection message"""
        return "🚫 Please slow down your messages to avoid spam detection."
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old rate limit data to prevent memory leaks"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # Clean rate limit storage
        for rate_limit_type, user_data in rate_limit_storage.items():
            for user_id in list(user_data.keys()):
                # Remove users with no recent activity
                if not user_data[user_id]:
                    del user_data[user_id]
                    continue
                
                # Remove old timestamps
                user_data[user_id] = [
                    ts for ts in user_data[user_id] 
                    if current_time - ts < max_age_seconds
                ]
                
                # Remove users with no remaining timestamps
                if not user_data[user_id]:
                    del user_data[user_id]
        
        # Clean spam storage
        for user_id in list(spam_storage.keys()):
            spam_storage[user_id] = [
                (ts, content) for ts, content in spam_storage[user_id]
                if current_time - ts < max_age_seconds
            ]
            
            if not spam_storage[user_id]:
                del spam_storage[user_id]
        
        self.logger.info(f"Cleaned up rate limit data. Active users: {sum(len(data) for data in rate_limit_storage.values())}")
    
    def get_rate_limit_stats(self) -> Dict[str, int]:
        """Get statistics about current rate limiting"""
        stats = {}
        for rate_limit_type, user_data in rate_limit_storage.items():
            stats[rate_limit_type] = len(user_data)
        return stats
    
    def get_spam_stats(self) -> Dict[str, int]:
        """Get statistics about spam detection"""
        return {
            "spam_detected_users": len(spam_storage),
            "total_spam_messages": sum(len(messages) for messages in spam_storage.values())
        }

# Global instance
dos_protection = DoSProtection()

# Convenience functions
def is_city_selection_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited for city selection"""
    return dos_protection.is_rate_limited(user_id, "city_selection")

def is_command_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited for commands"""
    return dos_protection.is_rate_limited(user_id, "commands")

def is_role_update_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited for role updates"""
    return dos_protection.is_rate_limited(user_id, "role_updates")

def is_combo_role_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited for combo role updates"""
    return dos_protection.is_rate_limited(user_id, "combo_role_updates")

def is_spam_detected(user_id: int, message_content: str) -> bool:
    """Check if message is spam"""
    return dos_protection.is_spam_detected(user_id, message_content)

def get_rate_limit_message(rate_limit_type: str) -> str:
    """Get rate limit message for specific type"""
    return dos_protection.get_rate_limit_message(rate_limit_type)

def get_spam_message() -> str:
    """Get spam detection message"""
    return dos_protection.get_spam_message() 
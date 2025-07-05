"""
Main Discord bot entry point
Handles bot initialization, cog loading, and core events
"""

import sys
import discord
from discord.ext import commands
import toml
import asyncio

# Import utilities
from utils.logging_config import setup_logging, get_logger
from utils.dos_protection import is_command_rate_limited, get_rate_limit_message

# Setup logging
setup_logging()
logger = get_logger(__name__)

class SGeBot(commands.Bot):
    """Main bot class with custom functionality"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self):
        """Setup hook called when the bot is starting up"""
        logger.info("Setting up bot...")
        
        # Load cogs
        await self.load_extension("cogs.combo_roles")
        await self.load_extension("cogs.city_pick")
        await self.load_extension("cogs.admin")
        
        logger.info("All cogs loaded successfully")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        if self.user:
            logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
            logger.info(f"Bot is ready! Serving {len(self.guilds)} guild(s)")
        else:
            logger.error("Logged in, but bot.user is None")
    
    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author.bot:
            return

        # DoS protection for message handling
        if is_command_rate_limited(message.author.id):
            logger.warning(f"Rate limited message from {message.author} (ID: {message.author.id})")
            try:
                await message.channel.send(
                    f"⏰ {message.author.mention} {get_rate_limit_message('commands')}",
                    delete_after=10
                )
            except discord.Forbidden:
                logger.warning("Cannot send rate limit message to channel.")
            try:
                await message.delete()
            except discord.Forbidden:
                logger.warning("Cannot delete rate limited message.")
            return

        # Process commands (cogs will handle their own message events)
        await self.process_commands(message)

def load_secrets():
    """Load bot secrets from TOML file"""
    try:
        secrets = toml.load("data/secrets.toml")
        return secrets
    except FileNotFoundError:
        logger.error("Cannot find API key: data/secrets.toml doesn't exist")
        logger.error("Please create data/secrets.toml with your Discord bot token")
        sys.exit(1)
    except toml.TomlDecodeError:
        logger.error("Error parsing data/secrets.toml")
        sys.exit(1)

def main():
    """Main function to run the bot"""
    logger.info("Starting SGe Bot...")
    
    # Load secrets
    secrets = load_secrets()
    
    # Create and run bot
    bot = SGeBot()
    
    try:
        bot.run(secrets["discord"]["token"])
    except discord.LoginFailure:
        logger.error("Invalid bot token. Please check your secrets.toml file.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

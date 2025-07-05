import discord
import datetime
import logging
import config
from typing import Optional
from discord.ext import commands
from utils.dos_protection import is_city_selection_rate_limited, get_rate_limit_message

logger = logging.getLogger(__name__)

class CityPick(commands.Cog):
    """Handles city selection functionality"""
    
    def __init__(self, bot):
        self.bot = bot

    async def assign_city_role(self, member: discord.Member, guild: discord.Guild, role_name: str) -> str:
        """Assign a city role to a member"""
        # Rate limiting check
        if is_city_selection_rate_limited(member.id):
            return get_rate_limit_message("city_selection")
        
        # Remove any existing city role
        city_role_names = set(config.CITY_ROLES.values())
        roles_to_remove = [role for role in member.roles if role.name in city_role_names]
        removed = False
        if roles_to_remove:
            try:
                await member.remove_roles(*roles_to_remove, reason="Replacing city role")
                removed = True
            except discord.Forbidden:
                return "❌ I don't have permission to remove existing city roles."
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            try:
                await member.add_roles(role, reason="Auto city role assignment")
                if removed:
                    return f"{member.mention} has replaced their city role with **{role.name}**!"
                else:
                    return f"{member.mention} has been given the **{role.name}** role!"
            except discord.Forbidden:
                return "❌ I don't have permission to assign roles."
        else:
            return f"❌ Role **{role_name}** not found."

    async def log_unrecognized_city(self, member: discord.Member, city_text: str) -> None:
        """Log unrecognized city submissions"""
        # Rate limiting for logging to prevent spam
        if is_city_selection_rate_limited(member.id):
            logger.warning(f"Rate limited logging attempt from {member} for city: {city_text}")
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {member} (ID: {member.id}): {city_text}"
        
        guild = member.guild if hasattr(member, 'guild') else None
        if guild is None:
            logger.warning("Cannot find guild for member when logging unrecognized city.")
            return

        channel = discord.utils.get(
            guild.text_channels,
            name=config.UNRECOGNIZED_CITY_CHANNEL,
            category__name=config.UNRECOGNIZED_CITY_CATEGORY
        )

        if channel:
            try:
                await channel.send(log_entry)
            except discord.Forbidden:
                logger.warning(f"Cannot send message to channel '{config.UNRECOGNIZED_CITY_CHANNEL}'.")
        else:
            logger.warning(f"Channel '{config.UNRECOGNIZED_CITY_CHANNEL}' in category '{config.UNRECOGNIZED_CITY_CATEGORY}' not found in guild '{guild.name}'.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle city selection messages"""
        if message.author.bot:
            return

        # Only handle messages in city-selection channels
        if "city-selection" not in message.channel.name:
            return

        # Rate limiting check
        if is_city_selection_rate_limited(message.author.id):
            try:
                await message.channel.send(
                    f"⏰ {message.author.mention} {get_rate_limit_message('city_selection')}",
                    delete_after=10
                )
            except discord.Forbidden:
                logger.warning("Cannot send rate limit message to channel.")
            try:
                await message.delete()
            except discord.Forbidden:
                logger.warning("Cannot delete rate limited message.")
            return

        content = message.content.strip().lower()
        member = message.author
        guild = message.guild

        # Ensure member is a discord.Member and guild is not None
        if not isinstance(member, discord.Member) or guild is None:
            logger.warning("Message author is not a Member or guild is None.")
            return

        if content in config.CITY_ROLES:
            result_msg = await self.assign_city_role(member, guild, config.CITY_ROLES[content])
        elif content == "other":
            result_msg = (
                f"{member.mention} 📌 If your city isn't listed, please type:\n"
                f"`other your-city-name`\n"
                "For example: `other Haifa`\n"
                "We'll review your submission and add your city if possible!"
            )
        elif content.startswith("other "):
            await self.log_unrecognized_city(member, message.content.strip())
            result_msg = (
                f"{member.mention} 📌 Thank you! We've received your city submission.\n"
                "Our team will review it soon. If you have questions, please contact a moderator."
            )
        else:
            result_msg = (
                f"{member.mention} ❌ Sorry, I didn't recognize that city.\n"
                "Please type the name of your city (e.g. `netanya`, `modiin`, `rehovot`),\n"
                "or if your city isn't listed, type: `other your-city-name`."
            )

        try:
            await message.channel.send(result_msg, delete_after=60)
        except discord.Forbidden:
            logger.warning("Cannot send message to channel.")
        try:
            await message.delete()
        except discord.Forbidden:
            logger.warning("Cannot delete user message.")

async def setup(bot):
    """Setup function for the city pick cog"""
    await bot.add_cog(CityPick(bot))

# Export the handle_city_selection function for backward compatibility
async def handle_city_selection(message: discord.Message) -> None:
    """Handle city selection - exported for backward compatibility"""
    # This function is now handled by the cog's on_message listener
    # It's kept for backward compatibility but doesn't need to do anything
    pass
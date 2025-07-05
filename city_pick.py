import discord
import datetime
import logging
import config
from typing import Optional, Dict
import asyncio
import time

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Rate limiting for DoS protection
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 5  # max requests per user per minute
rate_limit_data: Dict[int, list] = {}  # user_id -> list of timestamps

def is_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited"""
    current_time = time.time()
    
    # Clean old timestamps
    if user_id in rate_limit_data:
        rate_limit_data[user_id] = [
            ts for ts in rate_limit_data[user_id] 
            if current_time - ts < RATE_LIMIT_WINDOW
        ]
    else:
        rate_limit_data[user_id] = []
    
    # Check if user has exceeded limit
    if len(rate_limit_data[user_id]) >= MAX_REQUESTS_PER_WINDOW:
        return True
    
    # Add current request
    rate_limit_data[user_id].append(current_time)
    return False

# --------- City Role Helpers --------- #

async def assign_city_role(member: discord.Member, guild: discord.Guild, role_name: str) -> str:
    # Rate limiting check
    if is_rate_limited(member.id):
        return f"⏰ {member.mention} Please wait before making another request. Rate limit: {MAX_REQUESTS_PER_WINDOW} requests per {RATE_LIMIT_WINDOW} seconds."
    
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

async def log_unrecognized_city(member: discord.Member, city_text: str) -> None:
    # Rate limiting for logging to prevent spam
    if is_rate_limited(member.id):
        logging.warning(f"Rate limited logging attempt from {member} for city: {city_text}")
        return
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {member} (ID: {member.id}): {city_text}"
    
    guild = member.guild if hasattr(member, 'guild') else None
    if guild is None:
        logging.warning("Cannot find guild for member when logging unrecognized city.")
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
            logging.warning(f"Cannot send message to channel '{config.UNRECOGNIZED_CITY_CHANNEL}'.")
    else:
        logging.warning(f"Channel '{config.UNRECOGNIZED_CITY_CHANNEL}' in category '{config.UNRECOGNIZED_CITY_CATEGORY}' not found in guild '{guild.name}'.")


async def handle_city_selection(message: discord.Message) -> None:
    # Rate limiting check
    if is_rate_limited(message.author.id):
        try:
            await message.channel.send(
                f"⏰ {message.author.mention} Please wait before making another request. Rate limit: {MAX_REQUESTS_PER_WINDOW} requests per {RATE_LIMIT_WINDOW} seconds.",
                delete_after=10
            )
        except discord.Forbidden:
            logging.warning("Cannot send rate limit message to channel.")
        try:
            await message.delete()
        except discord.Forbidden:
            logging.warning("Cannot delete rate limited message.")
        return

    content = message.content.strip().lower()
    member = message.author
    guild = message.guild

    # Ensure member is a discord.Member and guild is not None
    if not isinstance(member, discord.Member) or guild is None:
        logging.warning("Message author is not a Member or guild is None.")
        return

    if content in config.CITY_ROLES:
        result_msg = await assign_city_role(member, guild, config.CITY_ROLES[content])
    elif content == "other":
        result_msg = (
            f"{member.mention} 📌 If your city isn't listed, please type:\n"
            f"`other your-city-name`\n"
            "For example: `other Haifa`\n"
            "We'll review your submission and add your city if possible!"
        )
    elif content.startswith("other "):
        await log_unrecognized_city(member, message.content.strip())
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
        logging.warning("Cannot send message to channel.")
    try:
        await message.delete()
    except discord.Forbidden:
        logging.warning("Cannot delete user message.")
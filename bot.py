# bot.py
import sys
import discord
import datetime
from discord.ext import commands
import toml
import logging
import config
import time
from typing import Dict, List

from combo_roles import update_combo_role, is_only_combo_role_change
from city_pick import handle_city_selection

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# DoS Protection - Rate limiting
COMMAND_RATE_LIMIT_WINDOW = 30  # seconds
MAX_COMMANDS_PER_WINDOW = 3  # max commands per user per 30 seconds
command_rate_limit_data: Dict[int, list] = {}  # user_id -> list of timestamps

ROLE_UPDATE_RATE_LIMIT_WINDOW = 10  # seconds
MAX_ROLE_UPDATES_PER_WINDOW = 2  # max role updates per user per 10 seconds
role_update_rate_limit_data: Dict[int, list] = {}  # user_id -> list of timestamps

def is_command_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited for commands"""
    current_time = time.time()
    
    # Clean old timestamps
    if user_id in command_rate_limit_data:
        command_rate_limit_data[user_id] = [
            ts for ts in command_rate_limit_data[user_id] 
            if current_time - ts < COMMAND_RATE_LIMIT_WINDOW
        ]
    else:
        command_rate_limit_data[user_id] = []
    
    # Check if user has exceeded limit
    if len(command_rate_limit_data[user_id]) >= MAX_COMMANDS_PER_WINDOW:
        return True
    
    # Add current request
    command_rate_limit_data[user_id].append(current_time)
    return False

def is_role_update_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited for role updates"""
    current_time = time.time()
    
    # Clean old timestamps
    if user_id in role_update_rate_limit_data:
        role_update_rate_limit_data[user_id] = [
            ts for ts in role_update_rate_limit_data[user_id] 
            if current_time - ts < ROLE_UPDATE_RATE_LIMIT_WINDOW
        ]
    else:
        role_update_rate_limit_data[user_id] = []
    
    # Check if user has exceeded limit
    if len(role_update_rate_limit_data[user_id]) >= MAX_ROLE_UPDATES_PER_WINDOW:
        return True
    
    # Add current request
    role_update_rate_limit_data[user_id].append(current_time)
    return False

# Load token
try:
    secrets = toml.load("secrets.toml")
except FileNotFoundError:
    logging.error("Cannot find API key: secrets.toml doesn't exist")
    sys.exit()
except toml.TomlDecodeError:
    logging.error("Error parsing secrets.toml")
    sys.exit()

# Bot config
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# TARGET_CHANNEL = "city-selection-israel"

# --------- Bot Events --------- #

@bot.event
async def on_ready():
    if bot.user:
        logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    else:
        logging.info("Logged in, but bot.user is None")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # DoS protection for message handling
    if is_command_rate_limited(message.author.id):
        logging.warning(f"Rate limited message from {message.author} (ID: {message.author.id})")
        try:
            await message.channel.send(
                f"⏰ {message.author.mention} Please wait before sending another command. Rate limit: {MAX_COMMANDS_PER_WINDOW} commands per {COMMAND_RATE_LIMIT_WINDOW} seconds.",
                delete_after=10
            )
        except discord.Forbidden:
            logging.warning("Cannot send rate limit message to channel.")
        try:
            await message.delete()
        except discord.Forbidden:
            logging.warning("Cannot delete rate limited message.")
        return

    if "city-selection" in message.channel.name:
        await handle_city_selection(message)
    else:
        await bot.process_commands(message)  # Let other commands work

@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return
    if is_only_combo_role_change(before.roles, after.roles):
        return

    # DoS protection for role updates
    if is_role_update_rate_limited(after.id):
        logging.warning(f"Rate limited role update for {after} (ID: {after.id})")
        return

    # --- Remove city roles if a country role is added ---
    
    city_role_names = set(config.CITY_ROLES.values())
    before_role_names = set(role.name for role in before.roles)
    after_role_names = set(role.name for role in after.roles)
    # Check if a country role was added
    added_roles = after_role_names - before_role_names
    if any(role in config.COUNTRY_ROLES for role in added_roles):
        roles_to_remove = [role for role in after.roles if role.name in city_role_names]
        if roles_to_remove:
            try:
                await after.remove_roles(*roles_to_remove, reason="Country role changed, removing city role")
                logging.info(f"Removed city roles from {after.display_name} due to country role change.")
            except Exception as e:
                logging.warning(f"Failed to remove city roles: {e}")

    await update_combo_role(after)

# --------- Admin Commands --------- #

@bot.command()
@commands.has_permissions(administrator=True)
async def reset_combo_roles(ctx):
    # DoS protection for admin commands
    if is_command_rate_limited(ctx.author.id):
        await ctx.send(f"⏰ Please wait before using another admin command. Rate limit: {MAX_COMMANDS_PER_WINDOW} commands per {COMMAND_RATE_LIMIT_WINDOW} seconds.")
        return
        
    await ctx.send("Resetting combo roles for all members...")
    for member in ctx.guild.members:
        await update_combo_role(member)
    await ctx.send("✅ Combo roles have been reset.")

@bot.command(name='listroles')
@commands.has_permissions(administrator=True)
async def get_roles(ctx):
    # DoS protection for admin commands
    if is_command_rate_limited(ctx.author.id):
        await ctx.send(f"⏰ Please wait before using another admin command. Rate limit: {MAX_COMMANDS_PER_WINDOW} commands per {COMMAND_RATE_LIMIT_WINDOW} seconds.")
        return
        
    role_names = [role.name for role in ctx.guild.roles][1:]  # Skip @everyone
    await ctx.send("Roles in this server:\n" + "\n".join(role_names))

@bot.command(name='sge_help')
@commands.has_permissions(administrator=True)
async def sge_help(ctx):
    # DoS protection for admin commands
    if is_command_rate_limited(ctx.author.id):
        await ctx.send(f"⏰ Please wait before using another admin command. Rate limit: {MAX_COMMANDS_PER_WINDOW} commands per {COMMAND_RATE_LIMIT_WINDOW} seconds.")
        return
        
    await ctx.send("commands (admin only):\n !reset_combo_roles \n !listroles \n !getchannels \n !sge_help")

@sge_help.error
@reset_combo_roles.error
@get_roles.error
async def perms_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need to be an admin to use this command.")

@bot.command(name='getchannels')
@commands.has_permissions(administrator=True)
async def get_channels(ctx):
    # DoS protection for admin commands
    if is_command_rate_limited(ctx.author.id):
        await ctx.send(f"⏰ Please wait before using another admin command. Rate limit: {MAX_COMMANDS_PER_WINDOW} commands per {COMMAND_RATE_LIMIT_WINDOW} seconds.")
        return
        
    channels = ctx.guild.channels
    channel_list = []
    for channel in channels:
        if isinstance(channel, discord.TextChannel):
            channel_list.append(f"{channel.name} (Text)")
        elif isinstance(channel, discord.VoiceChannel):
            channel_list.append(f"{channel.name} (Voice)")
        elif isinstance(channel, discord.CategoryChannel):
            channel_list.append(f"{channel.name} (Category)")
        else:
            channel_list.append(f"{channel.name} ({type(channel).__name__})")
    await ctx.send("Channels in this server:\n" + "\n".join(channel_list))

# --------- Run Bot --------- #

bot.run(secrets["discord"]["token"])

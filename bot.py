# bot.py
import sys
import discord
import datetime
from discord.ext import commands
import toml
import logging
import config

from combo_roles import update_combo_role, is_only_combo_role_change
from city_pick import handle_city_selection

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

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
    await ctx.send("Resetting combo roles for all members...")
    for member in ctx.guild.members:
        await update_combo_role(member)
    await ctx.send("✅ Combo roles have been reset.")

@bot.command(name='listroles')
@commands.has_permissions(administrator=True)
async def get_roles(ctx):
    role_names = [role.name for role in ctx.guild.roles][1:]  # Skip @everyone
    await ctx.send("Roles in this server:\n" + "\n".join(role_names))

@bot.command(name='sge_help')
@commands.has_permissions(administrator=True)
async def sge_help(ctx):
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

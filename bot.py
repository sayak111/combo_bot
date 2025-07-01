# bot.py
import sys
import discord
import datetime
from discord.ext import commands
import toml

from combo_roles import update_combo_role, is_only_combo_role_change
from city_pick import handle_city_selection

# Load token
try:
    secrets = toml.load("secrets.toml")
except:
    print("❌ Cannot find API key: secrets.toml doesn't exist")
    sys.exit()

# Bot config
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)



TARGET_CHANNEL = "city-selection-israel"

# --------- Bot Events --------- #

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.name == TARGET_CHANNEL:
        await handle_city_selection(message)
    else:
        await bot.process_commands(message)  # Let other commands work

@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return
    if is_only_combo_role_change(before.roles, after.roles):
        return
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

@reset_combo_roles.error
@get_roles.error
async def perms_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need to be an admin to use this command.")

# --------- Run Bot --------- #

bot.run(secrets["discord"]["token"])

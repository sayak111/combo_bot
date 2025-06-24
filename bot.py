import sys
import discord
from discord.ext import commands
import toml

from combo_roles import update_combo_role, is_only_combo_role_change

try:
    secrets = toml.load("secrets.toml")
except:
    print("cannot find api key becouse secrets.toml doesnt exist")
    sys.exit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")


@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return

    if is_only_combo_role_change(before.roles, after.roles):
        return

    await update_combo_role(after)


@bot.command()
@commands.has_permissions(administrator=True)
async def reset_combo_roles(ctx):
    await ctx.send("Resetting combo roles for all members...")
    for member in ctx.guild.members:
        await update_combo_role(member)
    await ctx.send("✅ Combo roles have been reset.")


@reset_combo_roles.error
async def reset_combo_roles_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need to be an admin to use this command.")


bot.run(secrets["discord"]["token"])

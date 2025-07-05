import discord
from discord.ext import commands
import logging
from utils.dos_protection import is_command_rate_limited, get_rate_limit_message

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    """Admin commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_combo_roles(self, ctx):
        """Reset combo roles for all members"""
        # DoS protection for admin commands
        if is_command_rate_limited(ctx.author.id):
            await ctx.send(get_rate_limit_message("commands"))
            return
            
        await ctx.send("Resetting combo roles for all members...")
        
        from cogs.combo_roles import update_combo_role
        for member in ctx.guild.members:
            await update_combo_role(member)
            
        await ctx.send("✅ Combo roles have been reset.")

    @commands.command(name='listroles')
    @commands.has_permissions(administrator=True)
    async def get_roles(self, ctx):
        """List all roles in the server"""
        # DoS protection for admin commands
        if is_command_rate_limited(ctx.author.id):
            await ctx.send(get_rate_limit_message("commands"))
            return
            
        role_names = [role.name for role in ctx.guild.roles][1:]  # Skip @everyone
        await ctx.send("Roles in this server:\n" + "\n".join(role_names))

    @commands.command(name='sge_help')
    @commands.has_permissions(administrator=True)
    async def sge_help(self, ctx):
        """Show admin command help"""
        # DoS protection for admin commands
        if is_command_rate_limited(ctx.author.id):
            await ctx.send(get_rate_limit_message("commands"))
            return
            
        await ctx.send("commands (admin only):\n !reset_combo_roles \n !listroles \n !getchannels \n !sge_help")

    @commands.command(name='getchannels')
    @commands.has_permissions(administrator=True)
    async def get_channels(self, ctx):
        """List all channels in the server"""
        # DoS protection for admin commands
        if is_command_rate_limited(ctx.author.id):
            await ctx.send(get_rate_limit_message("commands"))
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

    @sge_help.error
    @reset_combo_roles.error
    @get_roles.error
    @get_channels.error
    async def perms_error(self, ctx, error):
        """Handle permission errors for admin commands"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need to be an admin to use this command.")

async def setup(bot):
    """Setup function for the admin cog"""
    await bot.add_cog(Admin(bot)) 
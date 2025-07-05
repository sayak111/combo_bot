import discord
import logging
import config
from discord.ext import commands
from utils.dos_protection import dos_protection

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    """Admin commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dosstats")
    @commands.has_permissions(administrator=True)
    async def dos_stats(self, ctx):
        """Show DoS protection statistics (Admin only)"""
        try:
            rate_limit_stats = dos_protection.get_rate_limit_stats()
            spam_stats = dos_protection.get_spam_stats()
            
            embed = discord.Embed(
                title="🛡️ DoS Protection Statistics",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # Rate limit stats
            rate_limit_text = ""
            for rate_type, user_count in rate_limit_stats.items():
                rate_limit_text += f"• **{rate_type}**: {user_count} users\n"
            
            if rate_limit_text:
                embed.add_field(
                    name="Rate Limited Users",
                    value=rate_limit_text or "None",
                    inline=False
                )
            
            # Spam stats
            spam_text = f"• **Spam Detected Users**: {spam_stats.get('spam_detected_users', 0)}\n"
            spam_text += f"• **Total Spam Messages**: {spam_stats.get('total_spam_messages', 0)}"
            
            embed.add_field(
                name="Spam Detection",
                value=spam_text,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting DoS stats: {e}")
            await ctx.send("❌ Error retrieving DoS protection statistics.")

    @commands.command(name="cleanup")
    @commands.has_permissions(administrator=True)
    async def cleanup_dos_data(self, ctx):
        """Clean up old DoS protection data (Admin only)"""
        try:
            dos_protection.cleanup_old_data()
            await ctx.send("✅ DoS protection data cleaned up successfully.")
        except Exception as e:
            logger.error(f"Error cleaning up DoS data: {e}")
            await ctx.send("❌ Error cleaning up DoS protection data.")

    @commands.command(name="dosconfig")
    @commands.has_permissions(administrator=True)
    async def dos_config(self, ctx):
        """Show current DoS protection configuration (Admin only)"""
        try:
            embed = discord.Embed(
                title="⚙️ DoS Protection Configuration",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            config_text = ""
            for key, value in config.DOS_PROTECTION.items():
                if isinstance(value, dict):
                    config_text += f"• **{key}**:\n"
                    for sub_key, sub_value in value.items():
                        config_text += f"  - {sub_key}: {sub_value}\n"
                else:
                    config_text += f"• **{key}**: {value}\n"
            
            embed.add_field(
                name="Current Settings",
                value=config_text,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting DoS config: {e}")
            await ctx.send("❌ Error retrieving DoS protection configuration.")

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")

    @commands.command(name="status")
    @commands.has_permissions(administrator=True)
    async def show_status(self, ctx):
        """Show bot status information (Admin only)"""
        try:
            embed = discord.Embed(
                title="🤖 Bot Status",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            # Basic stats
            embed.add_field(
                name="Guilds",
                value=f"📊 {len(self.bot.guilds)} servers",
                inline=True
            )
            
            embed.add_field(
                name="Users",
                value=f"👥 {len(self.bot.users)} users",
                inline=True
            )
            
            embed.add_field(
                name="Latency",
                value=f"🏓 {round(self.bot.latency * 1000)}ms",
                inline=True
            )
            
            # Cog status
            cog_status = ""
            for cog_name in ["combo_roles", "city_pick", "admin"]:
                cog = self.bot.get_cog(cog_name.title().replace("_", ""))
                status = "✅" if cog else "❌"
                cog_status += f"{status} {cog_name}\n"
            
            embed.add_field(
                name="Cog Status",
                value=cog_status,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            await ctx.send("❌ Error retrieving bot status.")

async def setup(bot):
    """Setup function for the admin cog"""
    await bot.add_cog(Admin(bot)) 
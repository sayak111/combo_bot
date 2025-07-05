import discord
import logging
import config
from typing import List, Optional
from discord.ext import commands
from utils.dos_protection import is_combo_role_rate_limited

logger = logging.getLogger(__name__)

# Global reference to the cog instance
_combo_roles_cog = None

class ComboRoles(commands.Cog):
    """Handles combo role logic for users with both leader and location roles"""
    
    def __init__(self, bot):
        self.bot = bot
        # Define combo role names
        self.combo_role_names = [f"{loc} Leader" for loc in config.LOCATIONS]
        # Set global reference
        global _combo_roles_cog
        _combo_roles_cog = self

    def get_combo_role_name(self, user_roles: list[str]) -> Optional[str]:
        """Get the combo role name if user has both leader and location roles"""
        leader = next((r for r in user_roles if r in config.LEADER_ROLES), None)
        location = next((r for r in user_roles if r in config.LOCATIONS), None)
        if leader and location:
            return f"{location} Leader"
        return None

    async def update_combo_role(self, member: discord.Member) -> None:
        """Update combo role for a member based on their current roles"""
        # DoS protection for combo role updates
        if is_combo_role_rate_limited(member.id):
            logger.warning(f"Rate limited combo role update for {member} (ID: {member.id})")
            return
            
        user_roles = [role.name for role in member.roles]
        guild = member.guild

        # Remove all existing combo roles
        to_remove = [role for role in member.roles if role.name in self.combo_role_names]
        if to_remove:
            try:
                await member.remove_roles(*to_remove)
            except discord.Forbidden:
                logger.warning(f"Cannot remove combo roles from {member.display_name}")
                return
            except Exception as e:
                logger.warning(f"Error removing combo roles from {member.display_name}: {e}")
                return

        combo_role_name = self.get_combo_role_name(user_roles)
        if combo_role_name:
            combo_role = discord.utils.get(guild.roles, name=combo_role_name)
            if combo_role and combo_role not in member.roles:
                try:
                    await member.add_roles(combo_role)
                    logger.info(f"Added combo role '{combo_role_name}' to {member.display_name}")
                except discord.Forbidden:
                    logger.warning(f"Cannot add combo role '{combo_role_name}' to {member.display_name}")
                except Exception as e:
                    logger.warning(f"Error adding combo role '{combo_role_name}' to {member.display_name}: {e}")

    def is_only_combo_role_change(self, before_roles: List[discord.Role], after_roles: List[discord.Role]) -> bool:
        """Check if the only role change was a combo role"""
        before_names = set(role.name for role in before_roles)
        after_names = set(role.name for role in after_roles)
        changed = before_names.symmetric_difference(after_names)
        return len(changed) > 0 and all(role in self.combo_role_names for role in changed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Handle member role updates"""
        if before.roles == after.roles:
            return
        if self.is_only_combo_role_change(before.roles, after.roles):
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
                    logger.info(f"Removed city roles from {after.display_name} due to country role change.")
                except Exception as e:
                    logger.warning(f"Failed to remove city roles: {e}")

        await self.update_combo_role(after)

async def setup(bot):
    """Setup function for the combo roles cog"""
    await bot.add_cog(ComboRoles(bot))

# Export the update_combo_role function for use in other cogs
async def update_combo_role(member: discord.Member) -> None:
    """Update combo role for a member - exported for use in other cogs"""
    global _combo_roles_cog
    if _combo_roles_cog:
        await _combo_roles_cog.update_combo_role(member)
    else:
        logger.warning("ComboRoles cog not found")

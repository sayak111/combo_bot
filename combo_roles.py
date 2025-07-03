import discord
import logging
import config
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Define roles
combo_role_names = [f"{loc} Leader" for loc in config.LOCATIONS]


def get_combo_role_name(user_roles: list[str]) -> Optional[str]:
    leader = next((r for r in user_roles if r in config.LEADER_ROLES), None)
    location = next((r for r in user_roles if r in config.LOCATIONS), None)
    if leader and location:
        return f"{location} Leader"
    return None


async def update_combo_role(member: discord.Member) -> None:
    user_roles = [role.name for role in member.roles]
    guild = member.guild

    # Remove all existing combo roles
    to_remove = [role for role in member.roles if role.name in combo_role_names]
    if to_remove:
        await member.remove_roles(*to_remove)

    combo_role_name = get_combo_role_name(user_roles)
    if combo_role_name:
        combo_role = discord.utils.get(guild.roles, name=combo_role_name)
        if combo_role and combo_role not in member.roles:
            await member.add_roles(combo_role)
            logging.info(f"Added combo role '{combo_role_name}' to {member.display_name}")


def is_only_combo_role_change(before_roles: List[discord.Role], after_roles: List[discord.Role]) -> bool:
    before_names = set(role.name for role in before_roles)
    after_names = set(role.name for role in after_roles)
    changed = before_names.symmetric_difference(after_names)
    return len(changed) > 0 and all(role in combo_role_names for role in changed)

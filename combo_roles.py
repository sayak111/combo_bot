import discord
import logging
import config
from typing import List, Optional, Dict
import time

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# DoS Protection for combo role updates
COMBO_ROLE_RATE_LIMIT_WINDOW = 30  # seconds
MAX_COMBO_ROLE_UPDATES_PER_WINDOW = 3  # max updates per user per 30 seconds
combo_role_rate_limit_data: Dict[int, list] = {}  # user_id -> list of timestamps

def is_combo_role_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited for combo role updates"""
    current_time = time.time()
    
    # Clean old timestamps
    if user_id in combo_role_rate_limit_data:
        combo_role_rate_limit_data[user_id] = [
            ts for ts in combo_role_rate_limit_data[user_id] 
            if current_time - ts < COMBO_ROLE_RATE_LIMIT_WINDOW
        ]
    else:
        combo_role_rate_limit_data[user_id] = []
    
    # Check if user has exceeded limit
    if len(combo_role_rate_limit_data[user_id]) >= MAX_COMBO_ROLE_UPDATES_PER_WINDOW:
        return True
    
    # Add current request
    combo_role_rate_limit_data[user_id].append(current_time)
    return False

# Define roles
combo_role_names = [f"{loc} Leader" for loc in config.LOCATIONS]


def get_combo_role_name(user_roles: list[str]) -> Optional[str]:
    leader = next((r for r in user_roles if r in config.LEADER_ROLES), None)
    location = next((r for r in user_roles if r in config.LOCATIONS), None)
    if leader and location:
        return f"{location} Leader"
    return None


async def update_combo_role(member: discord.Member) -> None:
    # DoS protection for combo role updates
    if is_combo_role_rate_limited(member.id):
        logging.warning(f"Rate limited combo role update for {member} (ID: {member.id})")
        return
        
    user_roles = [role.name for role in member.roles]
    guild = member.guild

    # Remove all existing combo roles
    to_remove = [role for role in member.roles if role.name in combo_role_names]
    if to_remove:
        try:
            await member.remove_roles(*to_remove)
        except discord.Forbidden:
            logging.warning(f"Cannot remove combo roles from {member.display_name}")
            return
        except Exception as e:
            logging.warning(f"Error removing combo roles from {member.display_name}: {e}")
            return

    combo_role_name = get_combo_role_name(user_roles)
    if combo_role_name:
        combo_role = discord.utils.get(guild.roles, name=combo_role_name)
        if combo_role and combo_role not in member.roles:
            try:
                await member.add_roles(combo_role)
                logging.info(f"Added combo role '{combo_role_name}' to {member.display_name}")
            except discord.Forbidden:
                logging.warning(f"Cannot add combo role '{combo_role_name}' to {member.display_name}")
            except Exception as e:
                logging.warning(f"Error adding combo role '{combo_role_name}' to {member.display_name}: {e}")


def is_only_combo_role_change(before_roles: List[discord.Role], after_roles: List[discord.Role]) -> bool:
    before_names = set(role.name for role in before_roles)
    after_names = set(role.name for role in after_roles)
    changed = before_names.symmetric_difference(after_names)
    return len(changed) > 0 and all(role in combo_role_names for role in changed)

import discord

# Define roles
leader_roles = {
    "Director",
    "Co-Director",
    "Ambassador",
    "Operations/Media Volunteer"
}

locations = {
    "Netanya",
    "Modi'in",
    "Rehovot"
}

combo_role_names = [f"{loc} Leader" for loc in locations]


def get_combo_role_name(user_roles: list[str]) -> str | None:
    leader = next((r for r in user_roles if r in leader_roles), None)
    location = next((r for r in user_roles if r in locations), None)
    if leader and location:
        return f"{location} Leader"
    return None


async def update_combo_role(member: discord.Member):
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
            print(f"Added combo role '{combo_role_name}' to {member.display_name}")


def is_only_combo_role_change(before_roles, after_roles):
    before_names = set(role.name for role in before_roles)
    after_names = set(role.name for role in after_roles)
    changed = before_names.symmetric_difference(after_names)
    return len(changed) > 0 and all(role in combo_role_names for role in changed)

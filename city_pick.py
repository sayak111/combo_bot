import discord
import datetime

LOG_FILE = "unrecognized_cities.txt"

# City role logic
city_roles = {
    "netanya": "IL Netanya",
    "modiin": "IL Modi'in",
    "rehovot": "IL Rehovot",
    # Add more here
}


# --------- City Role Helpers --------- #

async def assign_city_role(member, guild, role_name):
    role = discord.utils.get(guild.roles, name=role_name)
    if role:
        try:
            await member.add_roles(role, reason="Auto city role assignment")
            return f"{member.mention} has been given the **{role.name}** role!"
        except discord.Forbidden:
            return "❌ I don't have permission to assign roles."
    else:
        return f"❌ Role **{role_name}** not found."

async def log_unrecognized_city(member, city_text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {member} (ID: {member.id}): {city_text}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"⚠️ Failed to write to log: {e}")

async def handle_city_selection(message):
    content = message.content.strip().lower()
    member = message.author
    guild = message.guild

    if content in city_roles:
        result_msg = await assign_city_role(member, guild, city_roles[content])
    elif content == "other":
        result_msg = f"{member.mention} 📌 Got it! If your city isn't listed, type: `other your-city-name`"
    elif content.startswith("other "):
        await log_unrecognized_city(member, message.content.strip())
        result_msg = f"{member.mention} 📌 Got it! We'll review your city submission."
    else:
        result_msg = f"{member.mention} ❌ Unknown city. Please try again or type `other your-city-name`."

    try:
        await message.channel.send(result_msg, delete_after=5)
    except discord.Forbidden:
        print("⚠️ Cannot send message to channel.")
    try:
        await message.delete()
    except discord.Forbidden:
        print("⚠️ Cannot delete user message.")
import discord
from discord.ext import commands
from discord import app_commands
import os
import json

# --- CONFIGURATION ---
ADMIN_IDS = [1171135456306536450, 924641550133248000]
CONFIG_FILE = "server_config.json"
# ---------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Essential for member events
bot = commands.Bot(command_prefix='!', intents=intents)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_server_config(guild_id):
    config = load_config()
    str_id = str(guild_id)
    if str_id not in config:
        config[str_id] = {
            "welcome_channel": None,
            "welcome_title": "Welcome to {server}!",
            "welcome_message": "Hey {user}, welcome to the server!",
            "welcome_gif": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWV4ZjQyZWN0ZWp0djdvZG8ydWphNW1kMW50aGlnbXp6OXNoaHhiayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPnAiaMCws8nOsE/giphy.gif",
            "goodbye_channel": None,
            "goodbye_title": "Goodbye from {server}",
            "goodbye_message": "{user} has left the server.",
            "goodbye_gif": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWV4ZjQyZWN0ZWp0djdvZG8ydWphNW1kMW50aGlnbXp6OXNoaHhiayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPnAiaMCws8nOsE/giphy.gif"
        }
        save_config(config)
    return config[str_id]

def update_server_config(guild_id, key, value):
    config = load_config()
    str_id = str(guild_id)
    if str_id not in config:
        get_server_config(guild_id)
        config = load_config()
    config[str_id][key] = value
    save_config(config)

# --- WELCOME EVENT WITH DEBUG ---
@bot.event
async def on_member_join(member):
    print(f"DEBUG JOIN: {member.name} joined server {member.guild.name}!")
    try:
        conf = get_server_config(member.guild.id)
        channel_id = conf.get("welcome_channel")
        print(f"DEBUG JOIN: Configured channel -> {channel_id}")
        
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            print(f"DEBUG JOIN: Found channel -> {channel}")
            
            if channel:
                title = conf["welcome_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
                desc = conf["welcome_message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
                
                embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
                if conf.get("welcome_gif"):
                    embed.set_image(url=conf["welcome_gif"])
                
                await channel.send(embed=embed)
                print("DEBUG JOIN: Welcome message sent successfully!")
    except Exception as e:
        print(f"ERROR in on_member_join: {e}")

# --- GOODBYE EVENT WITH DEBUG ---
@bot.event
async def on_member_remove(member):
    print(f"DEBUG REMOVE: {member.name} left or was kicked from {member.guild.name}!")
    try:
        conf = get_server_config(member.guild.id)
        channel_id = conf.get("goodbye_channel")
        print(f"DEBUG REMOVE: Configured goodbye channel -> {channel_id}")
        
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            print(f"DEBUG REMOVE: Found channel -> {channel}")
            
            if channel:
                title = conf["goodbye_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
                desc = conf["goodbye_message"].replace("{user}", member.name).replace("{server}", member.guild.name)
                
                embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
                if conf.get("goodbye_gif"):
                    embed.set_image(url=conf["goodbye_gif"])
                
                await channel.send(embed=embed)
                print("DEBUG REMOVE: Goodbye message sent successfully!")
    except Exception as e:
        print(f"ERROR in on_member_remove: {e}")

# --- SLASH COMMANDS ---
@bot.tree.command(name="set_welcome_channel", description="Set the welcome channel")
async def set_welcome_channel(interaction: discord.Interaction, channel: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    clean_id = channel.replace("<#", "").replace(">", "")
    if not clean_id.isdigit():
        return await interaction.response.send_message("Please tag a valid channel!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_channel", int(clean_id))
    await interaction.response.send_message("✅ Welcome channel successfully set!", ephemeral=True)

@bot.tree.command(name="set_goodbye_channel", description="Set the goodbye channel")
async def set_goodbye_channel(interaction: discord.Interaction, channel: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    clean_id = channel.replace("<#", "").replace(">", "")
    if not clean_id.isdigit():
        return await interaction.response.send_message("Please tag a valid channel!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_channel", int(clean_id))
    await interaction.response.send_message("✅ Goodbye channel successfully set!", ephemeral=True)

@bot.tree.command(name="set_welcome_gif", description="Set the welcome GIF")
async def set_welcome_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_gif", url)
    await interaction.response.send_message("✅ Welcome GIF updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_gif", description="Set the goodbye GIF")
async def set_goodbye_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_gif", url)
    await interaction.response.send_message("✅ Goodbye GIF updated!", ephemeral=True)

@bot.tree.command(name="test", description="Test welcome or goodbye messages")
@app_commands.choices(tipo=[app_commands.Choice(name="welcome", value="welcome"), app_commands.Choice(name="goodbye", value="goodbye")])
async def test_command(interaction: discord.Interaction, tipo: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    conf = get_server_config(interaction.guild.id)
    
    if tipo == "welcome":
        ch_id = conf.get("welcome_channel")
        if not ch_id:
            return await interaction.followup.send("Set welcome channel first!", ephemeral=True)
        ch = interaction.guild.get_channel(int(ch_id))
        if not ch:
            return await interaction.followup.send("Channel not found!", ephemeral=True)
        
        embed = discord.Embed(title=conf["welcome_title"].replace("{user}", interaction.user.name), description=conf["welcome_message"].replace("{user}", interaction.user.mention), color=discord.Color.green())
        if conf.get("welcome_gif"): embed.set_image(url=conf["welcome_gif"])
        await ch.send(embed=embed)
        await interaction.followup.send("✅ Welcome test sent!", ephemeral=True)
        
    elif tipo == "goodbye":
        ch_id = conf.get("goodbye_channel")
        if not ch_id:
            return await interaction.followup.send("Set goodbye channel first!", ephemeral=True)
        ch = interaction.guild.get_channel(int(ch_id))
        if not ch:
            return await interaction.followup.send("Channel not found!", ephemeral=True)
        
        embed = discord.Embed(title=conf["goodbye_title"].replace("{user}", interaction.user.name), description=conf["goodbye_message"].replace("{user}", interaction.user.name), color=discord.Color.red())
        if conf.get("goodbye_gif"): embed.set_image(url=conf["goodbye_gif"])
        await ch.send(embed=embed)
        await interaction.followup.send("✅ Goodbye test sent!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot online as {bot.user} and ready!')

bot.run(os.environ['TOKEN'])


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
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
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
            "welcome_message": "Hey {user}, welcome to the server! Make yourself comfortable.",
            "welcome_gif": "https://media.tenor.com/w2Yv2U6r3UAAAAAm/stephen-curry-curry.gif",
            "goodbye_channel": None,
            "goodbye_title": "Goodbye from {server}",
            "goodbye_message": "{user} has left the server. Hope to see you again soon!",
            "goodbye_gif": "https://media.tenor.com/w2Yv2U6r3UAAAAAm/stephen-curry-curry.gif"
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

# --- WELCOME / GOODBYE EVENTS ---
@bot.event
async def on_member_join(member):
    conf = get_server_config(member.guild.id)
    channel_id = conf["welcome_channel"]
    if channel_id:
        channel = member.guild.get_channel(int(channel_id))
        if channel:
            title = conf["welcome_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
            desc = conf["welcome_message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
            
            embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
            if conf["welcome_gif"]:
                embed.set_image(url=conf["welcome_gif"])
            await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    conf = get_server_config(member.guild.id)
    channel_id = conf["goodbye_channel"]
    if channel_id:
        channel = member.guild.get_channel(int(channel_id))
        if channel:
            title = conf["goodbye_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
            desc = conf["goodbye_message"].replace("{user}", member.name).replace("{server}", member.guild.name)
            
            embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
            if conf["goodbye_gif"]:
                embed.set_image(url=conf["goodbye_gif"])
            await channel.send(embed=embed)

# --- CONFIGURATION SLASH COMMANDS ---
@bot.tree.command(name="upload_gif", description="Upload an image/GIF and get its direct URL")
@app_commands.describe(attachment="Upload your GIF or image file here")
async def upload_gif(interaction: discord.Interaction, attachment: discord.Attachment):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    
    await interaction.response.send_message(f"✅ Here is your direct URL:\n`{attachment.url}`", ephemeral=True)

@bot.tree.command(name="set_welcome_channel", description="Set the welcome messages channel")
@app_commands.describe(channel="Tag the channel (e.g. #general) or paste its ID")
async def set_welcome_channel(interaction: discord.Interaction, channel: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    
    clean_id = channel.replace("<#", "").replace(">", "")
    if not clean_id.isdigit():
        return await interaction.response.send_message("❌ Please tag a valid channel like #general!", ephemeral=True)
        
    update_server_config(interaction.guild.id, "welcome_channel", int(clean_id))
    await interaction.response.send_message("✅ Welcome channel successfully updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_title", description="Set the welcome message title")
@app_commands.describe(title="The title (you can use {user} and {server})")
async def set_welcome_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_title", title)
    await interaction.response.send_message("✅ Welcome title updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_message", description="Set the welcome message text")
@app_commands.describe(message="The text (you can use {user} and {server})")
async def set_welcome_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_message", message)
    await interaction.response.send_message("✅ Welcome message updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_gif", description="Set the welcome GIF/image link")
@app_commands.describe(url="Direct link of the GIF or image")
async def set_welcome_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_gif", url)
    await interaction.response.send_message("✅ Welcome GIF updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_channel", description="Set the goodbye messages channel")
@app_commands.describe(channel="Tag the channel (e.g. #general) or paste its ID")
async def set_goodbye_channel(interaction: discord.Interaction, channel: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    
    clean_id = channel.replace("<#", "").replace(">", "")
    if not clean_id.isdigit():
        return await interaction.response.send_message("❌ Please tag a valid channel like #general!", ephemeral=True)
        
    update_server_config(interaction.guild.id, "goodbye_channel", int(clean_id))
    await interaction.response.send_message("✅ Goodbye channel successfully updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_title", description="Set the goodbye message title")
@app_commands.describe(title="The title (you can use {user} and {server})")
async def set_goodbye_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_title", title)
    await interaction.response.send_message("✅ Goodbye title updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_message", description="Set the goodbye message text")
@app_commands.describe(message="The text (you can use {user} and {server})")
async def set_goodbye_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_message", message)
    await interaction.response.send_message("✅ Goodbye message updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_gif", description="Set the goodbye GIF/image link")
@app_commands.describe(url="Direct link of the GIF or image")
async def set_goodbye_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_gif", url)
    await interaction.response.send_message("✅ Goodbye GIF updated!", ephemeral=True)

@bot.tree.command(name="test", description="Test welcome or goodbye messages")
@app_commands.describe(tipo="Choose whether to test welcome or goodbye")
@app_commands.choices(tipo=[
    app_commands.Choice(name="welcome", value="welcome"),
    app_commands.Choice(name="goodbye", value="goodbye")
])
async def test_command(interaction: discord.Interaction, tipo: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    conf = get_server_config(interaction.guild.id)
    
    if tipo == "welcome":
        channel_id = conf["welcome_channel"]
        if not channel_id:
            return await interaction.followup.send("❌ You must set a welcome channel first using `/set_welcome_channel`!", ephemeral=True)
        
        channel = interaction.guild.get_channel(int(channel_id))
        if not channel:
            return await interaction.followup.send("❌ The configured welcome channel no longer exists!", ephemeral=True)
            
        title = conf["welcome_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["welcome_message"].replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name)
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
        if conf["welcome_gif"]:
            embed.set_image(url=conf["welcome_gif"])
        
        await channel.send(embed=embed)
        await interaction.followup.send("✅ Welcome test sent successfully to the configured channel!", ephemeral=True)

    elif tipo == "goodbye":
        channel_id = conf["goodbye_channel"]
        if not channel_id:
            return await interaction.followup.send("❌ You must set a goodbye channel first using `/set_goodbye_channel`!", ephemeral=True)
        
        channel = interaction.guild.get_channel(int(channel_id))
        if not channel:
            return await interaction.followup.send("❌ The configured goodbye channel no longer exists!", ephemeral=True)
            
        title = conf["goodbye_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["goodbye_message"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
        if conf["goodbye_gif"]:
            embed.set_image(url=conf["goodbye_gif"])
        
        await channel.send(embed=embed)
        await interaction.followup.send("✅ Goodbye test sent successfully to the configured channel!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot online as {bot.user} and commands synced!')

bot.run(os.environ['TOKEN'])


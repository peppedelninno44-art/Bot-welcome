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
            "welcome_gif": "https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyazJweXM1eGZiNWtmb3ZycDN6b3kyMHlydmhtd3lxNjUxcTc4czhtZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2ZpkYucNiZpovyuMkf/giphy.gif",
            "goodbye_channel": None,
            "goodbye_title": "Goodbye from {server}",
            "goodbye_message": "{user} has left the server. Hope to see you again soon!",
            "goodbye_gif": "https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyazJweXM1eGZiNWtmb3ZycDN6b3kyMHlydmhtd3lxNjUxcTc4czhtZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2ZpkYucNiZpovyuMkf/giphy.gif"
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
            embed.set_image(url=conf["goodbye_gif"])
            await channel.send(embed=embed)

# --- CONFIGURATION SLASH COMMANDS ---
@bot.tree.command(name="upload_gif", description="Upload an image/GIF and get its direct URL")
@app_commands.describe(attachment="Upload your GIF or image file here")
async def upload_gif(interaction: discord.Interaction, attachment: discord.Attachment):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    # Restituisce il link diretto del file caricato su Discord
    await interaction.followup.send(f"✅ Here is your direct URL:\n```{attachment.url}
    

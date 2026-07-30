import discord
from discord.ext import commands
from discord import app_commands
import os
import json

# --- CONFIGURAZIONE ---
ADMIN_IDS = [1171135456306536450, 924641550133248000]
CONFIG_FILE = "server_config.json"
# ----------------------

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
            "welcome_title": "Benvenuto su {server}!",
            "welcome_message": "Hey {user}, benvenuto nel server! Mettiti comodo.",
            "welcome_gif": "https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyazJweXM1eGZiNWtmb3ZycDN6b3kyMHlydmhtd3lxNjUxcTc4czhtZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2ZpkYucNiZpovyuMkf/giphy.gif",
            "goodbye_channel": None,
            "goodbye_title": "Addio da {server}",
            "goodbye_message": "{user} ha lasciato il server. Speriamo di rivederci presto!",
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

# --- EVENTI WELCOME / GOODBYE ---
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

# --- COMANDI SLASH DI CONFIGURAZIONE ---
@bot.tree.command(name="set_welcome_channel", description="Imposta il canale per i benvenuti")
@app_commands.describe(channel="Il canale dove inviare i benvenuti")
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_channel", channel.id)
    await interaction.response.send_message(f"✅ Canale di benvenuto impostato su {channel.mention}", ephemeral=True)

@bot.tree.command(name="set_welcome_title", description="Imposta il titolo del messaggio di benvenuto")
@app_commands.describe(title="Il titolo (puoi usare {user} e {server})")
async def set_welcome_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_title", title)
    await interaction.response.send_message(f"✅ Titolo di benvenuto aggiornato!", ephemeral=True)

@bot.tree.command(name="set_welcome_message", description="Imposta il messaggio di benvenuto")
@app_commands.describe(message="Il testo (puoi usare {user} e {server})")
async def set_welcome_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_message", message)
    await interaction.response.send_message(f"✅ Messaggio di benvenuto aggiornato!", ephemeral=True)

@bot.tree.command(name="set_welcome_gif", description="Imposta il link della GIF/immagine di benvenuto")
@app_commands.describe(url="Il link diretto della GIF o immagine")
async def set_welcome_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_gif", url)
    await interaction.response.send_message(f"✅ GIF di benvenuto aggiornata!", ephemeral=True)

@bot.tree.command(name="set_goodbye_channel", description="Imposta il canale per gli addii")
@app_commands.describe(channel="Il canale dove inviare i messaggi di uscita")
async def set_goodbye_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_channel", channel.id)
    await interaction.response.send_message(f"✅ Canale di uscita impostato su {channel.mention}", ephemeral=True)

@bot.tree.command(name="set_goodbye_title", description="Imposta il titolo del messaggio di uscita")
@app_commands.describe(title="Il titolo (puoi usare {user} e {server})")
async def set_goodbye_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_title", title)
    await interaction.response.send_message(f"✅ Titolo di uscita aggiornato!", ephemeral=True)

@bot.tree.command(name="set_goodbye_message", description="Imposta il messaggio di uscita")
@app_commands.describe(message="Il testo (puoi usare {user} e {server})")
async def set_goodbye_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_message", message)
    await interaction.response.send_message(f"✅ Messaggio di uscita aggiornato!", ephemeral=True)

@bot.tree.command(name="set_goodbye_gif", description="Imposta il link della GIF/immagine di uscita")
@app_commands.describe(url="Il link diretto della GIF o immagine")
async def set_goodbye_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_gif", url)
    await interaction.response.send_message(f"✅ GIF di uscita aggiornata!", ephemeral=True)

# --- COMANDI DI TEST (/test welcome e /test goodbye) ---
@bot.tree.command(name="test", description="Testa i messaggi di benvenuto o uscita")
@app_commands.describe(tipo="Scegli se testare welcome o goodbye")
@app_commands.choices(tipo=[
    app_commands.Choice(name="welcome", value="welcome"),
    app_commands.Choice(name="goodbye", value="goodbye")
])
async def test_command(interaction: discord.Interaction, tipo: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("Non hai i permessi!", ephemeral=True)
    
    conf = get_server_config(interaction.guild.id)
    
    if tipo == "welcome":
        channel_id = conf["welcome_channel"]
        if not channel_id:
            return await interaction.response.send_message("❌ Devi prima impostare un canale di benvenuto con `/set_welcome_channel`!", ephemeral=True)
        
        channel = interaction.guild.get_channel(int(channel_id))
        if not channel:
            return await interaction.response.send_message("❌ Il canale di benvenuto impostato non esiste più!", ephemeral=True)
            
        title = conf["welcome_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["welcome_message"].replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name)
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
        embed.set_image(url=conf["welcome_gif"])
        
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Test di benvenuto inviato con successo nel canale configurato!", ephemeral=True)

    elif tipo == "goodbye":
        channel_id = conf["goodbye_channel"]
        if not channel_id:
            return await interaction.response.send_message("❌ Devi prima impostare un canale di uscita con `/set_goodbye_channel`!", ephemeral=True)
        
        channel = interaction.guild.get_channel(int(channel_id))
        if not channel:
            return await interaction.response.send_message("❌ Il canale di uscita impostato non esiste più!", ephemeral=True)
            
        title = conf["goodbye_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["goodbye_message"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
        embed.set_image(url=conf["goodbye_gif"])
        
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Test di uscita inviato con successo nel canale configurato!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot online as {bot.user} e comandi sincronizzati!')

bot.run(os.environ['TOKEN'])

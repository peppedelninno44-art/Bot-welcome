from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

ADMIN_IDS = [1171135456306536450, 924641550133248000]
CONFIG_FILE = "server_config.json"
announcement_channels = {}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- MEMORY PROTECTION (Impostazioni persistenti) ---
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
            "welcome_title": "Welcome!",
            "welcome_message": "WELCOME {user} TO THE {server}! You are our {member_count}th member! ENJOY!!!",
            "welcome_gif": "",
            "goodbye_channel": None,
            "goodbye_title": "Goodbye!",
            "goodbye_message": "{user} has left the server.",
            "goodbye_gif": ""
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

# --- WELCOME EVENT ---
@bot.event
async def on_member_join(member):
    print(f"DEBUG JOIN: {member.name} joined server {member.guild.name}!")
    try:
        conf = get_server_config(member.guild.id)
        channel_id = conf.get("welcome_channel")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if channel:
                member_count = member.guild.member_count
                title = conf["welcome_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
                desc = conf["welcome_message"].replace("{user}", member.mention).replace("{server}", member.guild.name).replace("{member_count}", str(member_count))
                
                embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
                if conf.get("welcome_gif"):
                    embed.set_image(url=conf["welcome_gif"])
                
                await channel.send(embed=embed)
                print("DEBUG JOIN: Welcome message sent successfully!")
    except Exception as e:
        print(f"ERROR in on_member_join: {e}")

# --- GOODBYE EVENT ---
@bot.event
async def on_member_remove(member):
    print(f"DEBUG REMOVE: {member.name} left or was kicked from {member.guild.name}!")
    try:
        conf = get_server_config(member.guild.id)
        channel_id = conf.get("goodbye_channel")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if channel:
                title = conf["goodbye_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
                desc = conf["goodbye_message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
                
                embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
                if conf.get("goodbye_gif"):
                    embed.set_image(url=conf["goodbye_gif"])
                
                await channel.send(embed=embed)
                print("DEBUG REMOVE: Goodbye message sent successfully!")
    except Exception as e:
        print(f"ERROR in on_member_remove: {e}")

# --- SETUP COMMANDS ---
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

@bot.tree.command(name="set_welcome_title", description="Set welcome embed title")
async def set_welcome_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_title", title)
    await interaction.response.send_message("✅ Welcome title updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_message", description="Set welcome text/description")
async def set_welcome_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_message", message)
    await interaction.response.send_message("✅ Welcome message updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_title", description="Set goodbye embed title")
async def set_goodbye_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_title", title)
    await interaction.response.send_message("✅ Goodbye title updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_message", description="Set goodbye text/description")
async def set_goodbye_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_message", message)
    await interaction.response.send_message("✅ Goodbye message updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_gif", description="Set the welcome GIF URL")
async def set_welcome_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_gif", url)
    await interaction.response.send_message("✅ Welcome GIF updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_gif", description="Set the goodbye GIF URL")
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
        
        member_count = interaction.guild.member_count
        title = conf["welcome_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["welcome_message"].replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name).replace("{member_count}", str(member_count))
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
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
        
        title = conf["goodbye_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["goodbye_message"].replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name)
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
        if conf.get("goodbye_gif"): embed.set_image(url=conf["goodbye_gif"])
        await ch.send(embed=embed)
        await interaction.followup.send("✅ Goodbye test sent!", ephemeral=True)

# --- INFO / SETTINGS COMMAND ---
@bot.tree.command(name="settings", description="Shows current server configuration and channels")
async def settings(interaction: discord.Interaction):
    conf = get_server_config(interaction.guild.id)
    
    w_ch = f"<#{conf['welcome_channel']}>" if conf.get("welcome_channel") else "Not set"
    g_ch = f"<#{conf['goodbye_channel']}>" if conf.get("goodbye_channel") else "Not set"
    
    embed = discord.Embed(title="⚙️ Server Settings & Configuration", color=discord.Color.blue())
    embed.add_field(name="Welcome Channel", value=w_ch, inline=True)
    embed.add_field(name="Goodbye Channel", value=g_ch, inline=True)
    embed.add_field(name="Welcome Title", value=conf.get("welcome_title"), inline=False)
    embed.add_field(name="Goodbye Title", value=conf.get("goodbye_title"), inline=False)
    embed.add_field(name="Welcome GIF", value=conf.get("welcome_gif") or "None", inline=False)
    embed.add_field(name="Goodbye GIF", value=conf.get("goodbye_gif") or "None", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- HELP / MENU COMMAND ---
@bot.tree.command(name="help", description="Shows the menu with all available bot commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Bot Menu & Commands", description="Here is the list of all available commands:", color=discord.Color.purple())
    
    embed.add_field(
        name="🛠️ Admin Setup Commands",
        value=(
            "`/set_welcome_channel` - Set welcome channel\n"
            "`/set_goodbye_channel` - Set goodbye channel\n"
            "`/set_welcome_title` - Set welcome embed title\n"
            "`/set_welcome_message` - Set welcome message\n"
            "`/set_goodbye_title` - Set goodbye embed title\n"
            "`/set_goodbye_message` - Set goodbye message\n"
            "`/set_welcome_gif` - Set welcome GIF URL\n"
            "`/set_goodbye_gif` - Set goodbye GIF URL\n"
            "`/test` - Test welcome or goodbye message"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎮 Fun & Utility Commands",
        value=(
            "`/match` - Create a 1v1 match between two players with buttons\n"
            "`/chance` - Calculate win probabilities between two players\n"
            "`/8ball` - Ask a question to the magic ball\n"
            "`/testa_o_croce` - Flip a coin (Heads or Tails)\n"
            "`/frase_casuale` - Get a random epic ring quote\n"
            "`/set_announcement_channel` - Set announcement channel\n"
            "`/settings` - View current server configuration\n"
            "`/help` - Open this menu"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 1. /match COMMAND ---
@bot.tree.command(name="match", description="Create a 1v1 match between two players")
@app_commands.describe(player1="The first player", player2="The second player")
async def match(interaction: discord.Interaction, player1: discord.Member, player2: discord.Member):
    embed = discord.Embed(
        title="⚔️ 1v1 MATCH",
        description=f"{player1.mention} VS {player2.mention}",
        color=discord.Color.gold()
    )
    embed.add_field(name="Player 1", value=player1.mention, inline=False)
    embed.add_field(name="Player 2", value=player2.mention, inline=False)
    embed.set_footer(text=f"Match created on {discord.utils.utcnow().strftime('%d/%m/%Y - %H:%M')}")

    class MatchView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Win P1", style=discord.ButtonStyle.green)
        async def win_p1(self, interaction: discord.Interaction, button: discord.ui.Button):
            win_embed = discord.Embed(
                title="🏆 VICTORY!",
                description=f"The winner of the match is **{player1.display_name}**!",
                color=discord.Color.gold()
            )
            win_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ZwbHZ4aDZicXR3MHhveHBocHRvN3VrcDZ2cGR3bnNuc3l0dzN6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif")
            await interaction.response.send_message(embed=win_embed, ephemeral=False)

        @discord.ui.button(label="Win P2", style=discord.ButtonStyle.green)
        async def win_p2(self, interaction: discord.Interaction, button: discord.ui.Button):
            win_embed = discord.Embed(
                title="🏆 VICTORY!",
                description=f"The winner of the match is **{player2.display_name}**!",
                color=discord.Color.gold()
            )
            win_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ZwbHZ4aDZicXR3MHhveHBocHRvN3VrcDZ2cGR3bnNuc3l0dzN6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif")
            await interaction.response.send_message(embed=win_embed, ephemeral=False)

        @discord.ui.button(label="Rematch", style=discord.ButtonStyle.blurple, emoji="🔄")
        async def rematch(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message(f"🔄 Rematch requested between {player1.mention} and {player2.mention}!", ephemeral=False)

    await interaction.response.send_message(embed=embed, view=MatchView())

# --- 2. /chance COMMAND ---
@bot.tree.command(name="chance", description="Calculate win probabilities between two players")
@app_commands.describe(player1="First player", player2="Second player")
async def chance(interaction: discord.Interaction, player1: discord.Member, player2: discord.Member):
    p1_chance = random.randint(15, 85)
    p2_chance = 100 - p1_chance
    
    embed = discord.Embed(title="🎲 Match Probability / Chance", color=discord.Color.magenta())
    embed.add_field(name=player1.display_name, value=f"Win Chance: **{p1_chance}%**", inline=True)
    embed.add_field(name=player2.display_name, value=f"Win Chance: **{p2_chance}%**", inline=True)
    
    await interaction.response.send_message(embed=embed)

# --- 3. /8ball COMMAND ---
@bot.tree.command(name="8ball", description="Ask a question and get a magical prediction")
@app_commands.describe(question="The question you want to ask")
async def ball8(interaction: discord.Interaction, question: str):
    responses = [
        "Sì, assolutamente!",
        "È molto probabile.",
        "Senza dubbio.",
        "Le probabilità sono a favore.",
        "Chiedi di nuovo più tardi...",
        "Non ci farei affidamento.",
        "Molto improbabile.",
        "Assolutamente no!"
    ]
    answer = random.choice(responses)
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.dark_purple())
    embed.add_field(name="Domanda", value=question, inline=False)
    embed.add_field(name="Risposta", value=answer, inline=False)
    await interaction.response.send_message(embed=embed)

# --- 4. /testa_o_croce COMMAND ---
@bot.tree.command(name="testa_o_croce", description="Flip a coin: Heads or Tails")
async def testa_o_croce(interaction: discord.Interaction):
    result = random.choice(["🪙 Testa (Heads)", "🪙 Croce (Tails)"])
    embed = discord.Embed(title="🪙 Lancio della Moneta", description=f"È uscito: **{result}**!", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

# --- 5. /frase_casuale COMMAND ---
@bot.tree.command(name="frase_casuale", description="Get a random epic quote or ring statement")
async def frase_casuale(interaction: discord.Interaction):
    quotes = [
        "\"From the opening rounds, the fight delivered intense exchanges!\" 🥊",
        "\"The champion stands tall, ready for the next legendary clash!\" 🌍",
        "\"A clear and decisive verdict on the professional division stage!\" ⚡",
        "\"The official decision stands without hesitation!\" 🥇",
        "\"Absolute peak of their regions, a battle to remember forever!\" 🔥"
    ]
    quote = random.choice(quotes)
    embed = discord.Embed(title="📜 Ring Quote", description=quote, color=discord.Color.teal())
    await interaction.response.send_message(embed=embed)

# --- 6. /set_announcement_channel COMMAND ---
@bot.tree.command(name="set_announcement_channel", description="Set the channel for match announcements")
@app_commands.describe(channel="The channel where announcements will be sent")
async def set_announcement_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    announcement_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"✅ Announcement channel successfully set to {channel.mention}!", ephemeral=True)

# --- BOT STARTUP ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

bot.run(os.environ['TOKEN'])
        

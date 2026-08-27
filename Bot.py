from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import psycopg2

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

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS server_config (
                guild_id TEXT PRIMARY KEY,
                config_data JSONB
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database Supabase connected and initialized successfully!")
    except Exception as e:
        print(f"Database connection error: {e}")

init_db()

def load_config():
    config = {}
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT guild_id, config_data FROM server_config")
        rows = cur.fetchall()
        for row in rows:
            config[str(row[0])] = row[1]
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error loading config: {e}")
    return config

def save_config_guild(guild_id, guild_data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO server_config (guild_id, config_data) 
            VALUES (%s, %s)
            ON CONFLICT (guild_id) 
            DO UPDATE SET config_data = EXCLUDED.config_data
        """, (str(guild_id), json.dumps(guild_data)))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error saving config: {e}")

def get_server_config(guild_id):
    config = load_config()
    str_id = str(guild_id)
    if str_id not in config:
        default_data = {
            "welcome_channel": None,
            "welcome_title": "Welcome!",
            "welcome_message": "WELCOME {user} TO THE {server}! You are our {member_count}th member! ENJOY!!!",
            "welcome_gif": "",
            "goodbye_channel": None,
            "goodbye_title": "Goodbye!",
            "goodbye_message": "{user} has left the server.",
            "goodbye_gif": ""
        }
        save_config_guild(guild_id, default_data)
        return default_data
    return config[str_id]

def update_server_config(guild_id, key, value):
    conf = get_server_config(guild_id)
    conf[key] = value
    save_config_guild(guild_id, conf)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_member_join(member):
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
                if conf.get("welcome_gif"): embed.set_image(url=conf["welcome_gif"])
                await channel.send(embed=embed)
    except Exception as e:
        print(f"ERROR in on_member_join: {e}")

@bot.event
async def on_member_remove(member):
    try:
        conf = get_server_config(member.guild.id)
        channel_id = conf.get("goodbye_channel")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if channel:
                title = conf["goodbye_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
                desc = conf["goodbye_message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
                embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
                if conf.get("goodbye_gif"): embed.set_image(url=conf["goodbye_gif"])
                await channel.send(embed=embed)
    except Exception as e:
        print(f"ERROR in on_member_remove: {e}")

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
        if not ch_id: return await interaction.followup.send("Set welcome channel first!", ephemeral=True)
        ch = interaction.guild.get_channel(int(ch_id))
        if not ch: return await interaction.followup.send("Channel not found!", ephemeral=True)
        member_count = interaction.guild.member_count
        title = conf["welcome_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["welcome_message"].replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name).replace("{member_count}", str(member_count))
        embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
        if conf.get("welcome_gif"): embed.set_image(url=conf["welcome_gif"])
        await ch.send(embed=embed)
        await interaction.followup.send("✅ Welcome test sent!", ephemeral=True)
    elif tipo == "goodbye":
        ch_id = conf.get("goodbye_channel")
        if not ch_id: return await interaction.followup.send("Set goodbye channel first!", ephemeral=True)
        ch = interaction.guild.get_channel(int(ch_id))
        if not ch: return await interaction.followup.send("Channel not found!", ephemeral=True)
        title = conf["goodbye_title"].replace("{user}", interaction.user.name).replace("{server}", interaction.guild.name)
        desc = conf["goodbye_message"].replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name)
        embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
        if conf.get("goodbye_gif"): embed.set_image(url=conf["goodbye_gif"])
        await ch.send(embed=embed)
        await interaction.followup.send("✅ Goodbye test sent!", ephemeral=True)

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
            "`/8ball` - Ask a question and get a magical prediction\n"
            "`/testa_o_croce` - Flip a coin (Heads or Tails)\n"
            "`/frase_casuale` - Get a random epic ring quote\n"
            "`/roll` - 🎲 Roll a dice\n"
            "`/poll` - 📊 Create a quick poll\n"
            "`/userinfo` - 👤 View user details\n"
            "`/settings` - View current server configuration\n"
            "`/help` - Open this menu"
        ),
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="match", description="Create a 1v1 match between two players")
@app_commands.describe(player1="The first player", player2="The second player")
async def match(interaction: discord.Interaction, player1: discord.Member, player2: discord.Member):
    embed = discord.Embed(title="⚔️ 1v1 MATCH", description=f"{player1.mention} VS {player2.mention}", color=discord.Color.gold())
    embed.add_field(name="Player 1", value=player1.mention, inline=False)
    embed.add_field(name="Player 2", value=player2.mention, inline=False)
    embed.set_footer(text=f"Match created on {discord.utils.utcnow().strftime('%d/%m/%Y - %H:%M')}")

    class MatchView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Win P1", style=discord.ButtonStyle.green)
        async def win_p1(self, interaction: discord.Interaction, button: discord.ui.Button):
            win_embed = discord.Embed(title="🏆 VICTORY!", description=f"The winner of the match is **{player1.display_name}**!", color=discord.Color.gold())
            win_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ZwbHZ4aDZicXR3MHhveHBocHRvN3VrcDZ2cGR3bnNuc3l0dzN6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif")
            await interaction.response.send_message(embed=win_embed, ephemeral=False)

        @discord.ui.button(label="Win P2", style=discord.ButtonStyle.green)
        async def win_p2(self, interaction: discord.Interaction, button: discord.ui.Button):
            win_embed = discord.Embed(title="🏆 VICTORY!", description=f"The winner of the match is **{player2.display_name}**!", color=discord.Color.gold())
            win_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ZwbHZ4aDZicXR3MHhveHBocHRvN3VrcDZ2cGR3bnNuc3l0dzN6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif")
            await interaction.response.send_message(embed=win_embed, ephemeral=False)

        @discord.ui.button(label="Rematch", style=discord.ButtonStyle.blurple, emoji="🔄")
        async def rematch(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message(f"🔄 Rematch requested between {player1.mention} and {player2.mention}!", ephemeral=False)

    await interaction.response.send_message(embed=embed, view=MatchView())

@bot.tree.command(name="8ball", description="Ask a question and get a magical prediction")
@app_commands.describe(question="The question you want to ask")
async def ball8(interaction: discord.Interaction, question: str):
    responses = [
        "Yes, absolutely!", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
        "Reply hazy, try again.", "Better not tell you now.", "My sources say no.",
        "Outlook not so good.", "Very doubtful.", "Definitely not!"
    ]
    answer = random.choice(responses)
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.dark_purple())
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=answer, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="testa_o_croce", description="Flip a coin: Heads or Tails")
async def testa_o_croce(interaction: discord.Interaction):
    result = random.choice(["🪙 Heads", "🪙 Tails"])
    embed = discord.Embed(title="🪙 Coin Flip", description=f"The result is: **{result}**!", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

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

@bot.tree.command(name="roll", description="Roll a dice from 1 to 6 (or custom max)")
@app_commands.describe(maximum="Maximum number on the dice (default 6)")
async def roll(interaction: discord.Interaction, maximum: int = 6):
    if maximum < 2: return await interaction.response.send_message("The dice must have at least 2 faces!", ephemeral=True)
    result = random.randint(1, maximum)
    embed = discord.Embed(title="🎲 Dice Roll", description=f"You rolled a dice up to {maximum} and got: **{result}**! 🎯", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="Create a quick poll with a question")
@app_commands.describe(question="The question for the poll")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
    embed.set_footer(text=f"Poll created by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    await message.add_reaction("🤷‍♂️")

@bot.tree.command(name="userinfo", description="View detailed information about a user")
@app_commands.describe(member="The user you

                       @bot.tree.command(name="userinfo", description="View detailed information about a user")
@app_commands.describe(member="The user you want to check")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if member is None: 
        member = interaction.user
    embed = discord.Embed(title=f"👤 User Info for {member.display_name}", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime('%d/%m/%Y'), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime('%d/%m/%Y'), inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(os.environ['TOKEN'])

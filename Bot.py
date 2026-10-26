import json
import random
import os
import threading
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord import app_commands
from discord.ext import commands


# --- SERVER HTTP PER KEEP-ALIVE ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Avvia il server in background
server_thread = Thread(target=run_server)
server_thread.daemon = True
server_thread.start()


# --- YOUR BOT CODE STARTS BELOW ---

ADMIN_IDS = [1171135456306536450, 924641550133248000]
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE): return {}
    try:
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    except Exception: return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4)
    except Exception as e: print(f"Error saving config: {e}")

def get_server_config(guild_id):
    config = load_config()
    str_id = str(guild_id)
    if str_id not in config:
        config[str_id] = {
            "welcome_channel": None, "welcome_title": "Welcome!",
            "welcome_message": "WELCOME {user} TO THE {server}! You are our {member_count}th member! ENJOY!!!",
            "welcome_gif": "", "goodbye_channel": None, "goodbye_title": "Goodbye!",
            "goodbye_message": "{user} has left the server.", "goodbye_gif": "",
            "confession_channel": None
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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e: print(e)
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_member_join(member):
    try:
        conf = get_server_config(member.guild.id)
        channel_id = conf.get("welcome_channel")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if channel:
                m_count = member.guild.member_count
                title = conf["welcome_title"].replace("{user}", member.name).replace("{server}", member.guild.name)
                desc = conf["welcome_message"].replace("{user}", member.mention).replace("{server}", member.guild.name).replace("{member_count}", str(m_count))
                embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
                if conf.get("welcome_gif"): embed.set_image(url=conf["welcome_gif"])
                await channel.send(embed=embed)
    except Exception as e: print(f"ERROR in on_member_join: {e}")

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
    except Exception as e: print(f"ERROR in on_member_remove: {e}")

@bot.tree.command(name="set_goodbye_channel", description="Set the goodbye channel")
async def set_goodbye_channel(interaction: discord.Interaction, channel: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    clean_id = channel.replace("<#", "").replace(">", "")
    if not clean_id.isdigit(): return await interaction.response.send_message("Please tag a valid channel!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_channel", int(clean_id))
    await interaction.response.send_message("✅ Goodbye channel successfully set!", ephemeral=True)

@bot.tree.command(name="set_goodbye_gif", description="Set the goodbye GIF URL")
async def set_goodbye_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_gif", url)
    await interaction.response.send_message("✅ Goodbye GIF updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_message", description="Set goodbye text/description")
async def set_goodbye_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_message", message)
    await interaction.response.send_message("✅ Goodbye message updated!", ephemeral=True)

@bot.tree.command(name="set_goodbye_title", description="Set goodbye embed title")
async def set_goodbye_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "goodbye_title", title)
    await interaction.response.send_message("✅ Goodbye title updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_channel", description="Set the welcome channel")
async def set_welcome_channel(interaction: discord.Interaction, channel: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    clean_id = channel.replace("<#", "").replace(">", "")
    if not clean_id.isdigit(): return await interaction.response.send_message("Please tag a valid channel!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_channel", int(clean_id))
    await interaction.response.send_message("✅ Welcome channel successfully set!", ephemeral=True)

@bot.tree.command(name="set_welcome_gif", description="Set the welcome GIF URL")
async def set_welcome_gif(interaction: discord.Interaction, url: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_gif", url)
    await interaction.response.send_message("✅ Welcome GIF updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_message", description="Set welcome text/description")
async def set_welcome_message(interaction: discord.Interaction, message: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_message", message)
    await interaction.response.send_message("✅ Welcome message updated!", ephemeral=True)

@bot.tree.command(name="set_welcome_title", description="Set welcome embed title")
async def set_welcome_title(interaction: discord.Interaction, title: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    update_server_config(interaction.guild.id, "welcome_title", title)
    await interaction.response.send_message("✅ Welcome title updated!", ephemeral=True)

@bot.tree.command(name="set_confessions_channel", description="Set the channel for confessions")
@app_commands.checks.has_permissions(administrator=True)
async def set_confessions_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    update_server_config(interaction.guild.id, "confession_channel", channel.id)
    await interaction.response.send_message(f"✅ Confessions channel set to {channel.mention}!", ephemeral=True)

@bot.tree.command(name="say", description="Make the bot repeat your message")
@app_commands.describe(text="The message to repeat")
async def say(interaction: discord.Interaction, text: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("You don't have permissions!", ephemeral=True)
    await interaction.channel.send(text)
    await interaction.response.send_message("✅ Message sent!", ephemeral=True)

@bot.tree.command(name="8ball", description="Ask a question and get a magical prediction")
@app_commands.describe(question="The question to ask")
async def ball8(interaction: discord.Interaction, question: str):
    responses = ["Yes, absolutely!", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "Reply hazy, try again.", "Better not tell you now.", "My sources say no.", "Outlook not so good.", "Very doubtful.", "Definitely not!"]
    answer = random.choice(responses)
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.dark_purple())
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=answer, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="Flip a coin: Heads or Tails")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["🪙 Heads", "🪙 Tails"])
    embed = discord.Embed(title="🪙 Coin Flip", description=f"The result is: **{result}**!", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="fact", description="Get a random mind-blowing scientific/historical fact")
async def fact(interaction: discord.Interaction):
    facts = [
        "Honey never spoils. Ancient Egyptian tombs have honey over 3,000 years old still edible!",
        "A day on Venus is longer than its year. It rotates slower than it orbits the Sun.",
        "Bananas grow towards the sun against gravity, known as negative geotropism.",
        "Sharks have been on Earth longer than trees and Saturn's rings!",
        "Cleopatra lived closer to the Moon landing than to the building of the Great Pyramid."
    ]
    selected = random.choice(facts)
    embed = discord.Embed(title="💡 Mind-Blowing Fact", description=selected, color=discord.Color.magenta())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hack", description="Simulate a fake cyber attack on a user")
@app_commands.describe(member="The user to hack")
async def hack(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"💻 Initiating cyber attack on {member.mention}...", ephemeral=False)
    msg = await interaction.original_response()
    steps = [
        "[■□□□□□□□□□] 10% - Bypassing firewall...",
        "[■■■□□□□□□□] 30% - Extracting IP address...",
        "[■■■■■□□□□□] 50% - Downloading secret folder...",
        "[■■■■■■■■□□] 80% - Stealing Discord tokens...",
        "[■■■■■■■■■■] 100% - Hack completed successfully! 🔓"
    ]
    for step in steps:
        await asyncio.sleep(1.2)
        await msg.edit(content=f"💻 Hacking {member.mention}...\n{step}")
    passwords = ["123456", "ilovecats", "password123", "qwerty2026", "admin_007", "matrix_reloaded"]
    fake_ip = f"{random.randint(10, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    embed = discord.Embed(title="⚠️ Target Hacked!", description=f"Successfully breached **{member.display_name}**!", color=discord.Color.red())
    embed.add_field(name="Fake IP", value=fake_ip, inline=True)
    embed.add_field(name="Leaked Password", value=random.choice(passwords), inline=True)
    await interaction.followup.send(embed=embed, ephemeral=False)

@bot.tree.command(name="help", description="Shows the menu with all available bot commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Bot Menu & Commands", description="Here is the sorted list of unique commands:", color=discord.Color.purple())
    embed.add_field(name="🛠️ Admin Setup Commands", value="`/set_goodbye_channel` - Set goodbye channel\n`/set_goodbye_gif` - Set goodbye GIF URL\n`/set_goodbye_message` - Set goodbye message\n`/set_goodbye_title` - Set goodbye title\n`/set_welcome_channel` - Set welcome channel\n`/set_welcome_gif` - Set welcome GIF URL\n`/set_welcome_message` - Set welcome message\n`/set_welcome_title` - Set welcome title\n`/set_confessions_channel` - Set confessions channel\n`/say` - Make the bot repeat text\n`/ticket` - Create support ticket panel\n`/setuproles` - Create 20 standard roles\n`/setupchannels` - Create 35 organized channels", inline=False)
    embed.add_field(name="🎮 Fun & Unique Commands", value="`/8ball` - Ask the magic ball\n`/coinflip` - Flip a coin\n`/fact` - Random fact 💡\n`/hack` - Fake hack attack 💻\n`/match` - 1v1 Match view\n`/password` - Generate password 🔒\n`/ping` - Check latency 🏓\n`/poll` - Reaction poll\n`/quote` - Epic statement\n`/roast` - Roast user 🔥\n`/roll` - Roll dice\n`/rps` - Rock, Paper, Scissors\n`/serverinfo` - Server info 📊\n`/settings` - Server configuration\n`/ship` - Love calculator ❤️\n`/userinfo` - User details\n`/conspiracy` - Conspiracy theory\n`/globalweather` - Absurd weather\n`/worldexcuse` - Global excuse\n`/globalroast` - Global chat roast\n`/mysterybox` - Mystery box prize", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)
@bot.tree.command(name="match", description="Create a 1v1 match between two players")
async def match(interaction: discord.Interaction, player1: discord.Member, player2: discord.Member):
    embed = discord.Embed(title="⚔️ 1v1 MATCH", description=f"{player1.mention} VS {player2.mention}", color=discord.Color.gold())
    embed.add_field(name="Player 1", value=player1.mention, inline=False)
    embed.add_field(name="Player 2", value=player2.mention, inline=False)
    t_str = discord.utils.utcnow().strftime('%d/%m/%Y - %H:%M')
    embed.set_footer(text=f"Match created on {t_str}")

    class MatchView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Win P1", style=discord.ButtonStyle.green)
        async def win_p1(self, interaction: discord.Interaction, button: discord.ui.Button):
            w_embed = discord.Embed(title="🏆 VICTORY!", description=f"Winner is **{player1.display_name}**!", color=discord.Color.gold())
            gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ZwbHZ4aDZicXR3MHhveHBocHRvN3VrcDZ2cGR3bnNuc3l0dzN6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif"
            w_embed.set_image(url=gif_url)
            await interaction.response.send_message(embed=w_embed, ephemeral=False)

        @discord.ui.button(label="Win P2", style=discord.ButtonStyle.green)
        async def win_p2(self, interaction: discord.Interaction, button: discord.ui.Button):
            w_embed = discord.Embed(title="🏆 VICTORY!", description=f"Winner is **{player2.display_name}**!", color=discord.Color.gold())
            gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ZwbHZ4aDZicXR3MHhveHBocHRvN3VrcDZ2cGR3bnNuc3l0dzN6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif"
            w_embed.set_image(url=gif_url)
            await interaction.response.send_message(embed=w_embed, ephemeral=False)

    await interaction.response.send_message(embed=embed, view=MatchView())

@bot.tree.command(name="password", description="Generate a secure random password")
@app_commands.describe(length="Length of the password (default 12)")
async def password(interaction: discord.Interaction, length: int = 12):
    if length < 6 or length > 30: return await interaction.response.send_message("Length must be between 6 and 30 characters!", ephemeral=True)
    import string
    chars = string.ascii_letters + string.digits + "!@#$%&*"
    pwd = "".join(random.choice(chars) for _ in range(length))
    embed = discord.Embed(title="🔒 Secure Password Generator", description=f"Your secure password:\n`{pwd}`", color=discord.Color.dark_red())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency is **{latency}ms**.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

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

@bot.tree.command(name="quote", description="Get a random epic quote or ring statement")
async def quote(interaction: discord.Interaction):
    quotes = [
        "\"From opening rounds, intense exchanges!\" 🥊",
        "\"The champion stands tall for the next clash!\" 🌍",
        "\"A clear and decisive verdict on stage!\" ⚡",
        "\"The official decision stands without hesitation!\" 🥇",
        "\"Absolute peak of regions, a battle to remember!\" 🔥"
    ]
    selected = random.choice(quotes)
    embed = discord.Embed(title="📜 Ring Quote", description=selected, color=discord.Color.teal())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roast", description="Roast a user with style")
@app_commands.describe(member="The user you want to roast")
async def roast(interaction: discord.Interaction, member: discord.Member):
    roasts = [
        f"Hey {member.mention}, if I wanted to commit suicide I'd climb to your ego and jump down to your IQ.",
        f"{member.mention}, you're the reason the gene pool needs a lifeguard.",
        f"I'd agree with you {member.mention}, but then we'd both be wrong.",
        f"{member.mention} brings everyone so much joy... when they leave the room.",
        f"You are proof that God has a sense of humor, {member.mention}."
    ]
    selected = random.choice(roasts)
    embed = discord.Embed(title="🔥 Ultimate Roast", description=selected, color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roll", description="Roll a dice from 1 to 6 (or custom max)")
@app_commands.describe(maximum="Maximum number on the dice (default 6)")
async def roll(interaction: discord.Interaction, maximum: int = 6):
    if maximum < 2: return await interaction.response.send_message("The dice must have at least 2 faces!", ephemeral=True)
    result = random.randint(1, maximum)
    embed = discord.Embed(title="🎲 Dice Roll", description=f"Rolled up to {maximum} and got: **{result}**! 🎯", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rps", description="Play Rock, Paper, Scissors against the bot")
@app_commands.choices(choice=[
    app_commands.Choice(name="Rock 🪨", value="rock"),
    app_commands.Choice(name="Paper 📄", value="paper"),
    app_commands.Choice(name="Scissors ✂️", value="scissors")
])   
async def rps(interaction: discord.Interaction, choice: str):
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    if choice == bot_choice: result = "It's a tie! 🤝"
    elif (choice == "rock" and bot_choice == "scissors") or (choice == "paper" and bot_choice == "rock") or (choice == "scissors" and bot_choice == "paper"): result = "You win! 🎉"
    else: result = "You lose! 🤖"
    embed = discord.Embed(title="✂️ Rock, Paper, Scissors", color=discord.Color.gold())
    embed.add_field(name="Your Choice", value=choice.capitalize(), inline=True)
    embed.add_field(name="Bot's Choice", value=bot_choice.capitalize(), inline=True)
    embed.add_field(name="Result", value=result, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="View detailed information about this server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Server Info: {guild.name}", color=discord.Color.blue())
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    c_date = guild.created_at.strftime('%d/%m/%Y')
    embed.add_field(name="Created On", value=c_date, inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

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

@bot.tree.command(name="ship", description="Calculate love compatibility between two users")
@app_commands.describe(user1="First user", user2="Second user")
async def ship(interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
    percentage = random.randint(0, 100)
    bars = "█" * (percentage // 10) + "─" * (10 - (percentage // 10))
    if percentage > 80: comment = "A match made in heaven! 💕"
    elif percentage > 50: comment = "There is definitely some chemistry! ✨"
    else: comment = "Better keep them as friends... 💀"
    embed = discord.Embed(title="❤️ Love & Friendship Calculator", description=f"Shipping **{user1.display_name}** & **{user2.display_name}**", color=discord.Color.pink())
    val = f"`[{bars}]` **{percentage}%**\n{comment}"
    embed.add_field(name="Compatibility", value=val, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="View detailed information about a user")
@app_commands.describe(member="The user you want to check")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if member is None: member = interaction.user
    embed = discord.Embed(title=f"👤 User Info for {member.display_name}", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    j_date = member.joined_at.strftime("%d/%m/%Y")
    embed.add_field(name="Joined Server", value=j_date, inline=True)
    c_date = member.created_at.strftime("%d/%m/%Y")
    embed.add_field(name="Account Created", value=c_date, inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

class ConfessionModal(discord.ui.Modal, title="Send an Anonymous Confession"):
    confession_text = discord.ui.TextInput(
        label="Your confession",
        style=discord.TextStyle.paragraph,
        placeholder="Type what you want to confess anonymously here...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        s_conf = get_server_config(interaction.guild_id)
        channel_id = s_conf.get("confession_channel")
        if not channel_id:
            return await interaction.response.send_message("❌ The confession channel has not been set up yet!", ephemeral=True)
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(title="🔒 New Anonymous Confession", description=self.confession_text.value, color=discord.Color.dark_purple())
            embed.set_footer(text="Sent totally anonymously.")
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Your confession has been sent successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Error: The confession channel no longer exists.", ephemeral=True)

@bot.tree.command(name="confess", description="Send an anonymous confession to the dedicated server channel.")
async def confess(interaction: discord.Interaction):
    await interaction.response.send_modal(ConfessionModal())

class TicketModal(discord.ui.Modal, title="Create a Ticket"):
    reason = discord.ui.TextInput(
        label="Reason for ticket",
        style=discord.TextStyle.paragraph,
        placeholder="Explain briefly why you are opening this ticket...",
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category: category = await guild.create_category("Tickets")
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        embed = discord.Embed(title=f"🎫 Ticket by {interaction.user.display_name}", description=f"**Reason:** {self.reason.value}", color=discord.Color.blue())
        await channel.send(embed=embed, content=f"{interaction.user.mention}")
        await interaction.response.send_message(f"✅ Your ticket has been created: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket 🎫", style=discord.ButtonStyle.green, custom_id="open_ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

@bot.tree.command(name="ticket", description="Create the support ticket panel")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 Support Tickets", description="Click the button below to open a private support ticket with the staff.", color=discord.Color.green())
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Ticket panel created successfully!", ephemeral=True)

# --- NUOVI COMANDI SLASH PER RUOLI (COLORATI) E CANALI ---

@bot.tree.command(name="setuproles", description="Creates structured and colored community roles")
@app_commands.checks.has_permissions(administrator=True)
async def setuproles(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    roles_to_create = [
        {"name": "👑 | Founder", "color": discord.Color.gold()},
        {"name": "🛡️ | Admin", "color": discord.Color.red()},
        {"name": "⚔️ | Moderator", "color": discord.Color.orange()},
        {"name": "🤖 | Bot", "color": discord.Color.blue()},
        {"name": "💎 | Server Booster", "color": discord.Color.magenta()},
        {"name": "⭐ | VIP / Veteran", "color": discord.Color.purple()},
        {"name": "👥 | Member", "color": discord.Color.green()},
        {"name": "📢 | Announcement Ping", "color": discord.Color.light_grey()},
        {"name": "🎁 | Giveaway Ping", "color": discord.Color.light_grey()},
        {"name": "🎥 | Stream & Video Ping", "color": discord.Color.light_grey()},
        {"name": "🎉 | Event Ping", "color": discord.Color.light_grey()},
        {"name": "🎮 | Gamer", "color": discord.Color.teal()},
        {"name": "🎨 | Artist / Creator", "color": discord.Color.dark_orange()},
        {"name": "💻 | Developer / Tech", "color": discord.Color.dark_blue()},
        {"name": "🎵 | Music Lover", "color": discord.Color.dark_magenta()},
        {"name": "🎬 | Anime & Movies", "color": discord.Color.dark_purple()}
    ]
    created = 0
    for r in roles_to_create:
        try:
            await interaction.guild.create_role(name=r["name"], color=r["color"])
            created += 1
        except Exception:
            pass
    await interaction.followup.send(f"✅ Successfully created **{created} colored roles**!")
    

@bot.tree.command(name="setupchannels", description="Creates structured and meaningful community channels")
@app_commands.checks.has_permissions(administrator=True)
async def setupchannels(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    guild = interaction.guild
    try:
        cat_info = await guild.create_category("📌 ┆ WELCOME & INFO")
        await guild.create_text_channel("📖・rules", category=cat_info)
        await guild.create_text_channel("📢・announcements", category=cat_info)
        await guild.create_text_channel("🎭・get-roles", category=cat_info)
        await guild.create_text_channel("🎁・events-giveaways", category=cat_info)

        cat_comm = await guild.create_category("💬 ┆ COMMUNITY CHAT")
        await guild.create_text_channel("💬・general", category=cat_comm)
        await guild.create_text_channel("🤖・bot-commands", category=cat_comm)
        await guild.create_text_channel("😂・memes-and-media", category=cat_comm)
        await guild.create_text_channel("💡・suggestions", category=cat_comm)

        cat_topics = await guild.create_category("🎯 ┆ TOPIC HUBS")
        await guild.create_text_channel("🎮・gaming-discussion", category=cat_topics)
        await guild.create_text_channel("🎬・movies-and-anime", category=cat_topics)
        await guild.create_text_channel("💻・tech-and-setups", category=cat_topics)
        await guild.create_text_channel("🎨・art-and-creativity", category=cat_topics)

        cat_support = await guild.create_category("🎫 ┆ HELP & SUPPORT")
        await guild.create_text_channel("❓・faq", category=cat_support)
        await guild.create_text_channel("🎫・open-a-ticket", category=cat_support)

        cat_voice = await guild.create_category("🔊 ┆ VOICE CHANNELS")
        await guild.create_voice_channel("💬・General Lounge", category=cat_voice)
        await guild.create_voice_channel("🎮・Gaming Squad #1", category=cat_voice)
        await guild.create_voice_channel("🎮・Gaming Squad #2", category=cat_voice)
        await guild.create_voice_channel("🎧・Chill & Music", category=cat_voice)
        await guild.create_voice_channel("💤・AFK", category=cat_voice)

        await interaction.followup.send("✅ **Community channels and categories created successfully!**")
    except Exception as e:
        await interaction.followup.send(f"❌ Error creating channels: {e}")

@bot.tree.command(name="conspiracy", description="Get a random conspiracy theory")
async def conspiracy(interaction: discord.Interaction):
    theories = [
        "Pigeons are government drones charging their batteries on power lines.",
        "Your toaster is secretly streaming your breakfast habits to the cloud.",
        "Monday mornings are artificially lengthened by time travelers.",
        "Socks don't disappear in the wash; they turn into Tupperware lids.",
        "Cats can speak fluent English, they just choose to judge you in silence."
    ]
    embed = discord.Embed(
        title="🕵️‍♂️ Global Conspiracy Theory",
        description=random.choice(theories),
        color=discord.Color.dark_theme()
    )
    embed.set_footer(text=f"Requested by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="globalweather", description="Check global absurd weather")
async def globalweather(interaction: discord.Interaction):
    weather = [
        "Raining meatballs over Western Europe 🍝",
        "Heavy gravity storms reported in sector 7 🪐",
        "A 100% chance of extreme laziness worldwide 🛏️",
        "Neon rain clouds forming above major cities 🌆"
    ]
    embed = discord.Embed(
        title="🌍 World Weather Report",
        description=random.choice(weather),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Requested by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="globalroast", description="Roast a member globally")
@app_commands.describe(member="Member to roast")
async def globalroast(interaction: discord.Interaction, member: discord.Member = None):
    target = member.mention if member else interaction.user.mention
    roasts = [
        "has the processing speed of a Windows 95 computer running Crysis.",
        "brings down the average IQ of the entire international server.",
        "gets lost using Google Maps inside a straight corridor.",
        "looks like an NPC whose dialogue was deleted by mistake."
    ]
    embed = discord.Embed(
        title="🔥 Global Roast",
        description=f"{target} {random.choice(roasts)}",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Requested by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)
    
bot.run(os.environ['TOKEN'])

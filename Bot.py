import discord
from discord.ext import commands
import os # Necessario per leggere il token da Railway

# Configurazione permessi
intents = discord.Intents.default()
intents.members = True  # Necessario per rilevare ingressi e uscite
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# Welcome message
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="👋-welcome-and-goodbye")
    if channel:
        embed = discord.Embed(
            title="Welcome to the UBA!",
            description=f"Hey {member.mention}, welcome to the ring! Get ready to fight!",
            color=discord.Color.red()
        )
        embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2ZqZ2h6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/1256E1qM12S5R6/giphy.gif")
        await channel.send(content=f"New challenger: {member.mention}", embed=embed)

# Goodbye message
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="👋-welcome-and-goodbye")
    if channel:
        embed = discord.Embed(
            title="Challenger retired",
            description=f"{member.name} has left the ring. See you next time!",
            color=discord.Color.dark_grey()
        )
        embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2ZqZ2h6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKK2a4Z1aBwY5uM/giphy.gif")
        await channel.send(embed=embed)

# Questa riga legge il token dalla variabile che imposterai su Railway
bot.run(os.environ['TOKEN'])

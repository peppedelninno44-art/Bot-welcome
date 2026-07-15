import discord
from discord.ext import commands
import os
import asyncio

# Configurazione permessi
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

# Welcome message (lasciamo come prima)
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1516927038794240161)
    if channel:
        embed = discord.Embed(
            title="Welcome to the UBA!",
            description=f'Hey {member.mention}, welcome to the ring! Get ready to fight!',
            color=discord.Color.red()
        )
        embed.set_image(url="https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyazJweXM1eGZiNWtmb3ZycDN6b3kyMHlydmhtd3lxNjUxcTc4czhtZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2ZpkYucNiZpovyuMkf/giphy.gif")
        await channel.send(content=f'New challenger: {member.mention}', embed=embed)

# Goodbye message (MODIFICATO: invio come file per evitare blocchi)
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(1516927038794240161)
    if channel:
        # Messaggio di testo invece di Embed per l'immagine
        await channel.send(f'Challenger retired: {member.name} has left the ring. See you next time!')
        # Invio diretto della GIF come file
        await channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjExNDMwJnc9YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxxHOGTdzJC/giphy.gif")

bot.run(os.environ['TOKEN'])

import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1516927038794240161)
    if channel:
        embed = discord.Embed(
            title="Welcome to the UBA!",
            description=f'Hey {member.mention}, welcome to the ring! Get ready to fight!',
            color=discord.Color.red()
        )
        embed.set_image(url="https://c.tenor.com/tXFv497uQ5sAAAAC/ashitano-joe-joe-yabuki.gif")
        await channel.send(content=f'New challenger: {member.mention}', embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(1516927038794240161)
    if channel:
        embed = discord.Embed(
            title="Challenger retired",
            description=f'{member.name} has left the ring. See you next time!',
            color=discord.Color.dark_grey()
        )
        # Questa è una GIF di Joe che se ne va, molto stabile
        embed.set_image(url="https://c.tenor.com/2s787LqG9_IAAAAC/joe-yabuki-ashita-no-joe.gif")
        
        await asyncio.sleep(1)
        await channel.send(embed=embed)

bot.run(os.environ['TOKEN'])

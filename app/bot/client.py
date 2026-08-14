import os

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set in .env")

intents = discord.Intents.default()


class CustosBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = CustosBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="ping", description="Check if Custos is running")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! Custos is online.")

@bot.tree.command(name="help", description="Get help with Custos")
async def help(interaction: discord.Interaction):
    help_message = (
        "Here are the available commands:\n"
        "/ping - Check if Custos is running\n"
        "/help - Get help with Custos\n"
        # Add more commands and descriptions as needed
    )
    await interaction.response.send_message(help_message)

bot.run(TOKEN)
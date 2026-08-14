import os

import discord
from discord import app_commands
from dotenv import load_dotenv
from app.database.connection import SessionLocal
from app.database.models import User

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

class RegisterModal(discord.ui.Modal, title="Register with Custos"):

    college_id = discord.ui.TextInput(
        label="College ID",
        placeholder="Enter your college ID",
        required=True,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):

        discord_id = str(interaction.user.id)
        username = interaction.user.name
        college_id = str(self.college_id.value).strip()

        db = SessionLocal()

        try:
            # Check whether this Discord user already exists
            existing_user = (
                db.query(User)
                .filter(User.discord_id == discord_id)
                .first()
            )

            if existing_user:
                await interaction.response.send_message(
                    "You're already registered with Custos.",
                    ephemeral=True,
                )
                return

            # Create new user
            new_user = User(
                discord_id=discord_id,
                username=username,
                college_id=college_id,
            )

            db.add(new_user)
            db.commit()

            await interaction.response.send_message(
                f"You're registered, {interaction.user.mention}! "
                "Your Custos profile has been created.",
                ephemeral=True,
            )

        except Exception:
            db.rollback()

            await interaction.response.send_message(
                "Something went wrong while registering you. "
                "Please try again.",
                ephemeral=True,
            )

        finally:
            db.close()
@bot.tree.command(
    name="register",
    description="Register a new user with Custos"
)
async def register(interaction: discord.Interaction):
    await interaction.response.send_modal(RegisterModal())

bot.run(TOKEN)
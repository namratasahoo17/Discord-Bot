import os
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from dotenv import load_dotenv
from app.database.connection import SessionLocal
from app.database.models import User,StudySubmission

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
        "Here are the available commands:\n\n"
        "`/register`\n"
        "Register your account with Custos.\n\n"

        "`/profile`\n"
        "View your Custos profile.\n\n"

        "`/submit`\n"
        "Submit what you studied today.\n\n"

        "`/ping`\n"
        "Check if Custos is online.\n\n"

        "`/help`\n"
        "Show this help message."
        # Add more commands and descriptions as needed
    )
    await interaction.response.send_message(help_message,ephemeral=True,
    )

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

        except Exception as e:
            db.rollback()

            print(
                f"Registration error: {e}"
            )

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

@bot.tree.command(
    name="profile",
    description="View your Custos Profile",
)
async def profile(
    interaction: discord.Interaction,
):
    discord_id = str(
        interaction.user.id
    )
    db = SessionLocal()
    
    try:
        #Find their Custos Profile using their Discord ID.
        user = (
            db.query(User)
            .filter(
                User.discord_id == discord_id
            )
            .first()
        )
        # A user must register before they can have a profile.
        if not user:

            await interaction.response.send_message(
                "You aren't registered with Custos yet.\n"
                "Please use `/register` first.",
                ephemeral=True,
            )
            return

        # CREATE PROFILE EMBED
        # Embeds make the profile considerably cleaner than
        # sending a large block of plain text.
        embed = discord.Embed(
            title="📚 Custos Profile",
            description=(
                f"Profile for "
                f"{interaction.user.mention}"
            ),
        )

        embed.add_field(
            name="Name",
            value=user.username,
            inline=True,
        )
        embed.add_field(
            name="Discord ID",
            value=user.discord_id,
            inline=True,
        )
        embed.add_field(
            name="Custos ID",
            value=str(user.id),
            inline=True,
        )
        embed.add_file(
            name="College ID",
            value=user.college_id,
            inline=True,
        )
        # When the user registered.
        # This is stored by SQLAlchemy in created_at.
        embed.add_field(
            name="📅 Registered",
            value=user.created_at.strftime(
                "%d %B %Y"
            ),
            inline=True,
        )
        # When the user registered.
        # This is stored by SQLAlchemy in created_at.
        embed.add_field(
            name="📅 Registered",
            value=user.created_at.strftime(
                "%d %B %Y"
            ),
            inline=True,
        )
        # FUTURE FEATURES
        #
        # We're intentionally NOT calculating streaks or
        # badges yet.
        #
        # Later, we can add fields here such as:
        #
        #  Current Streak
        #  Longest Streak
        #  Study Days
        #  Badges
        #
        # without changing the basic profile structure.
        embed.set_factor(
            text="Custos.Study.Track.Grow."
        )
        #Profile info is private, so only the user
        #who requested it should see it.
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
    except Exception as e:
        print(
            f"Profile error:{e}"
        )
        await interaction.response.send_message(
            "Something went wrong while loading "
            "your profile. ",
            ephemeral=True,
        )
    finally:
        db.close()
# SUBMIT MODAL
class SubmitModel(
    discord.ui.Modal,
    title="Today's Study",
):
    subject = discord.ui.TextInput(
        label="What did you study?",
        placeholder="e.g. Data Structures",
        required=True,
        max_length=200,
    )
    description = discord.ui.TextInput(
        label="What did you learn?",
        placeholder=(
            "Describe what you studied today..."
        ),
        required=True,
        style=discord.TextStyle.paragraph,

        max_length=2000,
    )
    difficulty = discord.ui.TextInput(
        label="Difficulty",
        placeholder="Easy / Medium / Hard",
        required=True,
        max_length=20,
    )
    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):

        discord_id = str(
            interaction.user.id
        )
        # GET CURRENT DATE
        #
        # We use Indian Standard Time because the study day
        # should be based on the timezone Custos is designed
        # around, rather than the machine/server timezone.

        today = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).date()

        # Clean up the difficulty entered by the user.
        difficulty_value = str(
            self.difficulty.value
        ).strip().lower()

        # VALIDATE DIFFICULTY
         allowed_difficulties = {
            "easy",
            "medium",
            "hard",
        }

        if difficulty_value not in allowed_difficulties:

            await interaction.response.send_message(
                "Invalid difficulty.\n\n"
                "Please enter one of:\n"
                "🟢 Easy\n"
                "🟡 Medium\n"
                "🔴 Hard",
                ephemeral=True,
            )

            return

        db = SessionLocal()
        try:
            # FIND USER

            # A study submission must belong to a registered
            # Custos user.
            user = (
                db.query(User)
                .filter(
                    User.discord_id == discord_id
                )
                .first()
            )

            if not user:

                await interaction.response.send_message(
                    "You aren't registered with Custos yet.\n"
                    "Please use `/register` first.",
                    ephemeral=True,
                )

                return
            # CHECK TODAY'S SUBMISSION
            # We're keeping the rule:
            # ONE study submission per user per day.
            # This is important because later your streak
            # system will depend on study days rather than
            # number of submissions.

            existing_submission = (
                db.query(StudySubmission)
                .filter(
                    StudySubmission.user_id == user.id,
                    StudySubmission.study_date == today,
                )
                .first()
            )

            if existing_submission:

                await interaction.response.send_message(
                    "You've already submitted today's "
                    "study log.\n\n"
                    "You can submit again tomorrow.",
                    ephemeral=True,  
                )
                return 
            # CREATE STUDY SUBMISSION

            submission = StudySubmission(
                user_id=user.id,

                study_date=today,

                subject=str(
                    self.subject.value
                ).strip(),

                description=str(
                    self.description.value
                ).strip(),

                difficulty=difficulty_value,
            )

            db.add(submission)
            db.commit()
            # CONFIRMATION MESSAGE

            await interaction.response.send_message(
                "✅ **Today's study has been submitted!**\n\n"
                f" **Subject:** {submission.subject}\n"
                f" **Difficulty:** "
                f"{submission.difficulty.title()}\n"
                f" **Date:** "
                f"{submission.study_date.strftime('%d %B %Y')}",
                ephemeral=True,
            )

        except Exception as e:
            db.rollback()

            print(
                f"Submission error: {e}"
            )

            await interaction.response.send_message(
                "Something went wrong while submitting "
                "your study log.\n"
                "Please try again.",
                ephemeral=True,
            )
        finally:
            db.close()
# /SUBMIT
@bot.tree.command(
    name="submit",
    description="Submit what you studied today",
)
async def submit(
    interaction: discord.Interaction,
):
    await interaction.response.send_modal(
        SubmitModal()
    )

bot.run(TOKEN)
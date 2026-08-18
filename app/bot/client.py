import os
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from dotenv import load_dotenv

from app.database.connection import SessionLocal
from app.database.models import User, StudySubmission
from app.services.streak import update_streak


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is not set in .env"
    )


# ============================================================
# DISCORD SETUP
# ============================================================

intents = discord.Intents.default()


class CustosBot(discord.Client):

    def __init__(self):
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(
            self
        )

    async def setup_hook(self):
        await self.tree.sync()


bot = CustosBot()


# ============================================================
# BOT EVENTS
# ============================================================

@bot.event
async def on_ready():
    print(
        f"Logged in as {bot.user}"
    )


# ============================================================
# /PING
# ============================================================

@bot.tree.command(
    name="ping",
    description="Check if Custos is running",
)
async def ping(
    interaction: discord.Interaction,
):
    await interaction.response.send_message(
        "Pong! Custos is online."
    )


# ============================================================
# /HELP
# ============================================================

@bot.tree.command(
    name="help",
    description="Get help with Custos",
)
async def help(
    interaction: discord.Interaction,
):

    help_message = (
        "Here are the available commands:\n\n"

        "`/register`\n"
        "Register your account with Custos.\n\n"

        "`/profile`\n"
        "View your Custos profile.\n\n"

        "`/submit`\n"
        "Submit what you studied today.\n\n"

        "`/ping`\n"
        "Check if Custos is running.\n\n"

        "`/help`\n"
        "Show this help message."
    )

    await interaction.response.send_message(
        help_message,
        ephemeral=True,
    )


# ============================================================
# REGISTER MODAL
# ============================================================

class RegisterModal(
    discord.ui.Modal,
    title="Register with Custos",
):

    college_id = discord.ui.TextInput(
        label="College ID",
        placeholder="Enter your college ID",
        required=True,
        max_length=100,
    )

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):

        discord_id = str(
            interaction.user.id
        )

        username = interaction.user.name

        college_id = str(
            self.college_id.value
        ).strip()

        db = SessionLocal()

        try:

            # ------------------------------------------------
            # Check whether the user already exists
            # ------------------------------------------------

            existing_user = (
                db.query(User)
                .filter(
                    User.discord_id == discord_id
                )
                .first()
            )

            if existing_user:

                await interaction.response.send_message(
                    "You're already registered with Custos.",
                    ephemeral=True,
                )

                return

            # ------------------------------------------------
            # Create new user
            # ------------------------------------------------

            new_user = User(
                discord_id=discord_id,
                username=username,
                college_id=college_id,
            )

            db.add(new_user)

            db.commit()

            # ------------------------------------------------
            # Confirmation
            # ------------------------------------------------

            await interaction.response.send_message(
                f"You're registered, "
                f"{interaction.user.mention}! "
                "Your Custos profile has been created.",
                ephemeral=True,
            )

        except Exception as e:

            db.rollback()

            print(
                f"Registration error: {e}"
            )

            await interaction.response.send_message(
                "Something went wrong while "
                "registering you. "
                "Please try again.",
                ephemeral=True,
            )

        finally:

            db.close()


# ============================================================
# /REGISTER
# ============================================================

@bot.tree.command(
    name="register",
    description="Register a new user with Custos",
)
async def register(
    interaction: discord.Interaction,
):

    await interaction.response.send_modal(
        RegisterModal()
    )


# ============================================================
# /PROFILE
# ============================================================

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

        # ------------------------------------------------
        # Find user
        # ------------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.discord_id == discord_id
            )
            .first()
        )

        # ------------------------------------------------
        # User must be registered
        # ------------------------------------------------

        if not user:

            await interaction.response.send_message(
                "You aren't registered with Custos yet.\n"
                "Please use `/register` first.",
                ephemeral=True,
            )

            return

        # ------------------------------------------------
        # Create profile embed
        # ------------------------------------------------

        embed = discord.Embed(
            title="📚 Custos Profile",
            description=(
                f"Profile for "
                f"{interaction.user.mention}"
            ),
        )

        # ------------------------------------------------
        # Basic information
        # ------------------------------------------------

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

        embed.add_field(
            name="College ID",
            value=user.college_id,
            inline=True,
        )

        # ------------------------------------------------
        # Registration date
        # ------------------------------------------------

        embed.add_field(
            name="📅 Registered",
            value=user.created_at.strftime(
                "%d %B %Y"
            ),
            inline=True,
        )

        # ------------------------------------------------
        # Footer
        # ------------------------------------------------

        embed.set_footer(
            text="Custos. Study. Track. Grow."
        )

        # ------------------------------------------------
        # Send private profile
        # ------------------------------------------------

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    except Exception as e:

        print(
            f"Profile error: {e}"
        )

        await interaction.response.send_message(
            "Something went wrong while loading "
            "your profile.",
            ephemeral=True,
        )

    finally:

        db.close()


# ============================================================
# SUBMIT MODAL
# ============================================================

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

        # ====================================================
        # GET CURRENT DATE
        # ====================================================

        # Custos uses Indian Standard Time so the
        # study day isn't dependent on the server timezone.

        today = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).date()

        # ====================================================
        # VALIDATE DIFFICULTY
        # ====================================================

        difficulty_value = str(
            self.difficulty.value
        ).strip().lower()

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

            # =================================================
            # FIND USER
            # =================================================

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

            # =================================================
            # CHECK TODAY'S SUBMISSION
            # =================================================

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

            # =================================================
            # CREATE STUDY SUBMISSION
            # =================================================

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

            # =================================================
            # UPDATE STREAK
            # =================================================

            streak = update_streak(
                db=db,
                user=user,
                study_date=today,
            )

            # =================================================
            # COMMIT EVERYTHING
            # =================================================

            # Both the StudySubmission and UserStreak
            # are committed together.

            db.commit()

            # =================================================
            # CONFIRMATION
            # =================================================

            await interaction.response.send_message(
                "✅ **Today's study has been submitted!**\n\n"

                f"📖 **Subject:** "
                f"{submission.subject}\n"

                f"📊 **Difficulty:** "
                f"{submission.difficulty.title()}\n"

                f"📅 **Date:** "
                f"{submission.study_date.strftime('%d %B %Y')}\n"

                f"🔥 **Current streak:** "
                f"{streak.length} day(s)",

                ephemeral=True,
            )

        except Exception as e:

            # =================================================
            # ROLLBACK
            # =================================================

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


# ============================================================
# /SUBMIT
# ============================================================

@bot.tree.command(
    name="submit",
    description="Submit what you studied today",
)
async def submit(
    interaction: discord.Interaction,
):

    await interaction.response.send_modal(
        SubmitModel()
    )


# ============================================================
# START BOT
# ============================================================

bot.run(TOKEN)
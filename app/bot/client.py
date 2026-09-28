
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import discord

from discord import app_commands
from dotenv import load_dotenv

from app.services.ai.analyzer import analyze_student
from app.database.connection import SessionLocal

from app.database.models import (
    User,
    StudySubmission,
)

from app.services.streaks import (
    update_streak,
    get_current_streak,
)


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

        super().__init__(
            intents=intents
        )

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

            existing_user = (
                db.query(User)
                .filter(
                    User.discord_id
                    == discord_id
                )
                .first()
            )

            if existing_user:

                await interaction.response.send_message(
                    "You're already registered with Custos.",
                    ephemeral=True,
                )

                return

            new_user = User(
                discord_id=discord_id,
                username=username,
                college_id=college_id,
            )

            db.add(new_user)

            db.commit()

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

        user = (
            db.query(User)
            .filter(
                User.discord_id
                == discord_id
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

        current_streak = get_current_streak(
            db,
            user,
        )

        streak_length = (
            current_streak.length
            if current_streak
            else 0
        )

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

        embed.add_field(
            name="College ID",
            value=user.college_id,
            inline=True,
        )

        embed.add_field(
            name="📅 Registered",
            value=user.created_at.strftime(
                "%d %B %Y"
            ),
            inline=True,
        )

        embed.add_field(
            name="🔥 Streak",
            value=f"{streak_length} day(s)",
            inline=True,
        )

        embed.set_footer(
            text="Custos. Study. Track. Grow."
        )

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
# DIFFICULTY BUTTON
# ============================================================

class DifficultyButton(
    discord.ui.Button
):

    def __init__(
        self,
        label,
        value,
        emoji,
        subject,
        description,
        today,
        user_id,
    ):

        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
        )

        self.value = value
        self.subject = subject
        self.description = description
        self.today = today
        self.user_id = user_id

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        print(
            f"[SUBMIT] Difficulty selected: {self.value}"
        )

        # Make sure only the original user
        # can use these buttons.
        if str(interaction.user.id) != str(self.user_id):

            await interaction.response.send_message(
                "This difficulty menu belongs to another user.",
                ephemeral=True,
            )

            return

        difficulty_value = self.value

        db = SessionLocal()

        try:

            # ====================================================
            # FIND USER
            # ====================================================

            user = (
                db.query(User)
                .filter(
                    User.discord_id
                    == str(interaction.user.id)
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

            # ====================================================
            # CHECK TODAY'S SUBMISSION
            # ====================================================

            existing_submission = (
                db.query(StudySubmission)
                .filter(
                    StudySubmission.user_id
                    == user.id,

                    StudySubmission.study_date
                    == self.today,
                )
                .first()
            )

            if existing_submission:

                await interaction.response.edit_message(
                    content=(
                        "You've already submitted today's "
                        "study log.\n\n"
                        "You can submit again tomorrow."
                    ),
                    view=None,
                )

                return

            # ====================================================
            # CREATE STUDY SUBMISSION
            # ====================================================

            submission = StudySubmission(
                user_id=user.id,
                study_date=self.today,
                subject=self.subject,
                description=self.description,
                difficulty=difficulty_value,
            )

            db.add(submission)

            # ====================================================
            # UPDATE STREAK
            # ====================================================

            streak = update_streak(
                db=db,
                user=user,
                study_date=self.today,
            )

            # ====================================================
            # COMMIT
            # ====================================================

            db.commit()

            print(
                "[SUBMIT] Study submission saved successfully"
            )

            # ====================================================
            # CONFIRMATION
            # ====================================================

            await interaction.response.edit_message(
                content=(
                    "✅ **Today's study has been submitted!**\n\n"

                    f"📖 **Topics:** "
                    f"{submission.subject}\n\n"

                    f"📝 **What you learned:** "
                    f"{submission.description}\n\n"

                    f"📊 **Difficulty:** "
                    f"{submission.difficulty.title()}\n"

                    f"📅 **Date:** "
                    f"{submission.study_date.strftime('%d %B %Y')}\n"

                    f"🔥 **Current streak:** "
                    f"{streak.length} day(s)"
                ),
                view=None,
            )

        except Exception as e:

            db.rollback()

            print(
                f"[SUBMIT] Difficulty button error: {e}"
            )

            try:

                await interaction.response.edit_message(
                    content=(
                        "❌ Something went wrong while "
                        "saving your study log.\n"
                        "Please try again."
                    ),
                    view=None,
                )

            except Exception as response_error:

                print(
                    f"[SUBMIT] Could not send error message: "
                    f"{response_error}"
                )

        finally:

            db.close()


# ============================================================
# DIFFICULTY VIEW
# ============================================================

class DifficultyView(
    discord.ui.View
):

    def __init__(
        self,
        subject,
        description,
        user_id,
        today,
    ):

        # Give the user 5 minutes to choose.
        super().__init__(
            timeout=300
        )

        self.add_item(
            DifficultyButton(
                label="Easy",
                value="easy",
                emoji="🟢",
                subject=subject,
                description=description,
                today=today,
                user_id=user_id,
            )
        )

        self.add_item(
            DifficultyButton(
                label="Medium",
                value="medium",
                emoji="🟡",
                subject=subject,
                description=description,
                today=today,
                user_id=user_id,
            )
        )

        self.add_item(
            DifficultyButton(
                label="Hard",
                value="hard",
                emoji="🔴",
                subject=subject,
                description=description,
                today=today,
                user_id=user_id,
            )
        )


# ============================================================
# SUBMIT MODAL
# ============================================================

class SubmitModal(
    discord.ui.Modal,
    title="Today's Study",
):

    subject = discord.ui.TextInput(
        label="What did you study?",
        placeholder=(
            "e.g. Arrays, Linked Lists, Binary Trees"
        ),
        required=True,
        max_length=500,
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

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):

        print(
            "[SUBMIT] Modal submitted"
        )

        # ========================================================
        # IMPORTANT FIX
        # ========================================================
        # Acknowledge the modal immediately.
        #
        # Previously the bot did database work before responding.
        # If that took too long, Discord could consider the modal
        # interaction expired, which prevented the difficulty menu
        # from appearing.
        #
        # We defer immediately and use followup.send() later.
        # ========================================================

        await interaction.response.defer(
            ephemeral=True
        )

        discord_id = str(
            interaction.user.id
        )

        today = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).date()

        subject_value = str(
            self.subject.value
        ).strip()

        description_value = str(
            self.description.value
        ).strip()

        print(
            f"[SUBMIT] Subject: {subject_value}"
        )

        print(
            f"[SUBMIT] Description: {description_value}"
        )

        print(
            f"[SUBMIT] Date: {today}"
        )

        # ====================================================
        # VALIDATE INPUT
        # ====================================================

        if not subject_value:

            await interaction.followup.send(
                "Please enter at least one topic.",
                ephemeral=True,
            )

            return

        if not description_value:

            await interaction.followup.send(
                "Please describe what you learned.",
                ephemeral=True,
            )

            return

        # ====================================================
        # CHECK USER
        # ====================================================

        db = SessionLocal()

        try:

            print(
                "[SUBMIT] Checking user..."
            )

            user = (
                db.query(User)
                .filter(
                    User.discord_id
                    == discord_id
                )
                .first()
            )

            if not user:

                await interaction.followup.send(
                    "You aren't registered with Custos yet.\n"
                    "Please use `/register` first.",
                    ephemeral=True,
                )

                return

            print(
                f"[SUBMIT] User found: {user.username}"
            )

            # =================================================
            # CHECK TODAY'S SUBMISSION
            # =================================================

            existing_submission = (
                db.query(StudySubmission)
                .filter(
                    StudySubmission.user_id
                    == user.id,

                    StudySubmission.study_date
                    == today,
                )
                .first()
            )

            if existing_submission:

                print(
                    "[SUBMIT] User already submitted today."
                )

                await interaction.followup.send(
                    "You've already submitted today's "
                    "study log.\n\n"
                    "You can submit again tomorrow.",
                    ephemeral=True,
                )

                return

            # =================================================
            # SAVE USER ID
            # =================================================

            user_id = user.id

        except Exception as e:

            print(
                f"[SUBMIT] Database error: {e}"
            )

            await interaction.followup.send(
                "Something went wrong while checking "
                "your study log.\n"
                "Please try again.",
                ephemeral=True,
            )

            return

        finally:

            db.close()

        # ====================================================
        # CREATE DIFFICULTY VIEW
        # ====================================================

        print(
            "[SUBMIT] Creating difficulty view..."
        )

        try:

            view = DifficultyView(
                subject=subject_value,
                description=description_value,
                user_id=user_id,
                today=today,
            )

            print(
                "[SUBMIT] Difficulty view created"
            )

            # ====================================================
            # SEND DIFFICULTY BUTTONS
            # ====================================================

            # IMPORTANT:
            # Because the original interaction was deferred,
            # we MUST use followup.send(), not response.send_message().
            await interaction.followup.send(
                "### 📊 How difficult was today's study?\n\n"
                f"📖 **Topics:** {subject_value}\n\n"
                f"📝 **What you learned:** "
                f"{description_value}\n\n"
                "Select a difficulty:",

                view=view,
                ephemeral=True,
            )

            print(
                "[SUBMIT] Difficulty buttons sent successfully"
            )

        except Exception as e:

            print(
                f"[SUBMIT] ERROR CREATING DIFFICULTY MENU: {e}"
            )

            try:

                await interaction.followup.send(
                    "❌ Something went wrong while "
                    "showing the difficulty options.\n"
                    "Check the bot terminal for the error.",
                    ephemeral=True,
                )

            except Exception as response_error:

                print(
                    f"[SUBMIT] Could not send error message: "
                    f"{response_error}"
                )


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
        SubmitModal()
    )


# ============================================================
# /ANALYZE
# ============================================================

@bot.tree.command(
    name="analyze",
    description="Analyze your study progress using AI",
)
async def analyze(
    interaction: discord.Interaction,
):

    # ------------------------------------------------
    # Defer response because AI may take a few seconds
    # ------------------------------------------------

    await interaction.response.defer(
        ephemeral=True
    )

    discord_id = str(
        interaction.user.id
    )

    db = SessionLocal()

    try:

        # ====================================================
        # FIND USER
        # ====================================================

        user = (
            db.query(User)
            .filter(
                User.discord_id == discord_id
            )
            .first()
        )

        if not user:

            await interaction.followup.send(
                "You aren't registered with Custos yet.\n"
                "Please use `/register` first.",
                ephemeral=True,
            )

            return

        # ====================================================
        # GET STUDY HISTORY
        # ====================================================

        submissions = (
            db.query(StudySubmission)
            .filter(
                StudySubmission.user_id == user.id
            )
            .order_by(
                StudySubmission.study_date.asc()
            )
            .all()
        )

        if not submissions:

            await interaction.followup.send(
                "You don't have any study submissions yet.\n"
                "Use `/submit` to start building your study history.",
                ephemeral=True,
            )

            return

        # ====================================================
        # GET CURRENT STREAK
        # ====================================================

        current_streak = get_current_streak(
            db,
            user,
        )

        streak_length = (
            current_streak.length
            if current_streak
            else 0
        )

        # ====================================================
        # PREPARE STUDY DATA
        # ====================================================

        study_history = []

        for submission in submissions:

            study_history.append({
                "date": str(
                    submission.study_date
                ),

                "subject": submission.subject,

                "description": submission.description,

                "difficulty": submission.difficulty,
            })

        # ====================================================
        # CREATE AI DATA
        # ====================================================

        analysis_data = {
            "username": user.username,

            "total_submissions": len(
                submissions
            ),

            "current_streak": streak_length,

            "study_history": study_history,
        }

        # ====================================================
        # SEND DATA TO GEMINI
        # ====================================================

        analysis = await analyze_student(
            analysis_data
        )

        # ====================================================
        # CREATE DISCORD EMBED
        # ====================================================

        embed = discord.Embed(
            title="🧠 Custos AI Analysis",
            description=(
                f"Here's your study analysis, "
                f"{interaction.user.mention}."
            ),
        )

        # ====================================================
        # STRENGTHS
        # ====================================================

        strengths = analysis.get(
            "strengths",
            []
        )

        if strengths:

            embed.add_field(
                name="💪 Strengths",
                value="\n".join(
                    f"• {strength}"
                    for strength in strengths
                ),
                inline=False,
            )

        # ====================================================
        # WEAKNESSES
        # ====================================================

        weaknesses = analysis.get(
            "weaknesses",
            []
        )

        if weaknesses:

            embed.add_field(
                name="⚠️ Areas to Improve",
                value="\n".join(
                    f"• {weakness}"
                    for weakness in weaknesses
                ),
                inline=False,
            )

        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        recommendations = analysis.get(
            "recommendations",
            []
        )

        if recommendations:

            embed.add_field(
                name="🎯 Recommendations",
                value="\n".join(
                    f"• {recommendation}"
                    for recommendation in recommendations
                ),
                inline=False,
            )

        # ====================================================
        # FOCUS TOPICS
        # ====================================================

        focus_topics = analysis.get(
            "focus_topics",
            []
        )

        if focus_topics:

            embed.add_field(
                name="📚 Focus Topics",
                value=", ".join(
                    focus_topics
                ),
                inline=False,
            )

        # ====================================================
        # FOOTER
        # ====================================================

        embed.set_footer(
            text="Custos • Study. Track. Grow."
        )

        # ====================================================
        # SEND RESULT
        # ====================================================

        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )

    except json.JSONDecodeError:

        print(
            "Gemini returned invalid JSON."
        )

        await interaction.followup.send(
            "Gemini returned an invalid analysis. "
            "Please try again.",
            ephemeral=True,
        )

    except Exception as e:

        print(
            f"AI analysis error: {e}"
        )

        await interaction.followup.send(
            "Something went wrong while "
            "analyzing your study progress.",
            ephemeral=True,
        )

    finally:

        db.close()


# ============================================================
# START BOT
# ============================================================

bot.run(TOKEN)


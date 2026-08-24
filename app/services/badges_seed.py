from sqlalchemy.orm import Session

from ..database.models import Badge, BadgeCategory


BADGE_DATA = [

    # ========================================================
    # STUDYCRAFT
    # ========================================================

    {
        "name": "First Steps",
        "description": "Complete your first study session.",
        "category": "Studycraft",
        "requirement_type": "study_sessions_completed",
        "requirement_value": 1,
        "emoji": "👣",
        "rarity": "common",
    },

    {
        "name": "Night Owl",
        "description": "Complete a study session after 1 AM.",
        "category": "Studycraft",
        "requirement_type": "night_owl",
        "requirement_value": 1,
        "emoji": "🦉",
        "rarity": "common",
    },

    {
        "name": "Early Bird",
        "description": "Complete a study session between 4 AM and 7 AM.",
        "category": "Studycraft",
        "requirement_type": "early_bird",
        "requirement_value": 1,
        "emoji": "🌅",
        "rarity": "rare",
    },

    {
        "name": "Marathoner",
        "description": "Complete a study session lasting 3 hours or more.",
        "category": "Studycraft",
        "requirement_type": "long_session",
        "requirement_value": 180,
        "emoji": "🏃",
        "rarity": "rare",
    },

    {
        "name": "Master of the Craft",
        "description": "Complete 1000 study sessions.",
        "category": "Studycraft",
        "requirement_type": "study_sessions_completed",
        "requirement_value": 1000,
        "emoji": "🎓",
        "rarity": "legendary",
    },

    # ========================================================
    # CONSISTENCY
    # ========================================================

    {
        "name": "3-Day Streak",
        "description": "Complete study sessions for 3 consecutive days.",
        "category": "Consistency",
        "requirement_type": "consecutive_days_studied",
        "requirement_value": 3,
        "emoji": "🔥",
        "rarity": "common",
    },

    {
        "name": "7-Day Streak",
        "description": "Complete study sessions for 7 consecutive days.",
        "category": "Consistency",
        "requirement_type": "consecutive_days_studied",
        "requirement_value": 7,
        "emoji": "💥",
        "rarity": "common",
    },

    {
        "name": "14-Day Streak",
        "description": "Complete study sessions for 14 consecutive days.",
        "category": "Consistency",
        "requirement_type": "consecutive_days_studied",
        "requirement_value": 14,
        "emoji": "💯",
        "rarity": "common",
    },

    {
        "name": "30-Day Streak",
        "description": "Complete study sessions for 30 consecutive days.",
        "category": "Consistency",
        "requirement_type": "consecutive_days_studied",
        "requirement_value": 30,
        "emoji": "🏆",
        "rarity": "rare",
    },

    {
        "name": "100-Day Streak",
        "description": "Complete study sessions for 100 consecutive days.",
        "category": "Consistency",
        "requirement_type": "consecutive_days_studied",
        "requirement_value": 100,
        "emoji": "🥇",
        "rarity": "ultra-rare",
    },

    {
        "name": "200-Day Streak",
        "description": "Complete study sessions for 200 consecutive days.",
        "category": "Consistency",
        "requirement_type": "consecutive_days_studied",
        "requirement_value": 200,
        "emoji": "🏅",
        "rarity": "ultra-rare",
    },

    {
        "name": "365-Day Streak",
        "description": "Complete study sessions for 365 consecutive days.",
        "category": "Consistency",
        "requirement_type": "consecutive_days_studied",
        "requirement_value": 365,
        "emoji": "🥇",
        "rarity": "epic",
    },

    # ========================================================
    # COMEBACK
    # ========================================================

    {
        "name": "Comeback Kid",
        "description": "After breaking a streak, complete a study session.",
        "category": "Comeback",
        "requirement_type": "comeback",
        "requirement_value": 1,
        "emoji": "🔄",
        "rarity": "common",
    },

    {
        "name": "I Am Still Alive",
        "description": "Complete a study session after being inactive for more than a week.",
        "category": "Comeback",
        "requirement_type": "comeback_7_days",
        "requirement_value": 7,
        "emoji": "🔄",
        "rarity": "rare",
    },

    {
        "name": "Ghost",
        "description": "Disappear from the radar for 60 days, then make a comeback.",
        "category": "Comeback",
        "requirement_type": "comeback_60_days",
        "requirement_value": 60,
        "emoji": "👻",
        "rarity": "ultra-rare",
    },

    # ========================================================
    # EXPLORATION
    # ========================================================

    {
        "name": "Explorer",
        "description": "Complete study sessions in 10 different subjects.",
        "category": "Exploration",
        "requirement_type": "subjects_studied",
        "requirement_value": 10,
        "emoji": "🗺️",
        "rarity": "rare",
    },

    {
        "name": "Master Explorer",
        "description": "Complete study sessions in 20 different subjects.",
        "category": "Exploration",
        "requirement_type": "subjects_studied",
        "requirement_value": 20,
        "emoji": "🗺️",
        "rarity": "epic",
    },

    {
        "name": "Walking Encyclopedia",
        "description": "Complete study sessions in 50 different subjects.",
        "category": "Exploration",
        "requirement_type": "subjects_studied",
        "requirement_value": 50,
        "emoji": "🗺️",
        "rarity": "epic",
    },

    # ========================================================
    # STUDYCRAFT / EXTREME
    # ========================================================

    {
        "name": "Masochist",
        "description": "Complete a study session lasting 10 hours without taking a break.",
        "category": "Studycraft",
        "requirement_type": "no_break_long_session",
        "requirement_value": 600,
        "emoji": "💪",
        "rarity": "epic",
    },

    # ========================================================
    # MILESTONES
    # ========================================================

    {
        "name": "Achievement Hunter",
        "description": "Earn 10 badges.",
        "category": "Milestones",
        "requirement_type": "badges_earned",
        "requirement_value": 10,
        "emoji": "🥈",
        "rarity": "rare",
    },

    {
        "name": "Badge Collector",
        "description": "Earn 20 badges.",
        "category": "Milestones",
        "requirement_type": "badges_earned",
        "requirement_value": 20,
        "emoji": "💎",
        "rarity": "epic",
    },

    {
        "name": "Completionist",
        "description": "Earn every non-secret badge.",
        "category": "Milestones",
        "requirement_type": "completionist",
        "requirement_value": None,
        "emoji": "👑",
        "rarity": "legendary",
    },
]


def seed_badges(
    db: Session,
) -> None:
    """
    Seed all predefined Custos badges.

    Existing badges are not duplicated.

    Badge categories must already exist.
    """

    # --------------------------------------------------------
    # Load categories once
    # --------------------------------------------------------

    categories = {
        category.name: category.id
        for category in db.query(BadgeCategory).all()
    }

    # --------------------------------------------------------
    # Verify categories
    # --------------------------------------------------------

    for badge_data in BADGE_DATA:

        category_name = badge_data["category"]

        if category_name not in categories:
            raise ValueError(
                f"Badge category '{category_name}' "
                "does not exist in the database."
            )

    # --------------------------------------------------------
    # Insert badges
    # --------------------------------------------------------

    for badge_data in BADGE_DATA:

        existing_badge = (
            db.query(Badge)
            .filter(
                Badge.name == badge_data["name"]
            )
            .first()
        )

        if existing_badge:
            continue

        badge = Badge(
            name=badge_data["name"],
            description=badge_data["description"],
            category_id=categories[
                badge_data["category"]
            ],
            requirement_type=badge_data[
                "requirement_type"
            ],
            requirement_value=badge_data[
                "requirement_value"
            ],
            emoji=badge_data["emoji"],
            rarity=badge_data["rarity"],
        )

        db.add(badge)

    db.commit()
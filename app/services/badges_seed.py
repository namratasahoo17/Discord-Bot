from sqlalchemy.orm import Session

from ..database.models import Badge, BadgeCategory


BADGE_DATA = [{
    "id": 1,
    "name": "First Steps",
    "description": "Complete your first study session.",
    "category_id": 1,
    "category": "Studycraft",  
    "requirement_type": "study_sessions_completed",
    "requirement_value": 1,
    "emoji": "👣",
    "rarity": "common",
},
{
    "id": 2,
    "name": "Night Owl",
    "description": "Complete a study session after 1 AM.",
    "category_id": 1,
    "category": "Studycraft",
    "requirement_type": "study_sessions_completed",
    "requirement_value": 1,
    "emoji": "🦉",
    "rarity": "common",
},
{
    "id": 3,
    "name": "Early Bird",       
    "description": "Complete a study session between 4 AM and 7 AM.",
    "category_id": 1,
    "category": "Studycraft",
    "requirement_type": "study_sessions_completed",
    "requirement_value": 1,
    "emoji": "🌅",
    "rarity": "rare",
},
{
    "id": 4,
    "name": "Marathoner",
    "description": "Complete a study session lasting 3 hours or more.",
    "category_id": 1,   
    "category": "Studycraft",
    "requirement_type": "study_sessions_completed",
    "requirement_value": 1,
    "emoji": "🏃",
    "rarity": "rare",
},
{
    "id": 5,
    "name": "3-Day Streak",
    "description": "Complete study sessions for 3 consecutive days.",   
    "category_id": 6,
    "category": "Consistency",
    "requirement_type": "consecutive_days_studied",
    "requirement_value": 3,
    "emoji": "🔥",
    "rarity": "common",
},
{
    "id": 6,
    "name": "7-Day Streak",
    "description": "Complete study sessions for 7 consecutive days.",
    "category_id": 6,
    "category": "Consistency",
    "requirement_type": "consecutive_days_studied",
    "requirement_value": 7,
    "emoji": "💥",
    "rarity": "common",
},
{
    "id": 7,
    "name": "14-Day Streak",
    "description": "Complete study sessions for 14 consecutive days.",
    "category_id": 6,
    "category": "Consistency",
    "requirement_type": "consecutive_days_studied",
    "requirement_value": 14,
    "emoji": "💯",
    "rarity": "common",
},
{
    "id": 8,
    "name": "30-Day Streak",
    "description": "Complete study sessions for 30 consecutive days.",
    "category_id": 6,
    "category": "Consistency",
    "requirement_type": "consecutive_days_studied",
    "requirement_value": 30,
    "emoji": "🏆",
    "rarity": "rare",
},
{
    "id": 9,
    "name": "100-Day Streak",   
    "description": "Complete study sessions for 100 consecutive days.",
    "category_id": 6,
    "category": "Consistency",
    "requirement_type": "consecutive_days_studied",
    "requirement_value": 100,
    "emoji": "🥇",
    "rarity": "ultra-rare",
},
{
    "id": 10,
    "name": "200-Day Streak",
    "description": "Complete study sessions for 200 consecutive days.",
    "category_id": 6,
    "category": "Consistency",
    "requirement_type": "consecutive_days_studied",
    "requirement_value": 200,
    "emoji": "🏅",
    "rarity": "ultra-rare",
},
{
    "id": 11,
    "name": "365-Day Streak",
    "description": "Complete study sessions for 365 consecutive days.",
    "category_id": 6,
    "category": "Consistency",
    "requirement_type": "consecutive_days_studied",
    "requirement_value": 365,
    "emoji": "🥇",
    "rarity": "epic",
},
{
    "id": 12,
    "name": "Comeback Kid", 
    "description": "After breaking a streak, complete a study session.",
    "category_id": 7,
    "category": "Comeback",
    "requirement_type": "comeback",
    "requirement_value": 1,
    "emoji": "🔄",
    "rarity": "common",
},
{
    "id": 13,
    "name": "Explorer",
    "description": "Complete study sessions in 10 different subjects.",
    "category_id": 8,
    "category": "Exploration",
    "requirement_type": "subjects_studied",
    "requirement_value": 10,
    "emoji": "🗺️",
    "rarity": "rare",
},
{
    "id": 14,
    "name": "Master Explorer",
    "description": "Complete study sessions in 20 different subjects.",
    "category_id": 8,
    "category": "Exploration",
    "requirement_type": "subjects_studied",
    "requirement_value": 20,
    "emoji": "🗺️",
    "rarity": "epic",
},
{
    "id": 15,
    "name": "Walking Encyclopedia",
    "description": "Complete study sessions in 50 different subjects.",
    "category_id": 8,   
    "category": "Exploration",
    "requirement_type": "subjects_studied",
    "requirement_value": 50,
    "emoji": "🗺️",
    "rarity": "epic",
},
{
    "id": 16,
    "name": "Masochist",
    "description": "Complete a study session  with 10hrs without taking a break.",
    "category_id": 9,
    "category": "Comeback",
    "requirement_type": "no_break",
    "requirement_value": 1,
    "emoji": "💪",
    "rarity": "epic",
},
{
    "id": 17,
    "name": "I am still alive",
    "description": "Complete a study session after being inactive for more than a week.",
    "category_id": 7,
    "category": "Comeback",
    "requirement_type": "comeback",
    "requirement_value": 1,
    "emoji": "🔄",
    "rarity": "rare",
},
{
    "id": 18,
    "name": "Ghost",
    "description": "Dissappear from the radar for 60 days, then make a comeback.",
    "category_id": 7,
    "category": "Comeback",
    "requirement_type": "comeback",
    "requirement_value": 1,
    "emoji": "👻",
    "rarity": "ultra-rare",
},
{
    "id": 19,
    "name": "Master of the Craft",
    "description": "Complete 1000 study sessions.",
    "category_id": 1,
    "category": "Studycraft",
    "requirement_type": "study_sessions_completed",
    "requirement_value": 1000,
    "emoji": "🎓",
    "rarity": "legendary",
},

]


def seed_badges(
    db: Session,
) -> None:
    """
    Seed all predefined Custos badges.

    Existing badges are not duplicated.

    Categories must already exist in the database.
    """

    # ---------------------------------------------------------
    # Load all categories once.
    # ---------------------------------------------------------

    categories = {
        category.name: category.id
        for category in db.query(BadgeCategory).all()
    }

    # ---------------------------------------------------------
    # Make sure every category used by a badge exists.
    # ---------------------------------------------------------

    for badge_data in BADGE_DATA:

        category_name = badge_data["category"]

        if category_name not in categories:
            raise ValueError(
                f"Badge category '{category_name}' "
                "does not exist in the database."
            )

    # ---------------------------------------------------------
    # Insert badges.
    # ---------------------------------------------------------

    for badge_data in BADGE_DATA:

        existing_badge = (
            db.query(Badge)
            .filter(
                Badge.slug
                == badge_data["slug"]
            )
            .first()
        )

        if existing_badge:
            continue

        badge = Badge(
            name=badge_data["name"],
            slug=badge_data["slug"],
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
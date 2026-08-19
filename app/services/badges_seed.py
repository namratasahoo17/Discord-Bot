from sqlalchemy.orm import Session

from ..database.models import Badge, BadgeCategory


BADGE_DATA = [#write later
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
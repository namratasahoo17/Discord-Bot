from sqlalchemy.orm import Session

from ..database.models import BadgeCategory


def seed_badge_categories(
    db: Session,
) -> None:
    """
    Seed predefined badge categories.

    Add categories to CATEGORY_DATA below.
    Existing categories should not be duplicated.
    """

    CATEGORY_DATA = [
        # Add your categories here.
        #
        # Example:
        #
        # {
        #     "name": "Streak",
        # },
    ]

    for category_data in CATEGORY_DATA:

        existing_category = (
            db.query(BadgeCategory)
            .filter(
                BadgeCategory.name
                == category_data["name"]
            )
            .first()
        )

        if existing_category:
            continue

        category = BadgeCategory(
            name=category_data["name"],
        )

        db.add(category)

    db.commit()
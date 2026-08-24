from sqlalchemy.orm import Session

from ..database.models import BadgeCategory


CATEGORY_DATA = [
    {
        "name": "Studycraft",
    },
    {
        "name": "Chronicle",
    },
    {
        "name": "Knowledge",
    },
    {
        "name": "Momentum",
    },
    {
        "name": "Milestones",
    },
    {
        "name": "Consistency",
    },
    {
        "name": "Comeback",
    },
    {
        "name": "Exploration",
    },
]


def seed_badge_categories(
    db: Session,
) -> None:
    """
    Seed the predefined Custos badge categories.

    Existing categories are not duplicated.

    If a new category is added to CATEGORY_DATA later,
    running database initialization will add it.
    """

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
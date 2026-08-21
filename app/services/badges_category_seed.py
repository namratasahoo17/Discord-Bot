from sqlalchemy.orm import Session

from ..database.models import BadgeCategory


CATEGORY_DATA = [
    {   "id": 1,
        "name": "Studycraft",
    },
    {
        "id": 2,    
        "name": "Chronicle",
    },
    {   
        "id": 3,
        "name": "Knowledge",
    },
    {
        "id": 4,
        "name": "Momentum",
    },
    {
        "id": 5,
        "name": "Milestones",
    },
    {
        "id": 6,
        "name": "Consistency",
    },
    {
        "id": 7,
        "name": "Comeback",
    },
    {
        "id": 8,
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
    running the database initialization will automatically
    add the missing category.
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
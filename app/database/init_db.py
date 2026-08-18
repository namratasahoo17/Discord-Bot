from app.database.connection import (
    Base,
    engine,
    SessionLocal,
)

from app.database.models import (
    User,
    StudySubmission,
    BadgeCategory,
    Badge,
    UserBadge,
    UserStreak,
)

from app.services.badges_category_seed import (
    seed_badge_categories,
)


# ---------------------------------------------------------
# Create database tables
# ---------------------------------------------------------

Base.metadata.create_all(
    bind=engine
)


# ---------------------------------------------------------
# Seed default data
# ---------------------------------------------------------

db = SessionLocal()

try:
    seed_badge_categories(db)

    print("Database initialized.")

except Exception as e:
    db.rollback()

    print(
        f"Database initialization failed: {e}"
    )

    raise

finally:
    db.close()
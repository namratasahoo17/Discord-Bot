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

from app.services.badges_seed import (
    seed_badges,
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# SEED DEFAULT DATA
# ============================================================

db = SessionLocal()

try:

    seed_badge_categories(db)
    seed_badges(db)

    print("Database initialized successfully.")

except Exception as e:

    db.rollback()

    print(
        f"Database initialization failed: {e}"
    )

    raise

finally:

    db.close()
from datetime import date, timedelta
from sqlalchemy.orm import Session
from ..database.models import User, UserStreak

def get_active_streak(
        db: Session, user: User) -> UserStreak | None:
    
    """Get the active streak for a user."""

    return db.query(UserStreak).filter(
        UserStreak.user_id == user.id,
        UserStreak.is_active == True
    ).first()

def start_streak(db: Session, user: User,study_date: date) -> UserStreak:
    """Start a new streak for a user."""
    new_streak = UserStreak(
        user_id=user.id,
        start_date=date.today(),
        end_date=None,
        length=1,
        is_active=True
    )
    db.add(new_streak)
    db.flush()
    return new_streak

def extend_streak(db: Session, streak: UserStreak, study_date: date) -> UserStreak:
    """Extend an existing streak for a user."""
    streak.length += 1
    db.flush()
    return streak

def close_streak(db: Session, streak: UserStreak, end_date: date) -> UserStreak:

    """Close an existing streak for a user."""

    streak.is_active = False
    streak.end_date = end_date
    db.flush()
    return streak

def update_streak(db: Session, user: User, study_date: date) -> UserStreak:

    """Update the user's streak based on the study date."""
    
    streak = get_active_streak(db, user)
    if streak is None:
        return start_streak(db, user, study_date)
    last_study_date = streak.start_date + timedelta(days=streak.length - 1)
    if study_date == last_study_date:
        return streak
    expected_next_date = last_study_date + timedelta(days=1)
    if study_date == expected_next_date:
        return extend_streak(db, streak, study_date)
    if study_date < last_study_date:
        return streak
    close_streak(db, streak, last_study_date)

    return start_streak(db, user, study_date)

def get_current_streak(
        db: Session, user: User) -> UserStreak | None:
    """Get the current streak for a user, whether active or closed."""
    return get_active_streak(db, user)
def get_longest_streak(
        db: Session, user: User) -> UserStreak | None:
    """Get the longest streak for a user."""
    return db.query(UserStreak).filter(
        UserStreak.user_id == user.id
    ).order_by(UserStreak.length.desc()).first()
    
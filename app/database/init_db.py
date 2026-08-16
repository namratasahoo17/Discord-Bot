from .connection import Base, engine
from .models import User, StudySubmission, Badge, UserBadge

Base.metadata.create_all(bind=engine)

print("Database initialized.")
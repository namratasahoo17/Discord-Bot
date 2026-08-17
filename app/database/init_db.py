from app.database.connection import Base, engine
from app.database.models import User, StudySubmission, Badge, UserBadge

Base.metadata.create_all(bind=engine)

print("Database initialized.")
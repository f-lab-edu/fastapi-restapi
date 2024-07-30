from app.database import Base, engine
from app.domain.models import comment, post, user

# 기존 테이블 삭제
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

# 새로운 테이블 생성
print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Database initialized.")

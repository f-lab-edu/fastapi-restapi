# init_db.py

from database import Base, engine

# 기존 테이블 삭제
Base.metadata.drop_all(bind=engine)
# 새로운 테이블 생성
Base.metadata.create_all(bind=engine)

print("Database initialized.")

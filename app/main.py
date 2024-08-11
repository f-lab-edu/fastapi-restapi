# from datetime import datetime
#
# from fastapi import FastAPI, HTTPException, status
# from pydantic import BaseModel, Field
#
# app = FastAPI()  # fastapi 인스턴스 생성 , uvicorn이 참조하고 있는 것과 동일
#
#
# # @app.get("/") #fastapi 에게 바로 아래에 있는 함수가 다음으로 이동하는 요청을 처리한다는 것을 알려줌, URL "/"에 대한 GET 작동을 사용하는 요청을 받을 때 마다 fastapi에 의해 호출
# # async def read_root():
# #     return {"Hello": "World"}
# class RequestPost(BaseModel):  # 요청
#     author: str
#     title: str
#     content: str
#
#
# class ResponsePost(BaseModel):  # 응답
#     id: int
#     created_at: datetime
#     author: str
#     title: str
#     content: str
#
#
# in_memory = {}
# id_counter = 1
#
#
# @app.post("/posts/", response_model=in_memory)  # 게시글 생성
# def create_post(post: RequestPost) -> ResponsePost:
#     global id_counter
#     new_post = ResponsePost(
#         id=id_counter,
#         created_at=datetime.now(),
#         author=post.author,
#         title=post.title,
#         content=post.content,
#     )
#     in_memory[id_counter] = new_post
#     id_counter += 1
#     return new_post
#
#
# @app.get("/posts/{post_id}", response_model=in_memory)  # 없는거 보내면 500에러?
# def get_post(post_id: int):
#     if post_id not in in_memory:
#         return status.HTTP_204_NO_CONTENT
#         # raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="게시글이 없습니다.")
#     return in_memory[post_id]
#
#
# @app.get("/posts/", response_model=in_memory)
# def get_posts():
#     return [post.dict() for post in in_memory.values()]
#
#
# ############################################# 1-1
#
#
# @app.patch("/posts/{post_id}", response_model=in_memory)
# def update_post(post_id: int, update_post: RequestPost) -> ResponsePost:
#     if post_id not in in_memory:
#         # return status.HTTP_204_NO_CONTENT
#         # raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="게시글이 없습니다.")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
#         )
#     return in_memory[post_id]
#
#     original = in_memory[post_id]
#
#     # PATCH 방식에서는 전송된 필드만 업데이트합니다.
#     if update_post.author != original.author:
#         return status.HTTP_403_FORBIDDEN
#         # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="작성자가 다릅니다.")
#
#     if update_post.title:
#         original.title = update_post.title
#     if update_post.content:
#         original.content = update_post.content
#
#     # 업데이트된 시간
#     original.created_at = datetime.now()
#
#     return original
#
#
# @app.delete("/posts/{post_id}", response_model={})
# def delete_post(post_id: int) -> dict[int, ResponsePost]:
#     if post_id not in in_memory:
#         return status.HTTP_204_NO_CONTENT
#         # raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="게시글이 없습니다.")
#     in_memory.pop(post_id)
#     return status.HTTP_200_OK
#
#
# ############################################# 1-2
# from typing import List
#
# from fastapi import Depends, FastAPI, HTTPException, Response, status
# from sqlalchemy.orm import Session
#
# from . import crud
# from .domain.schemas import schemas
# from .domain.models import models
# from .database import SessionLocal, engine
#
# models.Base.metadata.create_all(bind=engine)
#
# app = FastAPI()
#
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# @app.post("/posts/", response_model=schemas.PostRead)
# def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
#     return crud.create_post(db=db, post_create=post)
#
#
# @app.get("/posts/{post_id}", response_model=schemas.PostRead)
# def read_post(post_id: int, db: Session = Depends(get_db)):
#     db_post = crud.get_post(db=db, post_id=post_id)
#     if db_post is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다.."
#         )
#     return db_post
#
#
# @app.get("/posts/", response_model=List[schemas.PostRead])
# def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     posts = crud.get_posts(db=db, skip=skip, limit=limit)
#     return posts
#
#
# @app.patch("/posts/{post_id}", response_model=schemas.PostRead)
# def update_post(post_id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
#     db_post = crud.get_post(db=db, post_id=post_id)
#     if db_post is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다.."
#         )
#     try:
#         updated_post = crud.update_post(db=db, post_id=post_id, post_update=post)
#     except ValueError as e:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
#     return updated_post
#
#
# @app.delete("/posts/{post_id}", response_model=schemas.PostRead)
# def delete_post(post_id: int, db: Session = Depends(get_db)):
#     db_post = crud.get_post(db=db, post_id=post_id)
#     if db_post is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다.."
#         )
#     crud.delete_post(db=db, post_id=post_id)
#     return Response(status_code=status.HTTP_200_OK)
########################################################## 1-4
from fastapi import FastAPI

from app.api import endpoints
from app.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(endpoints.router, prefix="/api", tags=["posts"])

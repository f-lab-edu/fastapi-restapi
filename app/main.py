from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()  # fastapi 인스턴스 생성 , uvicorn이 참조하고 있는 것과 동일


# @app.get("/") #fastapi 에게 바로 아래에 있는 함수가 다음으로 이동하는 요청을 처리한다는 것을 알려줌, URL "/"에 대한 GET 작동을 사용하는 요청을 받을 때 마다 fastapi에 의해 호출
# async def read_root():
#     return {"Hello": "World"}
class Post(BaseModel):
    id: int
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class User_post(BaseModel):  # 클래스의 분리
    author: str
    title: str
    content: str


in_memory = {}
id_counter = 1


@app.post("/posts/")  # 게시글 생성
async def Create_post(post: Post):  # 여기도 타입힌트
    global id_counter, in_memory
    post.Id = id_counter
    post.Created_At = datetime.now()
    in_memory[id_counter] = post.dict()
    id_counter += 1
    return post


@app.get("/posts/{post_id}")  # 게시글 조회
async def Get_post(post_id: int):  # 타입힌트 , async 왜 쓰는지 / 모르면 그냥 빼라
    if post_id not in in_memory:
        return None
    return in_memory[post_id]


@app.get("/posts/")  # 게시글 조회
async def List_post():  # PEP 8 준수
    return in_memory


############################################# 1-1


@app.patch("/posts/{post_id}")
async def Update_post(post_id: int, update_post: Post):
    if post_id not in in_memory:
        return None

    original = in_memory[post_id]

    if original["Author"] != update_post.Author:
        raise ValueError("작성자가 다릅니다.")  # HTTP응답메소드로 변경

    original["Title"] = update_post.Title
    original["Content"] = update_post.Content
    original["Created_At"] = datetime.now()


@app.delete("/posts/{post_id}")
async def Delete_post(post_id: int):
    if post_id not in in_memory:
        return None  # 여기도 HTTP응답메소드
    in_memory.pop(post_id)
    return in_memory


############################################# 1-2

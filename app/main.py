from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()  # fastapi 인스턴스 생성 , uvicorn이 참조하고 있는 것과 동일


# @app.get("/") #fastapi 에게 바로 아래에 있는 함수가 다음으로 이동하는 요청을 처리한다는 것을 알려줌, URL "/"에 대한 GET 작동을 사용하는 요청을 받을 때 마다 fastapi에 의해 호출
# async def read_root():
#     return {"Hello": "World"}
class Post(BaseModel):
    Id: int
    Author: str
    Title: str
    Content: str
    Created_At: Optional[datetime] = Field(default_factory=datetime.utcnow)


in_memory = []
id_counter = 1


@app.post("/posts/")  # 게시글 생성
async def Create_post(post: Post):
    global id_counter, in_memory
    post.Id = id_counter
    post.Created_At = datetime.now()
    id_counter += 1
    in_memory.append(post)
    return post


@app.get("/posts/{post_id}")  # 게시글 조회
async def Get_post(post_id: int):  # int가 있고 없고의 차이가뭐지?
    if post_id <= 0 or post_id > len(in_memory):
        return None
    return in_memory[post_id - 1]


@app.get("/posts/")  # 게시글 조회
async def List_post():
    return in_memory


############################################# 1-1


# @app.patch("/posts/{post_id}")
# async def Update_post(post_id: int, update_post: Post):
#     index = post_id - 1
#     original = in_memory[index]
#
#     if original.Author != update_post.Author:
#         raise ValueError("작성자가 다릅니다.")
#     in_memory[index].Title = update_post.Title
#     in_memory[index].Content = update_post.Content
#     in_memory[index].Created_At = datetime.now()
#
#
# @app.delete("/posts/{post_id}")
# async def Delete_post(post_id: int):
#     in_memory.pop(post_id - 1)
#     return in_memory


############################################# 1-2

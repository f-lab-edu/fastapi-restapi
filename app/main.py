from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()  # fastapi 인스턴스 생성 , uvicorn이 참조하고 있는 것과 동일


# @app.get("/") #fastapi 에게 바로 아래에 있는 함수가 다음으로 이동하는 요청을 처리한다는 것을 알려줌, URL "/"에 대한 GET 작동을 사용하는 요청을 받을 때 마다 fastapi에 의해 호출
# async def read_root():
#     return {"Hello": "World"}
class RequestPost(BaseModel):  # 요청
    author: str
    title: str
    content: str


class ResponsePost(BaseModel):  # 응답
    id: int
    created_at: datetime
    author: str
    title: str
    content: str


in_memory = {}
id_counter = 1


@app.post("/posts/")  # 게시글 생성
def create_post(post: RequestPost) -> ResponsePost:
    global id_counter
    new_post = ResponsePost(
        id=id_counter,
        created_at=datetime.now(),
        author=post.author,
        title=post.title,
        content=post.content,
    )
    in_memory[id_counter] = new_post
    id_counter += 1
    return new_post


@app.get("/posts/{post_id}")
def get_post(id_counter: int) -> ResponsePost:
    if id_counter in in_memory:
        return in_memory[id_counter]
    raise HTTPException(status_code=404, detail="게시글이 없습니다..")


@app.get("/posts/")
def get_posts():
    return list(in_memory.values())


############################################# 1-1


@app.patch("/posts/{post_id}")
def update_post(post_id: int, update_post: RequestPost) -> ResponsePost:
    if post_id not in in_memory:
        raise HTTPException(status_code=404, detail="게시글이 없습니다..")

    original = in_memory[post_id]

    if original.author != update_post.author:
        raise HTTPException(status_code=403, detail="작성자가 다릅니다..")

    updated_post = ResponsePost(
        id=post_id,
        created_at=datetime.now(),
        author=update_post.author,
        title=update_post.title,
        content=update_post.content,
    )

    in_memory[post_id] = updated_post
    return updated_post


# @app.delete("/posts/{post_id}")
# async def delete_post(post_id: int) -> dict[int, Post]:
#     if post_id not in in_memory:
#         raise HTTPException(status_code=404, detail="게시글이 없습니다..")
#     in_memory.pop(post_id)
#     return in_memory


############################################# 1-2

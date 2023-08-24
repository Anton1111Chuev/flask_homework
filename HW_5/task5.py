from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel, EmailStr, SecretStr
from starlette.responses import JSONResponse

app = FastAPI()


class User(BaseModel):
    id_: int
    name: str
    email: EmailStr
    password: SecretStr


USERS = [
    User(id_=1, name='User1', email='User1@test.com', password='123'),
    User(id_=2, name='User2', email='User2@test.com', password='123'),
    User(id_=3, name='User3', email='User3@test.com', password='123'),
]


@app.get('/users/')
async def all_users():
    return {'users': USERS}


@app.post('/user/')
async def add_user(user: User):
    USERS.append(user)
    return {"user": user, "status": "added"}


@app.delete('/user/{item_id}/')
async def del_user(item_id: int):
    for item in USERS:
        if item.id_ == item_id:
            USERS.remove(item)
            return {"message": "success"}
    else:
        return JSONResponse(content={"message": "Resource Not Found"}, status_code=404)


if __name__ == "__main__":
    uvicorn.run("task5:app", port=8000)

from fastapi import FastAPI, Request, Form, status
import uvicorn
from pydantic import BaseModel, EmailStr, SecretStr
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="./templates")


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


@app.get('/', response_class=HTMLResponse)
async def all_users(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, 'users': USERS})


@app.post('/add_user/', response_class=HTMLResponse)
async def add_user(request: Request, id_=Form(), name=Form(), email=Form(), password=Form()):
    user = User(id_=id_, name=name, email=email, password=password)
    USERS.append(user)
    redirect_url = request.url_for('index')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    uvicorn.run("task6:app", port=8000)

from datetime import datetime
from typing import Optional
import random

from fastapi import Depends, FastAPI, HTTPException, Header, Response
from pydantic import BaseModel, constr
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

from database import *
from model import *
from tools import *

Base.metadata.create_all(
    bind=engine
)  

@app.post("/api/register", tags=["register"])
async def register(data: Register_example): 
    if data.password != data.re_pw:
        return {"비밀번호가 일치하지 않습니다."}

    hashed_pw = hashing_pw(
        data.password
    ) 

    db_user = User( 
        username=data.username,
        password=hashed_pw,
        school_id=data.school_id,
    )

    with SessionLocal() as db:  
        db.add(db_user)  
        db.commit()

    return {"ok": "True"}


@app.post("/api/login", tags=["login"])
async def login(data: Login_example):
    pw = data.password
    hashed_pw = hashing_pw(pw)
    
    with SessionLocal() as db:  
        user = db.query(User).filter(User.username == data.username, User.password == hashed_pw).first()

    if not user:
        return {"아이디 혹은 비밀번호가 다릅니다."}

    elif user.role == 'admin':
        token = admin_Token(user.id)
        return ({"ok": "true"}, token) 
    
    token = encToken(user.id)
    return ({"ok": "true"}, token)


@app.post("/api/authcheck", tags=["authcheck test"])
async def authcheck(token : str = Header(...)):
    user = check_auth(token)
    
    if not user:
        return {"ok":"False"}
    
    return {"recived_token": token}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import bcrypt

from .database import get_db
from .models import UserModel, SessionModel
from .schema import UserCreate, UserProfile, Token

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

with open("public_key.pem", "r") as f:
    PUBLIC_KEY = f.read()
with open("private_key.pem", "r") as f:
    PRIVATE_KEY = f.read()


@app.post("/register", response_model=UserProfile)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # if user exists, raise an exception
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system",
        )
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    db_user = UserModel(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role="customer",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserProfile(
        username=db_user.username, email=db_user.email, role=db_user.role
    )


@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not bcrypt.checkpw(
        form_data.password.encode(), user.password_hash.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    expires = datetime.utcnow() + timedelta(minutes=60)
    token = jwt.encode(
        {
            "id": user.id,
            "exp": expires,
        },
        PRIVATE_KEY,
        algorithm="RS256",  # use RS256
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/profile", response_model=UserProfile)
def read_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])  # use RS256
        user_id = payload.get("id")
        user = db.query(UserModel).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserProfile(username=user.username, email=user.email, role=user.role)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

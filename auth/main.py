from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import JWTError, jwt


from .auth_database import Base, engine, get_db
from . import model
from . import schema
from . import utils

# Create tables
Base.metadata.create_all(bind=engine)

SECRET_KEY = "OCAWz_h24NCYi191upIQ4cdZBpeDUWGFb7iAQrEVWgc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="Auth API",
    description="JWT Role-Based Auth",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# ✅ Moved here — before routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise credential_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credential_exception


def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


@app.post("/signup")
def register_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(model.User).filter(
        model.User.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = utils.hash_password(user.password)
    new_user = model.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username,
            "email": new_user.email, "role": new_user.role}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(model.User).filter(
        model.User.username == form_data.username
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
    if not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}! You accessed a protected route."}


@app.get("/admin")
def admin_route(current_user: dict = Depends(require_roles(["admin"]))):
    return {"message": f"Welcome Admin {current_user['username']}"}


@app.get("/user")
def user_route(current_user: dict = Depends(require_roles(["user", "admin"]))):
    return {"message": f"Welcome {current_user['username']}"}

@app.get("/user/dashboard")
def user_dashboard(current_user: dict = Depends(require_roles(["user", "admin"]))):
    return {"message": f"Welcome to your dashboard, {current_user['username']}!"}
@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(require_roles(["admin"]))):
    return {"message": f"Welcome to the admin dashboard, {current_user['username']}!"}

@app.get("/profile")
def profile_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']}! Here is your profile."}

print("FastAPI app loaded successfully")
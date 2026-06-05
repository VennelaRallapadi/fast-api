from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/greet")
def greet():
    return {"message": "Hello sam"}

@app.get("/greet/{name}")
def greet_name(name: str):
    return {"message": f"Hello {name}"}          

@app.get("/hello/{name}")
def hello_name(name: str, age: Optional[int] = None):
    return {"message": f"Hello {name} and you are {age} years old"}

class Student(BaseModel):
    name: str
    age: int
    roll: int

@app.post("/create-student")                      # ✅ Fix 2: removed space from path
def create_student(student: Student):
    return {
        "name": student.name,                     # ✅ Fix 3: instance not class
        "age": student.age,
        "roll": student.roll
    }
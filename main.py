from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER

import models
from database import engine, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Templates & Static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Home Page - List ToDos
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

# Add New ToDo (Form)
@app.get("/add")
def add_form(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})

@app.post("/add")
def add(title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    todo = models.Todo(title=title, description=description)
    db.add(todo)
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

# Mark Complete
@app.get("/complete/{todo_id}")
def complete(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.complete = True
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

# Delete ToDo
@app.get("/delete/{todo_id}")
def delete(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

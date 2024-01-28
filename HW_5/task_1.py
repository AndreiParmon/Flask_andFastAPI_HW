from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()
tasks = []
templates = Jinja2Templates(directory='templates')


class Task(BaseModel):
    id: int
    title: str
    description: str
    status: bool = False


@app.post('/tasks/', response_model=Task)
async def create_task(task: Task):
    task_id = len(tasks) + 1
    task.id = task_id
    tasks.append(task)
    return task


@app.get('/tasks/', response_class=HTMLResponse)
async def show_tasks(request: Request):
    tasks_table = pd.DataFrame([vars(task) for task in tasks]).to_html(index=False)
    return templates.TemplateResponse('tasks.html', {'request': request, 'tasks_table': tasks_table})


@app.get('/tasks/{task_id}', response_class=HTMLResponse)
async def show_task(request: Request, task_id: int):
    task = pd.DataFrame([vars(task) for task in tasks if task.id == task_id]).to_html(index=False)
    return templates.TemplateResponse("task.html", {"request": request, "task": task})


@app.put('/tasks/{task_id}', response_model=Task)
async def update_task(task_id: int, task: Task):
    for i, change_task in enumerate(tasks):
        if change_task.id == task_id:
            task.id = task_id
            tasks[i] = task
            return task


@app.delete('/tasks/delete/{task_id}', response_class=HTMLResponse)
async def delete_task(task_id: int):
    for i, rem_task in enumerate(tasks):
        if rem_task.id == task_id:
            return pd.DataFrame([vars(tasks.pop(i))]).to_html()

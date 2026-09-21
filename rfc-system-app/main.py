import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from routes import users, applications

load_dotenv()

app = FastAPI()
app.mount('/static', StaticFiles(directory = 'static/css'), name = 'static')

templates = Jinja2Templates(directory = 'templates')

app.include_router(users.router, prefix = '', tags = ['User'])
app.include_router(applications.router, prefix = '', tags = ['Applications'])

@app.get('/')
async def get_index_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = 'index.html'
    )
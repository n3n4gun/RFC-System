import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from logging_config import configure_logging, log_request
from routes import applications, users

load_dotenv()
configure_logging()


@asynccontextmanager
async def lifespan(app):
    logger.info('Application started')
    try:
        yield
    finally:
        logger.info('Application stopped')


app = FastAPI(lifespan=lifespan)
app.middleware('http')(log_request)
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

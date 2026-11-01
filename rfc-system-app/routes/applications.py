from typing import Annotated, Literal
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import (
    APIRouter,
    Request,
    Response,
    HTTPException,
    Cookie,
    Depends,
    Form,
    status
)

from models import ActiveUserModel
from dependencies import get_current_active_user

router = APIRouter(prefix = '/application')
templates = Jinja2Templates(directory = 'templates/application_pages')

@router.get('/new')
async def show_new_application_page(
    request: Request,
    current_user: Annotated[ActiveUserModel, Depends(get_current_active_user)]
):
    if current_user.is_active:
        return templates.TemplateResponse(
            request = request,
            name = 'new_application_page.html'
        )

@router.post('/new')
async def create_new_application(
    request: Request,
    title: Annotated[str, Form()],
    service: Annotated[str, Form()],
    priority: Annotated[Literal['low', 'medium', 'hight', 'critical'], Form()],
    description: Annotated[str, Form()],
    current_user: Annotated[ActiveUserModel, Depends(get_current_active_user)]
):
    if not current_user.is_active:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = 'Forbidden',
            headers = {'Location', '/user/login'}
        )

    

@router.get('/{application_id}')
async def get_application_description(application_id):
    pass

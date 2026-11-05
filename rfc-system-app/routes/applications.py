from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from loguru import logger

from dependencies import (
    get_application_validator,
    get_current_active_user,
    get_db_service,
)
from infrastructure import NewApplicationValidator
from models import ActiveUserModel, CreateApplicationModel
from services import DataBaseService
from core import ApplicationOutcome

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
    title: Annotated[str, Form()],
    service: Annotated[str, Form()],
    priority: Annotated[Literal['low', 'medium', 'hight', 'critical'], Form()],
    description: Annotated[str, Form()],
    current_user: Annotated[ActiveUserModel, Depends(get_current_active_user)],
    application_validator: Annotated[NewApplicationValidator, Depends(get_application_validator)],
    db_service: Annotated[DataBaseService, Depends(get_db_service)]
):
    if not current_user.is_active:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = 'Forbidden',
            headers = {'Location', '/user/login'}
        )

    application_data = {
        'title': title,
        'service': service,
        'priority': priority,
        'description': description
    }

    try:
        application_data = application_validator.validate_new_application(application_data)

    except ValidationError:
        logger.warning('Application data validation failed')
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'UNSUCCESS application data validation'
        )

    transaction_status_outcome = db_service.create_new_application()

    match transaction_status_outcome:
        case ApplicationOutcome.APPLICATION_SUCCESS:
            return JSONResponse(
                status_code = status.HTTP_201_CREATED,
                content = {'status': 'success', 'message': 'New application was successfully created'}
            )

        case ApplicationOutcome.APPLICATION_DB_UNAVAILABLE:
            pass

        case ApplicationOutcome.APPLICATION_DB_ERROR:
            pass


@router.get('/{application_id}')
async def get_application_description(application_id):
    pass

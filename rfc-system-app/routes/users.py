from typing import Annotated

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
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from core import (
    AuthentificationOutcome,
    create_access_token,
    RegistrationOutcome,
)
from dependencies import (
    get_current_active_user,
    get_db_service,
    get_user_login_validator,
    get_user_reg_validator,
)
from infrastructure import UserLoginValidator, UserRegValidator
from models import ActiveUserModel, JWTTokenModel
from services import DataBaseService

router = APIRouter(prefix = '/user')
templates = Jinja2Templates(directory = 'templates/user_pages')

@router.get('/login')
async def show_login_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = 'login_page.html'
    )

@router.post('/login')
async def login_user(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    user_login_validator: Annotated[UserLoginValidator, Depends(get_user_login_validator)],
    db_service: Annotated[DataBaseService, Depends(get_db_service)]
):
    user_login_data = {
        'email': email,
        'password': password
    }

    if not user_login_validator.validate_user_login_data(user_login_data):
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'UNSUCCESS user login data validation'
        )

    transaction_status_outcome, user_id = db_service.authentificate_user(user_login_data)

    match transaction_status_outcome:
        case AuthentificationOutcome.LOGIN_SUCCESS:
            user_access_token = create_access_token(
                {
                    'user_id': user_id,
                    'email': user_login_data['email']
                }
            )

            user_page = request.url_for(
                'get_user_page',
                user_id = user_id
            )

            redirect_response = RedirectResponse(
                url = user_page,
                status_code = status.HTTP_303_SEE_OTHER
            )

            redirect_response.set_cookie(
                key = 'access_token',
                value = user_access_token,
                httponly = True,
                samesite = 'lax'
            )

            return redirect_response
        
        case AuthentificationOutcome.LOGIN_DB_ERROR:
            return JSONResponse(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                content = {'status': 'error', 'message': 'internal server db error'}
            )

        case AuthentificationOutcome.LOGIN_DB_UNAVAILABLE:
            return JSONResponse(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                content = {'status': 'error', 'message': 'db is unavailable'}
            )

        case AuthentificationOutcome.LOGIN_AUTH_ERROR:
            return JSONResponse(
                status_code = status.HTTP_401_UNAUTHORIZED,
                content = {'status': 'unauthorized', 'message': 'user is unauthorized'}
            )

        case AuthentificationOutcome.LOGIN_USER_INACTIVE:
            return JSONResponse(
                status_code = status.HTTP_403_FORBIDDEN,
                content = {'status': 'forbidden', 'message': 'User is inactive'}
            )

        case _:
            return JSONResponse(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                content = {'status': 'error', 'message': 'internal server error'}
            )

@router.get('/registration')
async def show_registration_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = 'registration_page.html'
    )

@router.post('/registration')
async def register_user(
    full_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    department: Annotated[str, Form()],
    password: Annotated[str, Form()],
    user_reg_validator: Annotated[UserRegValidator, Depends(get_user_reg_validator)],
    db_service: Annotated[DataBaseService, Depends(get_db_service)]
):
    user_reg_data = {
        'full_name' : full_name,
        'email' : email,
        'department' : department,
        'password' : password
    }
    if not user_reg_validator.validate_user_reg_data(user_reg_data):
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'UNSUCCESS user registration data validation'
        )

    transaction_status_outcome = db_service.registrate_new_user(user_reg_data)

    match transaction_status_outcome:
        case RegistrationOutcome.REGISTRATION_SUCCESS:
            return JSONResponse(
                status_code = status.HTTP_201_CREATED,
                content = {'status': 'success', 'message': 'User registered successfully'}
            )

        case RegistrationOutcome.REGISTRATION_EMAIL_TAKEN:
            return JSONResponse(
                status_code = status.HTTP_409_CONFLICT,
                content = {'status' : 'conflict', 'message' : f'User with email: {email} has already existed'}
            )

        case RegistrationOutcome.REGISTRATION_DB_ERROR:
            return JSONResponse(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                content = {'status': 'error', 'message': 'internal server error'}
            )

        case RegistrationOutcome.REGISTRATION_DB_UNAVAILABLE:
            return JSONResponse(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                content = {'status': 'error', 'message': 'DB is unavailable'}
            )

        case _:
            return JSONResponse(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                content = {'status': 'error', 'message': 'internal server error'}
            )

@router.get('/{user_id}')
async def get_user_page(
    request: Request,
    user_id: str,
    current_user: Annotated[ActiveUserModel, Depends(get_current_active_user)]
):
    if current_user.user_id != user_id:
        logger.warning('Access rejected: user page belongs to another user')
        raise HTTPException(
            status_code = status.HTTP_303_SEE_OTHER,
            detail = 'Forbidden',
            headers = {'Location': '/user/login'}
        )

    return templates.TemplateResponse(
        request = request,
        name = 'user_page.html',
        context = {'current_user': current_user}
    )

@router.post('/logout')
async def user_logout(
    response: Response
):
    response.delete_cookie(
        key = 'access_token',
        path = '/',
        httponly = True,
        samesite = 'lax'
    )

    logger.info('Logout completed: authentication cookie cleared')
    return {'message': 'logout'}

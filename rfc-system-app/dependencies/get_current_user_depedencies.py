from typing import Annotated
from loguru import logger
from fastapi import Request, Depends, HTTPException, status

from services import DataBaseService
from core import decode_access_token
from models import ActiveUserModel, User
from dependencies import get_db_service

def get_current_user(request: Request) -> User:
    token = request.cookies.get('access_token')

    if not token:
        raise HTTPException(
            status_code = status.HTTP_303_SEE_OTHER,
            detail = 'Unauthorized user',
            headers = {'Location': '/user/login'}
        )

    user_payload = decode_access_token(token)

    if user_payload is None:
        logger.error(f'AUTHORIZED ERROR: Invalid or expired token: {user_payload}')
        raise HTTPException(
            status_code = status.HTTP_303_SEE_OTHER,
            detail = 'Invalid or expired token',
            headers = {'Location': '/user/login'}
        )

    return User(
        user_id = user_payload['user_id'],
        email = user_payload['email']
    )

def get_current_active_user(
    current_user: Annotated[User | dict, Depends(get_current_user)],
    db_service: Annotated[DataBaseService, Depends(get_db_service)]
) -> ActiveUserModel:    
    is_active = db_service.check_user_is_active(current_user.user_id)

    if is_active is None:
        raise HTTPException(
            status_code = status.HTTP_303_SEE_OTHER,
            detail = 'Unable to verify user status',
            headers = {'Location': '/user/login'}
        )

    if not is_active:
        raise HTTPException(
            status_code = status.HTTP_303_SEE_OTHER,
            detail = 'User is not active',
            headers = {'Location': '/user/login'}
        )

    return ActiveUserModel(
        user_id = current_user.user_id,
        email = current_user.email,
        is_active = is_active
    )


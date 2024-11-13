from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session  # Сессия БД
from backend.db_depends import get_db  # Функция подключения к базе данных
from typing import Annotated  # Аннотации
from models import User, Task  # Модели БД
from schemas import CreateUser, UpdateUser  # Pydantic.
from sqlalchemy import insert, select, update, delete  # Функции работы с записями
from slugify import slugify  # Функция работы с записями


router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    s = db.scalars(select(User)).all()
    return s


@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).fetchall()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found"
        )
    else:
        return user


@router.get('/user_id/tasks')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    task_this_user = db.scalars(select(Task).where(Task.user_id == user_id)).fetchall()
    if not task_this_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tasks this user are not found"
        )
    else:
        return task_this_user


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    is_username_exists = db.scalars(select(User).where(User.username == create_user.username))
    is_user_exists = is_username_exists.fetchall()

    if is_user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username already exists.'
        )
    else:
        db.execute(insert(User).values(username=create_user.username,
                                       firstname=create_user.firstname,
                                       lastname=create_user.lastname,
                                       age=create_user.age,
                                       slug=slugify(create_user.username)))
        db.commit()
        return {
            "status_code": status.HTTP_201_CREATED,
            "transaction": 'Successful'
        }


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], update_user: UpdateUser, user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).fetchall()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found"
        )
    else:
        db.execute(update(User).where(User.id == user_id).values(
            firstname=update_user.firstname,
            lastname=update_user.lastname,
            age=update_user.age,
        ))
        db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            'transaction': 'User update is successful!'
        }


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).fetchall()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found"
        )
    else:
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Task).where(Task.user_id == user_id))
        db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            'transaction': 'User delete is successful!'
        }


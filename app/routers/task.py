from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session  # Сессия БД
from backend.db_depends import get_db  # Функция подключения к базе данных
from typing import Annotated  # Аннотации
from models import Task, User  # Модели БД
from schemas import CreateTask, UpdateTask  # Pydantic.
from sqlalchemy import insert, select, update, delete  # Функции работы с записями
from slugify import slugify  # Функция работы с записями


router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Task)).all()



@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id)).fetchall()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found"
        )
    else:
        return task


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], create_task: CreateTask, user_id: int):
    is_username_exists = db.scalars(select(User).where(User.id == user_id))
    is_user_exists = is_username_exists.fetchall()

    if is_user_exists:
        db.execute(insert(Task).values(title=create_task.title,
                                       content=create_task.content,
                                       priority=create_task.priority,
                                       user_id=user_id,
                                       slug=slugify(create_task.title)))
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found.'
        )


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], update_task: UpdateTask, task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id)).fetchall()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found"
        )
    else:
        db.execute(update(Task).where(Task.id == task_id).values(
            title=update_task.title,
            content=update_task.content,
            priority=update_task.priority
        ))
        db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            'transaction': 'Task update is successful!'
        }


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id)).fetchall()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found"
        )
    else:
        db.execute(delete(Task).where(Task.id == task_id))
        db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            'transaction': 'Task delete is successful!'
        }

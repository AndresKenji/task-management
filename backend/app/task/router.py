import logging
from typing import Generator, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from task.schemas import TaskCreate, TaskShow, TaskUpdate
from task.models import Task
from task import exceptions
from database.database import Database, get_database
from auth.security import get_current_active_user, get_current_admin_user
from auth.models import User

database: Database = get_database()
logger: logging.Logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/task",
    tags=["Tasks"]
)

def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de base de datos"""
    database = get_database()
    return database.get_db()

@router.get("/", response_model=List[TaskShow], summary="Obtener tareas del usuario")
async def get_user_tasks(
    db: Session = Depends(database.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> List[TaskShow]:

    try:

        if current_user.is_admin:
            tasks = db.query(Task).offset(skip).limit(limit).all()
            logger.info(f"Admin {current_user.username} retrieved {len(tasks)} tasks")
        else:
            tasks = db.query(Task).filter(
                Task.user_id == current_user.id
            ).offset(skip).limit(limit).all()
            logger.info(f"User {current_user.username} retrieved {len(tasks)} personal tasks")

        return [TaskShow.model_validate(task) for task in tasks]

    except Exception as e:
        logger.error(f"Error retrieving tasks for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tasks"
        )

@router.get("/all", response_model=List[TaskShow], summary="Obtener todas las tareas (Admin)")
async def get_all_tasks(
    db: Session = Depends(database.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user)
) -> List[TaskShow]:

    try:

        tasks = db.query(Task).offset(skip).limit(limit).all()
        logger.info(f"Admin {current_user.username} retrieved all {len(tasks)} tasks")
        return [TaskShow.model_validate(task) for task in tasks]

    except Exception as e:
        logger.error(f"Error retrieving all tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving all tasks"
        )

@router.get("/{task_id}", response_model=TaskShow, summary="Obtener tarea específica")
async def get_task_by_id(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskShow:

    try:

        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own tasks"
            )

        logger.info(f"User {current_user.username} retrieved task {task_id}")
        return TaskShow.model_validate(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving task"
        )

@router.post("/", response_model=TaskShow, summary="Crear nueva tarea")
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskShow:

    try:

        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=current_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            done=False
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        logger.info(f"User {current_user.username} created task: {new_task.title}")
        return TaskShow.model_validate(new_task)

    except SQLAlchemyError as e:
        logger.error(f"Database error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task"
        )
    except Exception as e:
        logger.error(f"Error creating task for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task"
        )


@router.put("/{task_id}", response_model=TaskShow, summary="Actualizar tarea")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskShow:

    try:

        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only update your own tasks"
            )

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.done is not None:
            task.done = task_data.done

        task.updated_at = datetime.now()

        db.commit()
        db.refresh(task)

        logger.info(f"User {current_user.username} updated task {task_id}")
        return TaskShow.model_validate(task)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task"
        )
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task"
        )

@router.patch("/{task_id}/toggle", response_model=TaskShow, summary="Marcar/Desmarcar tarea como completada")
async def toggle_task_completion(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskShow:

    try:

        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only modify your own tasks"
            )

        task.done = not task.done
        task.updated_at = datetime.now()

        db.commit()
        db.refresh(task)

        status_text = "completed" if task.done else "uncompleted"
        logger.info(f"User {current_user.username} marked task {task_id} as {status_text}")

        return TaskShow.model_validate(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task status"
        )

@router.patch("/{task_id}/complete", response_model=TaskShow, summary="Marcar tarea como completada")
async def complete_task(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskShow:

    try:

        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only modify your own tasks"
            )

        task.done = True
        task.updated_at = datetime.now()

        db.commit()
        db.refresh(task)

        logger.info(f"User {current_user.username} completed task {task_id}")
        return TaskShow.model_validate(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error completing task"
        )


@router.delete("/{task_id}", summary="Eliminar tarea")
async def delete_task(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_active_user)
):

    try:

        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )


        if task.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only delete your own tasks"
            )

        task_title = task.title
        db.delete(task)
        db.commit()

        logger.info(f"User {current_user.username} deleted task: {task_title}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task"
        )
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task"
        )


@router.get("/stats/summary", summary="Estadísticas de tareas del usuario")
async def get_task_stats(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_active_user)
):

    try:

        if current_user.is_admin:
            # Stats globales para admins
            total_tasks = db.query(Task).count()
            completed_tasks = db.query(Task).filter(Task.done == True).count()
            pending_tasks = total_tasks - completed_tasks

            stats = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "scope": "global"
            }
        else:
            # Stats personales para usuarios
            user_tasks = db.query(Task).filter(Task.user_id == current_user.id)
            total_tasks = user_tasks.count()
            completed_tasks = user_tasks.filter(Task.done == True).count()
            pending_tasks = total_tasks - completed_tasks

            stats = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "scope": "personal"
            }

        logger.info(f"User {current_user.username} retrieved task statistics")
        return stats

    except Exception as e:
        logger.error(f"Error retrieving task stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving task statistics"
        )
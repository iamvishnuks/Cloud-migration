from model.project import Project
from model.mapping import Mapper
from model.user import User
from schemas.project import ProjectBase, ProjectUpdate
from datetime import datetime
import json
from typing import Union
from fastapi.responses import JSONResponse
from sqlalchemy import Column
from sqlalchemy.orm import Session


def check_project_exists(user: str, project: str, db: Session) -> bool:
    '''
    Returns if a project with the given name exists in the current database session for the active user.
    
    :param user: active user
    :param project: project name to check
    :param db: active database session
    '''

    return(db.query(Mapper).join(Project).join(User).filter(User.username==user, Project.name==project, Mapper.is_deleted==False).count() > 0)


def create_project(id: str, data: ProjectBase, db: Session) -> JSONResponse:
    '''
    Create a new project with the given details.
    
    :param data: new project details
    :param db: active database session
    '''

    stmt = Project(
        id = id,
        name = data.name,
        provider = data.provider,
        location = data.location,
        aws_access_key = data.aws_access_key,
        aws_secret_key = data.aws_secret_key,
        azure_client_id	= data.azure_client_id,
        azure_client_secret	= data.azure_client_secret,
        azure_tenant_id	= data.azure_tenant_id,
        azure_subscription_id = data.azure_subscription_id,
        azure_resource_group = data.azure_resource_group,
        gcp_service_token = json.dumps(data.gcp_service_token),
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "project created", "data": [{}]})


def get_all_projects(user: str, db: Session) -> list:
    '''
    Returns all active projects associated with the active user.
    
    :param user: active user
    :param db: active database session
    '''

    return(db.query(Project).join(Mapper).join(User).filter(User.username==user, Mapper.is_deleted==False).all())


def get_projectid(user: str, project: str, db: Session) -> Column[str]:
    '''
    Returns the id for the specified active project associated with the active user.
    
    :param user: active user
    :param project: project name to retrieve the id from
    :param db: active database session
    '''

    return(db.query(Project).join(Mapper).join(User).filter(User.username==user, Project.name==project, Mapper.is_deleted==False).first().id)


def get_project_by_id(project_id: str, db: Session) -> Project:
    '''
    Returns the specified active project associated with the active user.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''
    
    return(db.query(Project).filter(Project.id==project_id).first())


def get_project_by_name(user: str, project: str, db: Session) -> Union[Project, None]:
    '''
    Returns the specified active project associated with the active user.
    
    :param user: active user
    :param project: project name to check
    :param db: active database session
    '''

    return(db.query(Project).join(Mapper).join(User).filter(User.username==user, Project.name==project, Mapper.is_deleted==False).first())


def update_project(data: ProjectUpdate, db: Session) -> JSONResponse:
    '''
    Updates given project with corresponding data.
    
    :param data: details to update the project with
    :param db: active database session
    '''

    db_project = get_project_by_id(data.id, db)
    project_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in project_data.items():
        if isinstance(value, dict):
            value = json.dumps(value)
        setattr(db_project, key, value)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return JSONResponse({"status": 204, "message": "project updated", "data": [{}]}, status_code=204)
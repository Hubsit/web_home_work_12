from typing import List

from fastapi import Depends, HTTPException, Path, status, APIRouter, Query
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas import ContactResponse, ContactModel
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(limit: int = Query(10, le=100), offset: int = 0,
                       current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(limit, offset, current_user, db)
    return contacts


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactModel, current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_by_email(body.email, current_user, db)
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email is exists')
    contact = await repository_contacts.create_contact(body, current_user, db)
    return contact


@router.get('/birthday', response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contact_7_days_birthday(current_user: User = Depends(auth_service.get_current_user),
                                         db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_birthday(current_user, db)
    if len(contacts) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.put('/{contact_id}', response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1),
                         current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.update(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def remove_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    contact = await repository_contacts.remove(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.get('/search/{contact_email}', response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contact_by_email(contact_email: str, current_user: User = Depends(auth_service.get_current_user),
                                  db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_by_email(contact_email, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.get('/search/first_name/{contact_first_name}', response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contact_by_first_name(contact_first_name: str,
                                       current_user: User = Depends(auth_service.get_current_user),
                                       db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contact_by_first_name(contact_first_name, current_user, db)
    if len(contacts) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.get('/search/last_name/{contact_last_name}', response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contact_by_first_name(contact_last_name: str,
                                       current_user: User = Depends(auth_service.get_current_user),
                                       db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contact_by_last_name(contact_last_name, current_user, db)
    if len(contacts) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models import ContactMessage, User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.contact.schemas import (
    ContactMessageResponse,
    CreateContactMessageRequest,
)
from app.modules.contact.service import create_message as create_contact_message


router = APIRouter(prefix="/contact-messages", tags=["Contacto"])


@router.post(
    "",
    response_model=ContactMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    data: CreateContactMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ContactMessage:
    return create_contact_message(db, user, data)

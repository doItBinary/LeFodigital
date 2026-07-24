from sqlalchemy.orm import Session

from app.db.models import ContactMessage, User
from app.modules.contact.schemas import CreateContactMessageRequest


def create_message(
    db: Session,
    user: User,
    data: CreateContactMessageRequest,
) -> ContactMessage:
    message = ContactMessage(
        subject=data.subject.strip(),
        message=data.message.strip(),
        sender_id=user.id,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

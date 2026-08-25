from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models import Tenant, User
from app.schemas import RegisterRequest


class EmailAlreadyRegisteredError(Exception):
    pass


def register_user(db: Session, data: RegisterRequest) -> User:
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user is not None:
        raise EmailAlreadyRegisteredError(data.email)

    tenant = Tenant(name=data.tenant_name)
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

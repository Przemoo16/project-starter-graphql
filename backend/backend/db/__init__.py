# Import the models, so that they can be registered in Base.metadata
# and therefore detected by the Alembic
from backend.models.user import User

from .base import Base

__all__ = ["Base", "User"]

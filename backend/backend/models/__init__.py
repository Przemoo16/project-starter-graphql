# Import the models, so that they can be registered in Base.metadata
# and therefore detected by the Alembic
from .base import Base
from .user import User

__all__ = ["Base", "User"]

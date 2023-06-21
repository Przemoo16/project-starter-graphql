# Import the models, so that they can be registered in Base.metadata
# and therefore detected by the Alembic
from backend.libs.db.model import Base
from backend.services.user.models import User

__all__ = ["Base", "User"]

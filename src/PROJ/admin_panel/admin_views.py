from sqladmin import Admin, ModelView

from src.PROJ.db.models_jobs import Jobs, HR
from src.PROJ.users.user_models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email]
    column_details_exclude_list = [User.hashed_password]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class JobsAdmin(ModelView, model=Jobs):
    column_list = [c.name for c in Jobs.__table__.c]
    can_delete = True
    name = "Jobs"
    icon = "fa-solid fa-user"